terraform {
  required_version = ">= 1.3.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = "curso_mlops"
}

# ─────────────────────────────────────────────
# ECR Repository
# ─────────────────────────────────────────────

resource "aws_ecr_repository" "ml_repo" {
  name                 = var.ecr_repo_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = {
    Project     = "practica-ci-cd"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Elimina imágenes antiguas automáticamente (mantiene las últimas 10)
resource "aws_ecr_lifecycle_policy" "ml_repo_policy" {
  repository = aws_ecr_repository.ml_repo.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Mantener solo las últimas 10 imágenes"
        selection = {
          tagStatus   = "any"
          countType   = "imageCountMoreThan"
          countNumber = 10
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ─────────────────────────────────────────────
# S3 Data Bucket
# ─────────────────────────────────────────────

data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "ml_data_bucket" {
  bucket        = "practica-mlops-data-${data.aws_caller_identity.current.account_id}"
  force_destroy = true

  tags = {
    Project     = "practica-ci-cd"
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# ─────────────────────────────────────────────
# IAM User para GitHub Actions
# ─────────────────────────────────────────────

resource "aws_iam_user" "github_actions" {
  name = "github-actions-ecr-${var.ecr_repo_name}"

  tags = {
    Project   = "practica-ci-cd"
    ManagedBy = "terraform"
  }
}

resource "aws_iam_user_policy" "ecr_push" {
  name = "ecr-push-policy"
  user = aws_iam_user.github_actions.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowECRAuth"
        Effect = "Allow"
        Action = ["ecr:GetAuthorizationToken"]
        Resource = "*"
      },
      {
        Sid    = "AllowECRPush"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:BatchGetImage",
          "ecr:GetDownloadUrlForLayer"
        ]
        Resource = aws_ecr_repository.ml_repo.arn
      }
    ]
  })
}

resource "aws_iam_access_key" "github_actions" {
  user = aws_iam_user.github_actions.name
}
