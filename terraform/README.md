# Terraform
This folder should contain all code and resources required to handle the infrastructure of the project.

# 📝 Project Description
- This folder contains all the terraform code and details that are needed to setup the cloud services required in our project.

## :hammer_and_wrench: Getting Setup

`.tfvars` keys used:

- `database_username`
- `database_password`
- `database_ip`
- `database_port`
- `database_name`
- `aws_access_key_id`
- `aws_secret_access_key`

## 🏃 Running the script

Run the terraform with `terraform init` and then `terraform apply`.
Remove the terraform with `terraform destroy`

## :card_index_dividers: Files Explained
- `main.tf`
    - A terraform script to create all resources and services needed within the project. These services include:
      - `pipeline Task Definition`
        - Task definition to run the pipeline container found in AWS ECR.
      - `AWS pipeline ECS Service`
         - ECS Service that constantly runs the pipeline task to keep loading data into our database.
      - `load old data Task Definition`
         - Task definition to run the load old data container found in AWS ECR.
      - `EventBridge Scheduler`
         - EventBridge Scheduler that runs every 24 hours at 9:05 extracting the previous days data and uploading it to our     long term storage.
      - `dashboard Security Group`
         - Security Group setup for the dashboard to allow access on port 4321.
      - `dashboard Task Definition`
         - Task definition to run the dashboard container found in AWS ECR.
      - `AWS dashboard ECS Service`
         - ECS Service that runs the dashboard task constantly and makes it publicly available on the cloud.
