"""Script to run the dashboard app, displaying the key plant data for the LNHM botanical wing."""
from io import StringIO
from os import environ, _Environ
import datetime

import altair as alt
from dotenv import load_dotenv
import pandas as pd
from boto3 import client
from mypy_boto3_s3 import S3Client
from sqlalchemy import create_engine, Connection, sql
import streamlit as st

ARCHIVE_BUCKET = "c9-ladybird-lnhm-data-bucket"

ARCHIVE_KEY = 'lmnh_plant_data_archive.csv'

COLOUR_LIST = ['#7db16a', '#c6d485', '#618447', '#5e949b', '#415d2e',
               '#d7f1ec', '#b7c62d', '#0f1511', '#3e6164', '#87c7cd',
               '#2d4221', '#6a6539' '#2b4242', '#48472f', '#1e2f1d']

QUERY = sql.text("""SELECT rec.recording_id, rec.soil_moisture, rec.temperature,
                     rec.recording_taken, rec.last_watered, plant.name AS plant_name,
                     bot.name, bot.email, bot.telephone_number, loc.region, loc.country,
                     loc.continent
                     FROM s_delta.recording AS rec
                     JOIN s_delta.plant AS plant ON rec.plant_id = plant.plant_id
                     JOIN s_delta.botanist AS bot ON plant.botanist_id = bot.botanist_id
                     JOIN s_delta.location AS loc ON plant.location_id = loc.location_id;
                     """)

COLUMNS = {"recording_id": "Recording ID", "soil_moisture": "Soil Moisture",
           "temperature": "Temperature", "recording_taken": "Recording Taken",
           "last_watered": "Last Watered", "plant_name": "Plant Name", "name": "Botanist Name",
           "email": "Botanist Email", "telephone_number": "Botanist Phone Number",
           "region": "Region", "country": "Country", "continent": "Continent"}


def get_s3_client(config: _Environ) -> S3Client:
    """Get a connection to the relevant S3 bucket."""
    s3client = client("s3",
                       aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                       aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])
    return s3client


def get_archive_data_csv(s3client: S3Client, bucket: str, key: str) -> pd.DataFrame:
    """Retrieves the archived data from an S3 bucket."""

    obj = s3client.get_object(Bucket=bucket, Key=key)
    csv_str = obj["Body"].read().decode()
    return pd.read_csv(StringIO(csv_str))


def get_db_connection(config: _Environ) -> Connection:
    """Creates a database connection to the SQL Server."""
    engine = create_engine(
        f"mssql+pymssql://{config['DB_USERNAME']}:{config['DB_PASSWORD']}@{config['DB_HOST']}/?charset=utf8")
    conn = engine.connect()
    return conn


def get_data_from_db(conn: Connection) -> pd.DataFrame:
    """Returns a dataframe containing all the food truck data."""
    conn.execute(sql.text("USE plants;"))
    recording_data = conn.execute(QUERY)
    recordings_df = pd.DataFrame(recording_data.fetchall())
    recordings_df = recordings_df.rename(columns=COLUMNS)
    return recordings_df


def get_date_and_time_from_data(data: pd.DataFrame) -> pd.DataFrame:
    """Extracts the date from the datetime values for recordings taken."""
    data['date'] = data['Recording Taken'].dt.date
    data['time'] = data['Recording Taken'].dt.time
    return data


def get_last_watered_plants(data: pd.DataFrame, chosen_plants: list[str]) -> pd.DataFrame:
    """Extracts the most recent value for when each plant was last watered."""
    data = data[data['Plant Name'].isin(chosen_plants)]
    sorted_by_last_watered = data.sort_values(by='Last Watered')
    each_plant_data = sorted_by_last_watered.drop_duplicates('Plant Name', keep='last')
    return each_plant_data[['Plant Name', 'Last Watered']]


def temp_line_chart(data: pd.DataFrame, chosen_plants: list[str]) -> st.altair_chart:
    """Creates a line graph showing temperature of soil throughout the day for plants."""
    data = data[data['Plant Name'].isin(chosen_plants)].rename(
        columns={'Temperature': 'Soil Temperature', 'Recording Taken': 'Time'})
    title = alt.TitleParams(
        'Temperature of soil over time', anchor='middle')
    color = alt.Color('Plant Name', scale=alt.Scale(range=COLOUR_LIST))
    figure = alt.Chart(data).mark_line().encode(
        x='hoursminutes(Time)', y='Soil Temperature', color=color).properties(title=title)
    return figure


