"""
Script para lanzar un SageMaker Training Job.
Lee datos procesados de S3 y guarda el modelo entrenado en S3.

Uso:
    python scripts/launch_training_job.py \
        --image <ecr-uri>:train-latest \
        --role <sagemaker-execution-role-arn> \
        --input-s3 s3://bucket/path/to/processed/ \
        --output-s3 s3://bucket/path/to/models/
"""
import argparse
import datetime
import logging
import sys
import time

import boto3

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

REGION = "us-east-1"


def parse_args():
    p = argparse.ArgumentParser(description="Launch SageMaker Training Job")
    p.add_argument("--image", required=True, help="ECR image URI (train stage)")
    p.add_argument("--role", required=True, help="SageMaker execution IAM role ARN")
    p.add_argument(
        "--input-s3", required=True,
        help="S3 URI prefix of the processed dataset"
    )
    p.add_argument(
        "--output-s3", required=True,
        help="S3 URI prefix where trained model artifacts will be saved"
    )
    p.add_argument(
        "--instance-type", default="ml.m5.large",
        help="SageMaker instance type (default: ml.m5.large)"
    )
    p.add_argument(
        "--max-runtime", type=int, default=3600,
        help="Max training runtime in seconds (default: 3600)"
    )
    p.add_argument(
        "--wait", action="store_true", default=True,
        help="Wait for job to complete (default: True)"
    )
    return p.parse_args()


def launch_training_job(args):
    sm = boto3.client("sagemaker", region_name=REGION)

    ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    job_name = f"titanic-training-{ts}"

    log.info("Launching SageMaker Training Job: %s", job_name)
    log.info("  Image      : %s", args.image)
    log.info("  Role       : %s", args.role)
    log.info("  Input  (S3): %s", args.input_s3)
    log.info("  Output (S3): %s", args.output_s3)
    log.info("  Instance   : %s", args.instance_type)
    log.info("  Max Runtime: %s s", args.max_runtime)

    sm.create_training_job(
        TrainingJobName=job_name,
        AlgorithmSpecification={
            "TrainingImage": args.image,
            "TrainingInputMode": "File",
        },
        RoleArn=args.role,
        InputDataConfig=[
            {
                "ChannelName": "train",
                "DataSource": {
                    "S3DataSource": {
                        "S3DataType": "S3Prefix",
                        "S3Uri": args.input_s3,
                        "S3DataDistributionType": "FullyReplicated",
                    }
                },
                "ContentType": "text/csv",
                "InputMode": "File",
            }
        ],
        OutputDataConfig={
            "S3OutputPath": args.output_s3,
        },
        ResourceConfig={
            "InstanceCount": 1,
            "InstanceType": args.instance_type,
            "VolumeSizeInGB": 10,
        },
        StoppingCondition={
            "MaxRuntimeInSeconds": args.max_runtime,
        },
        Tags=[
            {"Key": "Project", "Value": "practica-ci-cd"},
            {"Key": "ManagedBy", "Value": "github-actions"},
        ],
    )

    log.info("Job submitted: %s", job_name)
    print(f"::set-output name=training_job_name::{job_name}")  # GitHub Actions output

    if not args.wait:
        return job_name

    # Esperar a que termine
    log.info("Waiting for training job to complete …")
    while True:
        response = sm.describe_training_job(TrainingJobName=job_name)
        status = response["TrainingJobStatus"]
        log.info("  Status: %s", status)

        if status == "Completed":
            log.info("✅ Training Job completed successfully.")
            model_artifact = response.get("ModelArtifacts", {}).get(
                "S3ModelArtifacts", "N/A"
            )
            log.info("  Model artifact: %s", model_artifact)
            return job_name
        elif status in ("Failed", "Stopped"):
            reason = response.get("FailureReason", "unknown")
            log.error("❌ Training Job %s: %s", status, reason)
            sys.exit(1)

        time.sleep(30)


if __name__ == "__main__":
    args = parse_args()
    launch_training_job(args)
