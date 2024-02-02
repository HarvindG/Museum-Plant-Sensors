"""Unit tests created to ensure the functionality of the load script."""
from unittest.mock import MagicMock

import pandas as pd

from load import insert_into_location_table, insert_into_plant_table

TEST_PLANT_DATA = [{"Id": "1", "Name": "Epipremnum Aureum", "watered": "2023-12-19 14:03:04",
                   "recording": "2023-12-19 15:02:35",
                    "moisture": "96.54", "temp": "13.14", "botanist": "Carl Linnaeus",
                    "email": "carl.linnaeus@lnhm.co.uk", "phone": "(146)994-1635x35992",
                    "region": "Resplendor", "country": "America", "continent": "Brazil"}]


def test_insert_into_location_table():
    """Tests that the insert into location table works correctly."""

    mock_connection = MagicMock()
    mock_execute = mock_connection.execute

    plant_dataframe = pd.DataFrame(TEST_PLANT_DATA)

    insert_into_location_table(mock_connection, plant_dataframe)

    assert mock_execute.call_count == len(plant_dataframe)


def test_insert_into_plant_table():
    """Tests the insert into plants functions runs the correct commands"""

    mock_connection = MagicMock()
    mock_execute = mock_connection.execute

    plant_dataframe = pd.DataFrame(TEST_PLANT_DATA)

    insert_into_plant_table(mock_connection, plant_dataframe)

    assert mock_execute.call_count == len(plant_dataframe)
