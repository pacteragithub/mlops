
from .clean_helpers import convert_to_datetime
from pandas import read_csv
from dotenv import load_dotenv
import os


def data_creation():
    """
    This function would be used for data ingestion pipeline
    Inputs : Load necessary environment variables for connecting to database, other config variables etc.,
    Output : DataFrame which will be further used for modeling
    """
    # Block to read environment variables
    load_dotenv()

    # Connection to Database

    # Data Manipulation

    # Finalize the dataset

    # Dummy code to test if .csv ingestion works
    data_folder_dir = os.environ.get(["INGESTED_DATA_DIR"])
    ingest_data_filename = os.environ.get(["INGESTED_DATA_FILENAME"])
    data_file_path = data_folder_dir + "/" + ingest_data_filename + ".csv"

    # Read the csv
    req_data = read_csv(data_file_path)

    return req_data
