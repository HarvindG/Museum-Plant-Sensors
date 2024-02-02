# Pipeline
This directory contains all code and resources required for the pipeline. The pipeline is broken down into three main stages - an extract stage, transform stage and load stage. Also included in the folder is a text file detailing requirements, a dockerfile and a database sub-directory that contains a .sql file that allows the creation of the database as required. 

# 📝 Project Description
- In order to be able to analyse data coming from sensors in the museum on each plant, data needs to be extracted from respective API endpoints for each plant at the museum. The extract script achieves this using a 'session' object created using the requests library.
- The data coming from the API is relatively clean but needs to be adjusted to allow it to be fit to the structure of the database that has been designed for storing data on each of the plants. This process of normalizing data and excluding faults is carried out by the transform script.
- Finally, data is loaded into the RDS database via the load script - where other services such as the dashboard and the service that loads the archive database are able to extract data.
- The pipeline has also incorporated functionality that creates a log of every run of the pipeline and the timestamp - as well as runtime - associated with each phase of the pipeline

## :hammer_and_wrench: Getting Setup

1. `pip install -r requirements.txt` - command to install all necessary requirements to working directory
2. `.env` keys used:
    - `DB_HOST`
    - `DB_PORT`
    - `DB_USERNAME`
    - `DB_PASSWORD`
    - `DB_NAME`

## 🏃 Running the pipeline locally

Run the command `python3 pipeline.py`

## :card_index_dividers: Files Explained

- `extract.py` : A script that extracts data from each of the plant API endpoints into a single pandas DataFrame. 
- `transform.py` : A script to clean and format all the data in the extracted DataFrame to ensure its contains all the required data and that all the data is in format ready to be loaded into the database.
- `load.py` : A script that establishes a connection to an RDS database on AWS and loads all data into the appropriate tables of the database. 
- `pipeline.py` : 
    - A script that imports functionality from the extract, transform and load scripts to allow them to all be run sequentially by running a single script.

- `test_extract`, `test_transform` and `test_load` : test suite for each respective stage script of the pipeline

- `Dockerfile` : A dockerfile that outlines the instructions and requirements to be able to containerise the pipeline directory. 

- `database`
    - `db_connect.sh` : shell script that allows quick connection to Microsoft SQL Server database via local terminal
    - `reset_db.sh` : shell script that allows quick reset of Microsoft SQL Server database via local terminal. database is reset to structure defined in schema.sql
    - `schema.sql` : database design outlined in this file. Creation of four tables - plant, location, botanist and recording tables. 