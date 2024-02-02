# Museum-Plant-Sensors

## 📝 Project Description
The Liverpool Natural History Museum (LNHM) has opened a new botanical wing. This will feature exhibits that showcase a diversity of plants across different regions of the world. This is naturally difficult to maintain, so the museum has set up plant sensors which monitor the health of each plant. However, this is only configured with a single API endpoint, so the aim of the proejct is to help monitor a plants health overtime, store the historical data and create visualisations of the plants health for the gardeners. 

To do this, the team will:
- Create an ETL Pipeline for the plants sensors data.
- Create long term and short term storage solutions for data.
- Visualise data in real time and view data in long term storage.

Terraform:
This project contains a terraform folder that has the capability to to provision the infrastructure of the pipeline.

Dashboard:
This project contains a dashboard folder. This folder contains the code to run a Streamlit dashboard that can be hosted on AWS.
This dashboard allows us:
- To be able to view the data in real-time
- To view graphs of the latest temperature and moisture readings for every plant
- To be able to view the data from the long-term storage


## 🗂️ Repository Contents
- `dashboard` - contains all the code and resources required to run the dashboard
- `diagrams` - contains all the diagrams used in planning and designing our approach
- `pipeline` - contains all the code and resources required to run the pipeline
  - `database` - contains the code required to set up the database, as well as script to connect to and reset the database
- `terraform` - contains all the terraform code required to build the necessary AWS services for running the pipeline on the cloud
- `transfer-old-data` - contains all the code and resources required to transfer data from the RDS to a CSV file in an S3 bucket


## 🛠️ Setup

Follow the instructions provided in the `README.md` files located in each folder.


## 🏃 Running the pipeline locally

1. To get the pipeline running, navigate to the `pipeline` folder and follow the instructions provided in the `README.md` file
2. Once the pipeline is running, navigate to the `dashboard` folder and follow the `README.md` instructions to run the dashboard

## ☁️ Running the pipeline on the cloud

1. Create three ECR repositories, one for each of the following:
    - `pipeline`
    - `transfer-old-data`
    - `dashboard`
2. Navigate to the each of these folders, and follow the `push commands` provided in the ECR repository to build and upload the Docker images
3. To create the AWS infrastructure required for the pipeline to run on the cloud, navigate to the `terraform` folder and follow the instructions provided in the `README.md` file

## Credits
- Charlie Dean
- Harvind Grewal
- Zander Snow
- Shivani Patel
