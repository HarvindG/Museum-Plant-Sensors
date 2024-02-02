"""Transform script that produces cleaned data after extracting from APIs"""

import pandas as pd
import country_converter as coco


def standardize_country_name(country_name: str) -> str:
    """
    Convert country code given into standard country name.
    """
    return coco.convert(names=country_name, to='name_short')


def remove_rows_with_null(dataframe, columns):
    """
    Remove rows with null values in specified columns of a DataFrame.
    """
    return dataframe.dropna(subset=columns)


def check_soil_temp_valid(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Check if temperature reading is valid.
    """
    temp_conditions = (
        (dataframe['Temperature'] > 0) &
        (dataframe['Temperature'] < 30)
    )

    return dataframe[temp_conditions]


def check_soil_moisture_valid(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Check if temperature reading is valid.
    """
    moisture_conditions = (
        (dataframe['Soil Moisture'] > 0) &
        (dataframe['Soil Moisture'] < 100)
    )

    return dataframe[moisture_conditions]


def normalize_datetimes(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Check if datetimes are valid. Drop non-valid values
    """
    dataframe['Last Watered'] = pd.to_datetime(
        dataframe['Last Watered'], errors='coerce').dt.tz_localize(None)
    dataframe['Recording Taken'] = pd.to_datetime(
        dataframe['Recording Taken'], errors='coerce')

    dataframe = dataframe.dropna(subset=['Last Watered', 'Recording Taken'])

    return dataframe


def change_temp_and_moisture_to_two_dp(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Round values of temperature and soil moisture to include only two decimal places
    """
    dataframe['Soil Moisture'] = dataframe['Soil Moisture'].round(2)
    dataframe['Temperature'] = dataframe['Temperature'].round(2)

    return dataframe


def csv_to_data_frame(filename: str) -> pd.DataFrame:
    """Converts a csv file to a pandas data frame."""

    return pd.read_csv(filename)


def upload_clean_csv_file(filename: str, plant_data: pd.DataFrame) -> None:
    """Creates a new CSV file with the clean data"""

    plant_data.to_csv(filename, index=False)


if __name__ == "__main__":

    plants = csv_to_data_frame("./data/plant_data.csv")

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

    # Add clean data to new file
    upload_clean_csv_file('./data/cleaned_plant_data.csv', plants)