def moisture_line_chart(data: pd.DataFrame, chosen_plants: list[str]) -> st.altair_chart:
    """Creates a line graph showing moisture levels of soil throughout the day for plants."""
    data = data[data['Plant Name'].isin(chosen_plants)].rename(
        columns={'Recording Taken': 'Time'})
    title = alt.TitleParams(
        'Moisture Level of soil over time', anchor='middle')
    color = alt.Color('Plant Name', scale=alt.Scale(range=COLOUR_LIST))
    figure = alt.Chart(data).mark_line().encode(
        x='hoursminutes(Time)', y='Soil Moisture', color=color).properties(title=title)
    return figure


def filter_by_date(chosen_date: datetime.date,
                   current_data: pd.DataFrame,
                   archived_data: pd.DataFrame) -> pd.DataFrame:
    """Filters by the chosen date, returns relevant data to be displayed in a pandas dataframe."""
    if chosen_date == datetime.date.today():
        data = current_data
    else:
        data = archived_data[(archived_data['date'] == chosen_date)]
    return data


def filter_by_country(data: pd.DataFrame) -> list[str]:
    """Retrieves the plants relevant to the selected countries and returns plant names as a list."""
    chosen_countries = st.sidebar.multiselect("Select Country", data['Country'].unique(),
                                                default=None, placeholder="Choose an option")

    country_plants = data[data['Country'].isin(chosen_countries)]['Plant Name'].unique()
    chosen_plants = st.sidebar.multiselect("Select Plant", country_plants,
                                           default=None, placeholder="Choose an option")

    return chosen_plants


def filter_by_botanist(data: pd.DataFrame) -> list[str]:
    """Retrieves the plants relevant to the selected botanists and returns plant names as a list."""
    chosen_botanists = st.sidebar.multiselect("Select Botanist", data['Botanist Name'].unique(),
                                            default=data['Botanist Name'].unique(),
                                            placeholder="Choose an option")

    botanist_plants = data[data['Botanist Name'].isin(chosen_botanists)]['Plant Name'].unique()
    chosen_plants = st.sidebar.multiselect("Select Plant", botanist_plants,
                                            default=None, placeholder="Choose an option")

    return chosen_plants


def soil_monitoring_charts(data:pd.DataFrame, chosen_plants:list[str]) -> None:
    """Plots the temperature and soil moisture charts."""
    st.subheader('Soil Monitoring', anchor=None, divider='grey')
    st.altair_chart(moisture_line_chart
                    (data, chosen_plants), theme=None, use_container_width=True)
    st.altair_chart(temp_line_chart
                    (data, chosen_plants), theme=None, use_container_width=True)


def last_watered_table(data:pd.DataFrame, chosen_plants:list[str]) -> None:
    """Plots the table of last watered data against plant name."""
    st.subheader('Last Watered Data', anchor=None, divider='grey')
    st.dataframe(get_last_watered_plants(
            data, chosen_plants), hide_index=True, use_container_width=True)


if __name__ == "__main__":

    load_dotenv()

    # connecting to the database and retrieving the data:
    connection = get_db_connection(environ)
    todays_data = get_data_from_db(connection)
    todays_data = get_date_and_time_from_data(todays_data)

    # connecting to the s3 bucket and retrieving archive data file:
    s3_client = get_s3_client(environ)
    archive_data = get_archive_data_csv(s3_client, ARCHIVE_BUCKET, ARCHIVE_KEY)
    archive_data['Recording Taken'] = pd.to_datetime(archive_data['Recording Taken'])
    archive_data = get_date_and_time_from_data(archive_data)

    all_dates = pd.concat([todays_data['date'], archive_data['date'][::-1]]).unique()

    # establishing streamlit dashboard title.
    st.title(':herb: LNHM Botanical Plant Sensors :herb:')

    # setting up a filter search on the side bar.
    st.sidebar.header('Filters:')

    #filtering by date
    selected_date = st.sidebar.selectbox(
        "Select Date:", all_dates, index=0)
    relevant_data = filter_by_date(selected_date, todays_data, archive_data)

    # option to filter by country or botanist.
    filter_choice = st.sidebar.selectbox("Filter by:", ['Botanist', 'Country'])

    if filter_choice == "Country":
        selected_plants = filter_by_country(relevant_data)

    if filter_choice == "Botanist":
        selected_plants = filter_by_botanist(relevant_data)

    # displays relevant charts depending on the date and plants selected.
    if selected_plants and selected_date == datetime.date.today():
        last_watered_table(relevant_data, selected_plants)
        soil_monitoring_charts(relevant_data, selected_plants)

    elif selected_plants:
        soil_monitoring_charts(relevant_data, selected_plants)

    else:
        st.subheader('Please use the filters to display relevant data :hibiscus:',
                     anchor=None, divider='grey', )
