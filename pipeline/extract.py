"""Extract script that pulls all plant data from the API."""
import os
import concurrent.futures
import time


import requests
import requests.exceptions
import pandas as pd

API_URL = "https://data-eng-plants-api.herokuapp.com/plants/"


def convert_plant_data_to_csv(plant_list: list[dict]) -> None:
    """Converts the list of all plant data into one csv file."""

    plant_dataframe = pd.DataFrame(plant_list)

    os.makedirs('./data/', exist_ok=True)
    plant_dataframe.to_csv('./data/plant_data.csv',
                           header='column_names', index=False)

    return plant_dataframe


def flatten_and_organize_data(plant_dict: dict) -> dict:
    """Flattens the data and selects only the parts of the data we need."""

    if plant_dict == {}:
        raise ValueError("Plant data was empty")

    botanist_email = plant_dict["botanist"]["email"]
    botanist_name = plant_dict["botanist"]["name"]
    botanist_phone = plant_dict["botanist"]["phone"]

    country_initials = plant_dict["origin_location"][3]
    continent = plant_dict["origin_location"][4].split("/")[0]
    region = plant_dict["origin_location"][2]

    plant_id = str(int(plant_dict["plant_id"] + 1))

    new_plant_dict = {"Id": plant_id, "Name": plant_dict["name"],
                      "Last Watered": plant_dict["last_watered"],
                      "Recording Taken": plant_dict["recording_taken"],
                      "Soil Moisture": plant_dict["soil_moisture"],
                      "Temperature": plant_dict["temperature"],
                      "Botanist Name": botanist_name,
                      "Botanist Email": botanist_email,
                      "Botanist Phone": botanist_phone,
                      "Region": region, "Country's Initials": country_initials,
                      "Continent": continent}

    return new_plant_dict


def fetch_plant_data(current_plant, session):
    """
    Fetches data for a single plant.
    """
    try:
        response = session.get(f"{API_URL}{current_plant}", timeout=20)
        plant_json = response.json()
        plant_keys = plant_json.keys()

        if 'error' not in plant_keys:
            return flatten_and_organize_data(plant_json)
    except requests.exceptions.JSONDecodeError:
        pass

    return None


def fetch_all_plant_data() -> list[dict]:
    """
    Fetches all 50 plants data from the API,
    reads the data into a dict using multiprocessing.
    """

    max_plants = 55

    with concurrent.futures.ThreadPoolExecutor() as multiprocessor:
        session = requests.Session()

        def partial_fetch_plant_data(
            plant): return fetch_plant_data(plant, session)
        plant_data = list(multiprocessor.map(
            partial_fetch_plant_data, range(max_plants)))

    return [plant for plant in plant_data if plant is not None]


if __name__ == "__main__":

    st = time.time()

    plant_api_data = fetch_all_plant_data()

    convert_plant_data_to_csv(plant_api_data)

    # get the end time
    et = time.time()

    # get the execution time
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')
