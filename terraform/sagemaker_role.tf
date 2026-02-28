# ─────────────────────────────────────────────
# IAM Role que SageMaker asume al correr jobs
# ─────────────────────────────────────────────

resource "aws_iam_role" "sagemaker_execution" {
  name = "sagemaker-execution-${var.ecr_repo_name}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "sagemaker.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = {
    Project   = "practica-ci-cd"
    ManagedBy = "terraform"
  }
}

# Acceso a S3 (leer raw, escribir processed)
resource "aws_iam_role_policy" "sagemaker_s3" {
  name = "sagemaker-s3-policy"
  role = aws_iam_role.sagemaker_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "S3ListBucket"
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::practica.mlops.2026"
        ]
      },
      {
        Sid    = "S3ReadWriteObjects"
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = [
          "arn:aws:s3:::practica.mlops.2026/*"
        ]
      }
    ]
  })
}

# Acceso a ECR (pull de la imagen de processing)
resource "aws_iam_role_policy" "sagemaker_ecr" {
  name = "sagemaker-ecr-policy"
  role = aws_iam_role.sagemaker_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "ECRAuth"
        Effect = "Allow"
        Action = ["ecr:GetAuthorizationToken"]
        Resource = "*"
      },
      {
        Sid    = "ECRPull"
        Effect = "Allow"
        Action = [
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchCheckLayerAvailability"
        ]
        Resource = aws_ecr_repository.ml_repo.arn
      }
    ]
  })
}

# Logs de CloudWatch para el Processing Job
resource "aws_iam_role_policy_attachment" "sagemaker_cloudwatch" {
  role       = aws_iam_role.sagemaker_execution.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

# ─────────────────────────────────────────────
# Permisos adicionales para el usuario IAM de
# GitHub Actions: lanzar y monitorear jobs
# ─────────────────────────────────────────────

resource "aws_iam_user_policy" "github_sagemaker" {
  name = "sagemaker-launch-policy"
  user = aws_iam_user.github_actions.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "SageMakerJobs"
        Effect = "Allow"
        Action = [
          "sagemaker:CreateProcessingJob",
          "sagemaker:DescribeProcessingJob",
          "sagemaker:StopProcessingJob",
          "sagemaker:ListProcessingJobs",
          "sagemaker:CreateTrainingJob",
          "sagemaker:DescribeTrainingJob",
          "sagemaker:StopTrainingJob",
          "sagemaker:ListTrainingJobs"
        ]
        Resource = "*"
      },
      {
        Sid      = "PassRoleToSageMaker"
        Effect   = "Allow"
        Action   = "iam:PassRole"
        Resource = aws_iam_role.sagemaker_execution.arn
      }
    ]
  })
}

output "sagemaker_execution_role_arn" {
  description = "ARN del IAM Role que SageMaker usará para ejecutar los jobs"
  value       = aws_iam_role.sagemaker_execution.arn
}
