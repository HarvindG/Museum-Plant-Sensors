terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}

provider "aws" {
  region  = "eu-west-2"
}

data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}

resource "aws_ecs_task_definition" "c9-ladybirds-pipeline-task" {
  family                   = "c9-ladybirds-pipeline-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = "${data.aws_iam_role.ecs_task_execution_role.arn}"
  container_definitions    = <<TASK_DEFINITION
[
  {
    "environment": [
      {"name": "DB_HOST", "value": "${var.database_ip}"},
      {"name": "DB_NAME", "value": "${var.database_name}"},
      {"name": "DB_PASSWORD", "value": "${var.database_password}"},
      {"name": "DB_PORT", "value": "${var.database_port}"},
      {"name": "DB_USERNAME", "value": "${var.database_username}"}
    ],
    "name": "c9-ladybirds-pipeline",
    "image": "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c9-ladybirds-pipeline:latest",
    "essential": true
  }
]
TASK_DEFINITION

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
}

resource "aws_ecs_service" "c9-ladybirds-pipeline" {
  name            = "c9-ladybirds-pipeline"
  cluster         = "c9-ecs-cluster"
  task_definition = aws_ecs_task_definition.c9-ladybirds-pipeline-task.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  force_new_deployment = true 
  depends_on = [aws_ecs_task_definition.c9-ladybirds-pipeline-task]

network_configuration {
    security_groups = ["sg-020697b6514174b72"]
    subnets         = ["subnet-0d0b16e76e68cf51b","subnet-081c7c419697dec52","subnet-02a00c7be52b00368"]
    assign_public_ip = true
  }
}



resource "aws_ecs_task_definition" "c9-ladybirds-load-old-data-task" {
  family                   = "c9-ladybirds-load-old-data-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = "${data.aws_iam_role.ecs_task_execution_role.arn}"
  container_definitions    = <<TASK_DEFINITION
[
  {
    "environment": [
      {"name": "DB_HOST", "value": "${var.database_ip}"},
      {"name": "DB_NAME", "value": "${var.database_name}"},
      {"name": "DB_PASSWORD", "value": "${var.database_password}"},
      {"name": "DB_PORT", "value": "${var.database_port}"},
      {"name": "DB_USERNAME", "value": "${var.database_username}"},
      {"name": "AWS_ACCESS_KEY_ID", "value": "${var.aws_access_key_id}"},
      {"name": "AWS_SECRET_ACCESS_KEY", "value": "${var.aws_secret_access_key}"}
    ],
    "name": "c9-ladybirds-load-old-data",
    "image": "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c9-ladybirds-load-old-data:latest",
    "essential": true
  }
]
TASK_DEFINITION

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
}


# Create a resource that allows running ecs tasks
resource "aws_iam_policy" "ecs-schedule-permissions" {
    name = "ExecuteECSFunctions"
    policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecs:RunTask"
            ],
            "Resource": [
                aws_ecs_task_definition.c9-ladybirds-load-old-data-task.arn
            ],
            "Condition": {
                "ArnLike": {
                    "ecs:cluster": "arn:aws:ecs:eu-west-2:129033205317:cluster/c9-ecs-cluster"
                }
            }
        },
        {
            "Effect": "Allow",
            "Action": "iam:PassRole",
            "Resource": [
                "*"
            ],
            "Condition": {
                "StringLike": {
                    "iam:PassedToService": "ecs-tasks.amazonaws.com"
                }
            }
        }
    ]
})
}


resource "aws_iam_role" "iam_for_ecs" {
  name = "ECSPermissionsForIAM-73sfa"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    },
    {
      "Effect": "Allow",
      "Principal": {
          "Service": "scheduler.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
      }
    ]
}
EOF
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "attach-ecs-policy" {
  role       = aws_iam_role.iam_for_ecs.name
  policy_arn = aws_iam_policy.ecs-schedule-permissions.arn
}



resource "aws_scheduler_schedule" "c9-ladybirds-load-old-data" {
  name        = "c9-ladybirds-load-old-data"
  group_name  = "default"

  flexible_time_window {
    maximum_window_in_minutes = 15
    mode = "FLEXIBLE"
  }
  schedule_expression_timezone = "Europe/London"
  schedule_expression = "cron(05 09 * * ? *)" 

  target {
    arn      = "arn:aws:ecs:eu-west-2:129033205317:cluster/c9-ecs-cluster" # arn of the ecs cluster to run on
    # role that allows scheduler to start the task (explained later)
    role_arn = aws_iam_role.iam_for_ecs.arn

    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.c9-ladybirds-load-old-data-task.arn
      launch_type         = "FARGATE"

    network_configuration {
        subnets         = ["subnet-0d0b16e76e68cf51b","subnet-081c7c419697dec52","subnet-02a00c7be52b00368"]
        assign_public_ip = true
      }
    }
  }
}


resource "aws_security_group" "c9_ladybirds_dashboard_sg" {
  name        = "c9_ladybirds_dashboard_sg"
  description = "Allow TLS inbound traffic"
  vpc_id      = "vpc-04423dbb18410aece"

  ingress {
    description      = "TLS from VPC"
    from_port        = 4321
    to_port          = 4321
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"] 
  }
  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name = "c9_ladybirds_dashboard_sg"
  }
}



resource "aws_ecs_task_definition" "c9-ladybirds-dashboard-task" {
  family                   = "c9-ladybirds-dashboard-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = "${data.aws_iam_role.ecs_task_execution_role.arn}"
  container_definitions    = <<TASK_DEFINITION
[
  {
    "environment": [
      {"name": "DB_HOST", "value": "${var.database_ip}"},
      {"name": "DB_PASSWORD", "value": "${var.database_password}"},
      {"name": "DB_PORT", "value": "${var.database_port}"},
      {"name": "DB_USERNAME", "value": "${var.database_username}"},
      {"name": "AWS_ACCESS_KEY_ID", "value": "${var.aws_access_key_id}"},
      {"name": "AWS_SECRET_ACCESS_KEY", "value": "${var.aws_secret_access_key}"}
    ],
    "name": "c9-ladybirds-dashboard",
    "image": "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c9-ladybirds-dashboard:latest",
    "essential": true,
    "portMappings" : [
        {
          "containerPort" : 4321,
          "hostPort"      : 4321
        }
      ]
  }
]
TASK_DEFINITION

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
}

resource "aws_ecs_service" "c9-ladybirds-dashboard" {
  name            = "c9-ladybirds-dashboard"
  cluster         = "c9-ecs-cluster"
  task_definition = aws_ecs_task_definition.c9-ladybirds-dashboard-task.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  force_new_deployment = true 
  depends_on = [aws_ecs_task_definition.c9-ladybirds-dashboard-task]

network_configuration {
    security_groups = [aws_security_group.c9_ladybirds_dashboard_sg.id]
    subnets         = ["subnet-0d0b16e76e68cf51b","subnet-081c7c419697dec52","subnet-02a00c7be52b00368"]
    assign_public_ip = true
  }
}