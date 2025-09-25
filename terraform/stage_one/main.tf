# STAGE 1 - No dependencies for creation

provider "aws" {
  region = var.REGION
  access_key = var.ACCESS_KEY
  secret_key = var.SECRET_ACCESS_KEY
}

# S3 Bucket

resource "aws_s3_bucket" "c19-cran-bucket" {
    bucket = var.S3_NAME
    force_destroy = false   
}

resource "aws_s3_bucket_versioning" "c19-cran-s3-disable-versioning" {
  bucket = aws_s3_bucket.c19-cran-bucket.id
  versioning_configuration {
    status = "Disabled"
  }
}

# ECR's

resource "aws_ecr_repository" "c19-cran-pipeline" {
  name                 = "c19-cran-pipeline"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "c19-cran-summarise" {
  name                 = "c19-cran-summarise"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

# resource "aws_ecr_repository" "c19-cran-dashboard" {
#   name                 = "c19-cran-dashboard"
#   image_tag_mutability = "MUTABLE"

#   image_scanning_configuration {
#     scan_on_push = true
#   }
# }


# GLUE DB & GLUE CRAWLER

resource "aws_iam_role" "c19-cran-glue-role" {
  name = "c19-cran-glue-service-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "glue.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "c19-cran-glue-service-role" {
    role = aws_iam_role.c19-cran-glue-role.id
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy" "my_s3_policy" {
  name = "my_s3_policy"
  role = aws_iam_role.c19-cran-glue-role.id
  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*"
      ],
      "Resource": [
        "arn:aws:s3:::c19-cran-bucket",
        "arn:aws:s3:::c19-cran-bucket/*"
      ]
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "glue_service_s3" {
 name = "glue_service_s3"
    role = aws_iam_role.c19-cran-glue-role.id
    policy = "${aws_iam_role_policy.my_s3_policy.policy}"
}

resource "aws_glue_catalog_database" "c19-cran-plants-db" {
  name = "c19-cran-plants-db"
}

resource "aws_glue_crawler" "c19-cran-crawler" {
  database_name = aws_glue_catalog_database.c19-cran-plants-db.name
  name          = "c19-cran-crawler"
  role          = aws_iam_role.c19-cran-glue-role.arn

  s3_target {
    path = "s3://${aws_s3_bucket.c19-cran-bucket.bucket}/summary/"
  }
  schedule = "cron(1 9 * * ? *)"
}