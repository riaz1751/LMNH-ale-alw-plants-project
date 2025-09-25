
provider "aws" {
  region = var.REGION
  access_key = var.ACCESS_KEY
  secret_key = var.SECRET_ACCESS_KEY
}

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

resource "aws_lambda_function" "c19-cran-plants-summarise-lambda" {
  function_name = "c19-cran-plants-summarise"
  role          = "arn:aws:iam::129033205317:role/c19-cran-lambda-role"
  package_type  = "Image"
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c19-cran-summarise:latest"

  environment {
    variables = {
      ACCESS_KEY = var.ACCESS_KEY,
      SECRET_ACCESS_KEY = var.SECRET_ACCESS_KEY,
      DB_DRIVER = var.DB_DRIVER,
      S3_BUCKET = var.S3_NAME,
      REGION = var.REGION,
      DB_HOST = var.DB_HOST,
      DB_PORT = var.DB_PORT,
      DB_NAME = var.DB_NAME,
      DB_USERNAME = var.DB_USERNAME,
      DB_PASSWORD = var.DB_PASSWORD
    }
  }

  memory_size = 512
  timeout     = 30
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
