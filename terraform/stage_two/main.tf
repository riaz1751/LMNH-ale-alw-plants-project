
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
#       name = "c19-cran-plants-dashboard",
#       image ="",
#       essential = true,
#       portMappings = [
#         {
#           containerPort = 8501
#           hostPort      = 8501
#           protocol      = "tcp"
#         }
#       ],
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
#         },
#         {
#           name = "DB_DRIVER",
#           value = var.DB_DRIVER
#         }
#       ]
#     }
#   ]
#   )
#   runtime_platform {
#     operating_system_family = "LINUX"
#     cpu_architecture        = "X86_64"
#   }
# }

resource "aws_iam_role" "c19_cran_ecs_service_role" {
  name = "c19-cran_ecs_service_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "c19_cran_ecs_athena" {
  role       = aws_iam_role.c19_cran_ecs_service_role.id
  policy_arn = "arn:aws:iam::aws:policy/AmazonAthenaFullAccess"
}

resource "aws_iam_role_policy_attachment" "c19_cran_ecs_rds" {
  role       = aws_iam_role.c19_cran_ecs_service_role.id
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
}

resource "aws_security_group" "c19_cran_sg" {
  name        = "c19_cran_sg"
  description = "Allow access to streamlit dashboard"
  vpc_id      = "vpc-0f29b6a6ab918bcd5"

  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# resource "aws_ecs_service" "c19_cran_service" {
#   name            = "c19_cran_service"
#   cluster         = "arn:aws:ecs:eu-west-2:129033205317:cluster/c19-ecs-cluster"
#   task_definition = aws_ecs_task_definition.c19-cran-plants-dashboard
#   desired_count   = "1"
#   network_configuration {
#     subnets          = ["subnet-00506a8db091bdf2a", "subnet-0425a4a0b929ea507", "subnet-0e7a1e60734c4fca7"]
#     security_groups  = [aws_security_group.c19_cran_sg]
#     assign_public_ip = true
#   }
# }