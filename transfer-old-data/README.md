# Transfer Old Data

This folder contains all the code and resources used for transferring old data.

# 📝 Project Description

 - A script was created to transfer all data from an RDS to a CSV file in an S3 bucket, which when uploaded to the cloud, is ran everyday at 9am.
- This ensures that only one days worth of data is stored in the RDS, with the rest of the data being stored in a CSV file in an S3 bucket, which is our long term storage solution for archived data.

## 🛠️ Getting Setup
- Install requirements using `pip3 install -r requirements.txt`
- Install boto3 type hints by running `python -m pip install 'boto3-stubs[essential]'`
- Create a `.env` file with the following information:
    - `AWS_ACCESS_KEY_ID `= xxxxxxxxxx
    - `AWS_SECRET_ACCESS_KEY` = xxxxxxxx
    - `DB_USERNAME` = xxxxxxxx
    - `DB_PASSWORD` = xxxxxxxx
    - `DB_HOST` = xxxxxxxxx
    - `DB_PORT` = xxxxxxxx

## 🗂️ Files Explained
- `transfer_old_data.py`
    - A script to extract all data from an RDS and load it onto a CSV file contained within an S3 bucket. After this, the script removes all the data from the RDS.
- `test_transfer_old_data.py`
    - A script containing unit tests for the `transfer_old_data.py` script
- `Dockerfile`
    - A file which is used to build a Docker image of the `transfer_old_data.py` program
    - To build this image, run the command `docker build -t <image-name> .`
    - To run the container, run the command `docker run --env-file .env <image-name>`
