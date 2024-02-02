import pytest
import pandas as pd
from datetime import datetime

from transform import standardize_country_name, remove_rows_with_null, check_soil_temp_valid, check_soil_moisture_valid, normalize_datetimes


def test_standardize_country_name():
    """Testing basic functionality of country converter"""
    assert standardize_country_name('UK') == 'United Kingdom'


def test_standardize_country_name_2():
    """Testing basic functionality of country converter"""
    assert standardize_country_name('US') == 'United States'


def test_standardize_country_name_3():
    """Testing basic functionality of country converter"""
    assert standardize_country_name('FR') == 'France'


def test_standardize_country_name_4():
    """Testing basic functionality of country converter"""
    assert standardize_country_name('CL') == 'Chile'


def test_remove_rows_with_null():
    """Testing that null rows in given columns are dropped"""
    data = {'A': [None, 2, 1, 4],
            'B': [5, None, 7, 8],
            'C': [9, 10, 11, 12]}

    df = pd.DataFrame(data)
    critical_columns = ['A', 'B']

    df = remove_rows_with_null(df, critical_columns)
    assert df.to_dict() == {'A': {2: 1.0, 3: 4.0},
                            'B': {2: 7.0, 3: 8.0},
                            'C': {2: 11.0, 3: 12.0}}


def test_check_soil_temp_valid():
    """Testing soil temperature is within valid range"""
    data = {'Plant Name': ['PlantA', 'PlantB', 'PlantC', 'PlantD'],
            'Temperature': [-4, 101, 15, 31]}

    df = pd.DataFrame(data)

    df = check_soil_temp_valid(df)

    assert df.to_dict() == {'Plant Name': {2: 'PlantC'},
                            'Temperature': {2: 15.0}}


def test_check_soil_moisture_valid():
    """Testing soil moisture is within valid range"""
    data = {'Plant Name': ['PlantA', 'PlantB', 'PlantC'],
            'Soil Moisture': [-4.435, 101.45, 15.54]}

    df = pd.DataFrame(data)

    df = check_soil_moisture_valid(df)

    assert df.to_dict() == {'Plant Name': {2: 'PlantC'},
                            'Soil Moisture': {2: 15.54}}


def test_normalize_datetimes():
    """Testing datetimes are able to be normalised"""
    data = {'Plant Name': ['PlantA'],
            'Last Watered': ['Mon, 18 Dec 2023 14:03:04 GMT'],
            'Recording Taken': ['Mon, 18 Dec 2023 14:03:04 GMT']
            }

    df = pd.DataFrame(data)

    df = normalize_datetimes(df)

    assert df.to_dict() == {'Plant Name': {0: 'PlantA'},
                            'Last Watered': {0: pd.Timestamp('2023-12-18 14:03:04')},
                            'Recording Taken': {0: pd.Timestamp('2023-12-18 14:03:04+0000', tz='GMT')}}


def test_normalize_datetimes_invalid_datetime():
    """Testing rows where date columns are entered with invalid datetimes are dropped"""
    data = {'Plant Name': ['PlantA'],
            'Last Watered': [''],
            'Recording Taken': ['']
            }

    df = pd.DataFrame(data)

    df = normalize_datetimes(df)

    assert df.to_dict() == {'Plant Name': {},
                            'Last Watered': {},
                            'Recording Taken': {}}
