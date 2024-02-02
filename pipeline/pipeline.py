"""
Pipeline script that connects the ETL scripts,
Runs the pipeline in a loop every 1 min.
"""

import time
from os import environ
import logging
from datetime import datetime

import requests
from dotenv import load_dotenv
import pandas as pd

from extract import fetch_all_plant_data
from transform import standardize_country_name, remove_rows_with_null, check_soil_moisture_valid, check_soil_temp_valid, normalize_datetimes, change_temp_and_moisture_to_two_dp
from load import create_database_connection, insert_into_recordings_table, insert_into_location_table, insert_into_botanist_table, insert_into_plant_table

if __name__ == "__main__":

    logging.basicConfig(filename='execution_time.log',
                        encoding='utf-8', level=logging.DEBUG)

    logging.getLogger('urllib3').setLevel(logging.WARNING)

    load_dotenv()

    while True:

        # Starts a timer for each iteration of the pipeline
        start_time = time.time()
        logging.debug(str(datetime.now()) + ': Initializing pipeline')

        # Fetches all plant data from the api

        plant_api_data = fetch_all_plant_data()

        extract_time = time.time() - start_time
        logging.debug(str(datetime.now()) + ': Time taken to extract data: ' +
                      str(extract_time) + ' seconds')

        # Creates a csv file for the data and returns a data frame
        plants = pd.DataFrame(plant_api_data)

        # Location formatting
        plants["Country"] = plants["Country's Initials"].apply(
            standardize_country_name)

        # Drop redundant columns
        plants = plants.drop("Country's Initials", axis=1)

        # Drop rows with null values in important columns
        plants = remove_rows_with_null(plants, ["Id", "Name", "Recording Taken", "Soil Moisture",
                                                "Temperature", "Botanist Name", "Botanist Email", "Botanist Phone"])

        # Validate and round moisture and temperature values
        plants = check_soil_moisture_valid(plants)
        plants = check_soil_temp_valid(plants)
        plants = normalize_datetimes(plants)
        plants = change_temp_and_moisture_to_two_dp(plants)

        transform_time = time.time() - extract_time
        logging.debug(str(datetime.now()) + ': Time taken to transform data: ' +
                      str(transform_time) + ' seconds')

        # Creates a connection to the SQL Server
        connection = create_database_connection(environ)

        # Inserts the current iterations data into the SQL Server
        insert_into_botanist_table(connection, plants)
        insert_into_location_table(connection, plants)
        insert_into_plant_table(connection, plants)

        insert_into_recordings_table(connection, plants)

        load_time = time.time() - (extract_time + transform_time)
        logging.debug(str(datetime.now()) + ': Time taken to load data: ' +
                      str(load_time) + ' seconds')

        # get the end time
        et = time.time()

        # get the execution time
        elapsed_time = et - start_time
        logging.debug(str(datetime.now()) + ': Total execution time: ' +
                      str(elapsed_time) + ' seconds')

        time.sleep(30)
