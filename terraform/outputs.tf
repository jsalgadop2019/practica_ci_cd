output "ecr_repository_url" {
  description = "URL completa del repositorio ECR (úsala en el workflow de GitHub Actions)"
  value       = aws_ecr_repository.ml_repo.repository_url
}

output "ecr_repository_arn" {
  description = "ARN del repositorio ECR"
  value       = aws_ecr_repository.ml_repo.arn
}

output "aws_region" {
  description = "Región de AWS utilizada"
  value       = var.aws_region
}

output "iam_user_name" {
  description = "Nombre del usuario IAM creado para GitHub Actions"
  value       = aws_iam_user.github_actions.name
}

output "aws_access_key_id" {
  description = "Access Key ID → guárdalo como secreto AWS_ACCESS_KEY_ID en GitHub"
  value       = aws_iam_access_key.github_actions.id
}

output "aws_secret_access_key" {
  description = "Secret Access Key → guárdalo como secreto AWS_SECRET_ACCESS_KEY en GitHub"
  value       = aws_iam_access_key.github_actions.secret
  sensitive   = true
}

output "s3_bucket_name" {
  description = "Nombre del bucket S3 de datos"
  value       = aws_s3_bucket.ml_data_bucket.bucket
}
