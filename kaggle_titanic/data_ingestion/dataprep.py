
import os
from .clean_helpers import convert_to_datetime
from pandas import read_csv
from ml_service.util.env_variables import Env


def data_preparation():
    """
    This function would be used for data ingestion pipeline
    Inputs : Load necessary environment variables for connecting to database, other config variables etc.,
    Output : Dictionary of DataFrames with keys as dataset names which will be further used for modeling
    """
    # Block to read environment variables
    e = Env()

    # Connection to Database

    # Data Manipulation

    # Finalize the dataset

    # Dummy code to test if .csv ingestion works
    data_folder_dir = "./data"
    raw_data_filename = "titanic_dataset"
    data_file_path = data_folder_dir + "/" + raw_data_filename + ".csv"

    # Read the csv
    req_data = read_csv(data_file_path)

    # Initialize a dictionary to store dataframe objects with names
    data_dict = {}

    # Add key value pairs to the dictionary
    data_dict["passenger_data"] = req_data
    data_dict["transaction_data"] = req_data

    return data_dict
