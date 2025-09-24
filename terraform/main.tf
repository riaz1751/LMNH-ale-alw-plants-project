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
  name = "AWSGlueServiceRoleDefault"
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
        "arn:aws:s3:::my_bucket",
        "arn:aws:s3:::my_bucket/*"
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
    path = "s3://${aws_s3_bucket.c19-cran-bucket.bucket}"
  }
}

# Lambda Function

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "c19-cran-lambda-role" {
  name               = "c19-cran-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# resource "aws_lambda_function" "c19-cran-plants-summarise-lambda" {
#   function_name = "c19-cran-plants-summarise"
#   role          = "arn:aws:iam::129033205317:role/c19-cran-lambda-role"
#   package_type  = "Image"
#   image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c19-cran-summarise:latest"

#   environment {
#     variables = {
#       ACCESS_KEY = var.ACCESS_KEY,
#       SECRET_ACCESS_KEY = var.SECRET_ACCESS_KEY
#     }
#   }

#   memory_size = 512
#   timeout     = 30
# }

# IAM ROLE FOR TASK EXECUTION

resource "aws_iam_role" "c19-cran-task-execution-role" {
  name = "c19-cran-task-execution-role"
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ecs-tasks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
})
}

resource "aws_iam_role_policy_attachment" "c19-cran-task-execution-policy" {
  role= aws_iam_role.c19-cran-task-execution-role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# PIPELINE ECS TASK DEFINITION
resource "aws_ecs_task_definition" "c19-cran-plants-pipeline" {
  family = "c19-cran-plants-pipeline"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu = 1024
  memory                   = 3072
  execution_role_arn = aws_iam_role.c19-cran-task-execution-role.arn
  container_definitions = jsonencode([
    {
      name = "my_pipeline",
      image ="129033205317.dkr.ecr.eu-west-2.amazonaws.com/c19-cran-pipeline:latest",
      essential = true,
      logConfiguration = {
                logDriver = "awslogs"
                "options": {
                    awslogs-group = "/ecs/c19-cran-plants-pipeline"
                    awslogs-stream-prefix = "ecs"
                    awslogs-create-group = "true"
                    awslogs-stream-prefix = "ecs"
                    awslogs-region = "eu-west-2"
                }
            }
      environment= [
        {
          name = "ACCESS_KEY",
          value= var.ACCESS_KEY
        },
        {
          name = "SECRET_ACCESS_KEY",
          value= var.SECRET_ACCESS_KEY
        },
        {
          name = "DB_HOST",
          value = var.DB_HOST
        },
        {
          name = "DB_PORT",
          value = var.DB_PORT
        },
        {
          name = "DB_NAME",
          value = var.DB_NAME
        },
        {
          name = "DB_USERNAME",
          value = var.DB_USERNAME
        },
        {
          name = "DB_PASSWORD",
          value = var.DB_PASSWORD
        },
        {
          name = "DB_DRIVER",
          value = var.DB_DRIVER
        }
      ]
    }
  ]
  )
}

# DASHBOARD ECS TASK DEFINITION
# resource "aws_ecs_task_definition" "c19-cran-plants-dashboard" {
#   family = "c19-cran-plants-dashboard"
#   requires_compatibilities = ["FARGATE"]
#   network_mode             = "awsvpc"
#   cpu = 1024
#   memory                   = 3072
#   execution_role_arn = aws_iam_role.c19-cran-task-execution-role.arn
#   container_definitions = jsonencode([
#     {
#       name = "my_pipeline",
#       image ="129033205317.dkr.ecr.eu-west-2.amazonaws.com/c19-cran-plants-dashboard:latest",
#       essential = true,
#       logConfiguration = {
#                 logDriver = "awslogs"
#                 "options": {
#                     awslogs-group = "/ecs/c19-cran-plants-dashboard"
#                     awslogs-stream-prefix = "ecs"
#                     awslogs-create-group = "true"
#                     awslogs-stream-prefix = "ecs"
#                     awslogs-region = "eu-west-2"
#                 }
#             }
#       environment= [
#         {
#           name = "AWS_ACCESS_KEY",
#           value= var.ACCESS_KEY
#         },
#         {
#           name = "AWS_SECRET_ACCESS_KEY",
#           value= var.SECRET_ACCESS_KEY
#         },
#         {
#           name = "DB_HOST",
#           value = var.DB_HOST
#         },
#         {
#           name = "DB_PORT",
#           value = var.DB_PORT
#         },
#         {
#           name = "DB_NAME",
#           value = var.DB_NAME
#         },
#         {
#           name = "DB_USERNAME",
#           value = var.DB_USERNAME
#         },
#         {
#           name = "DB_PASSWORD",
#           value = var.DB_PASSWORD
#         },
#         {
#           name = "S3_NAME",
#           value = var.S3_NAME
#         }
#       ]
#     }
#   ]
#   )
# }

# ECS SERVICE 

# resource "aws_ecs_service" "c19-cran-plants-pipeline" {
#   name                               = "${var.namespace}_ECS_Service_${var.environment}"
#   cluster                            = aws_ecs_cluster.default.id
#   task_definition                    = aws_ecs_task_definition.default.arn
#   desired_count                      = var.ecs_task_desired_count
#   launch_type                        = "FARGATE"

#   network_configuration {
#     security_groups  = [aws_security_group.ecs_container_instance.id]
#     subnets          = aws_subnet.private.*.id
#     assign_public_ip = false
#   }

#   lifecycle {
#     ignore_changes = [desired_count]
#   }
# }