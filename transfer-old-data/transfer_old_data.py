"""
Script that gets and removes all data from an RDS, uploading it
to a CSV file in an S3 bucket in the process.
"""

from io import StringIO
from os import environ, _Environ

import pandas as pd
from boto3 import client
from mypy_boto3_s3 import S3Client
from dotenv import load_dotenv
from sqlalchemy import create_engine, sql, Connection

ARCHIVE_BUCKET = "c9-ladybird-lnhm-data-bucket"
ARCHIVE_KEY = 'lmnh_plant_data_archive.csv'

GET_QUERY = sql.text("""SELECT rec.recording_id, rec.soil_moisture, rec.temperature,
                     rec.recording_taken, rec.last_watered, plant.name AS plant_name,
                     bot.name, bot.email, bot.telephone_number, loc.region, loc.country,
                     loc.continent
                     FROM s_delta.recording AS rec
                     JOIN s_delta.plant AS plant ON rec.plant_id = plant.plant_id
                     JOIN s_delta.botanist AS bot ON plant.botanist_id = bot.botanist_id
                     JOIN s_delta.location AS loc ON plant.location_id = loc.location_id;
                     """)

DELETE_QUERY = sql.text("""DELETE FROM s_delta.recording;""")

COLUMNS = {"recording_id": "Recording ID", "soil_moisture": "Soil Moisture",
           "temperature": "Temperature", "recording_taken": "Recording Taken",
           "last_watered": "Last Watered", "plant_name": "Plant Name", "name": "Botanist Name",
           "email": "Botanist Email", "telephone_number": "Botanist Phone Number",
           "region": "Region", "country": "Country", "continent": "Continent"}


def get_database_connection(config: _Environ) -> Connection:
    """Get a connection to the short term database."""
    sql_engine = create_engine(
        f"mssql+pymssql://{config['DB_USERNAME']}:{config['DB_PASSWORD']}@{config['DB_HOST']}/?charset=utf8")

    connection = sql_engine.connect()

    return connection


def get_s3_client(config: _Environ) -> S3Client:
    """Get a connection to the relevant S3 bucket."""
    s3_client = client("s3",
                       aws_access_key_id=config["AWS_ACCESS_KEY_ID"],
                       aws_secret_access_key=config["AWS_SECRET_ACCESS_KEY"])
    return s3_client


def extract_old_data_from_database(connection: Connection) -> pd.DataFrame:
    """Extract all data from the database."""

    connection.execute(sql.text("USE plants;"))

    result = connection.execute(GET_QUERY).fetchall()

    return pd.DataFrame(result).rename(columns=COLUMNS)


def get_archive_data_csv(s3_client: S3Client, bucket: str, key: str) -> pd.DataFrame:
    """Retrieves the archived data from an S3 bucket."""

    obj = s3_client.get_object(Bucket=bucket, Key=key)
    csv_str = obj["Body"].read().decode()
    return pd.read_csv(StringIO(csv_str))


def update_archive_data(arch_df: pd.DataFrame, new_df: pd.DataFrame) -> pd.DataFrame:
    """Updates the archived dataframe with new data."""

    return pd.concat([arch_df, new_df], ignore_index=True, sort=False)


def delete_data_from_db(conn: Connection) -> None:
    """Deletes all data from the database."""

    conn.execute(DELETE_QUERY)
    conn.execute(sql.text("COMMIT;"))


if __name__ == "__main__":

    load_dotenv()

    conn = get_database_connection(environ)
    s3_client = get_s3_client(environ)

    arch_data = get_archive_data_csv(s3_client, ARCHIVE_BUCKET, ARCHIVE_KEY)
    new_plant_data = extract_old_data_from_database(conn)
    combined_data = update_archive_data(arch_data, new_plant_data)

    combined_data.to_csv(
        f"s3://{ARCHIVE_BUCKET}/{ARCHIVE_KEY}", index=False
    )

    delete_data_from_db(conn)
