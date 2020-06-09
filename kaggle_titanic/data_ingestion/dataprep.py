
import os
from azure.storage.blob import BlockBlobService
import pandas as pd
from .clean_helpers import convert_to_datetime
from pandas import read_csv
from ml_service.util.env_variables import Env
from azure.storage.blob import BlobClient


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
    #req_data = read_csv(data_file_path)
    
#     STORAGEACCOUNTNAME= <storage_account_name>
#     STORAGEACCOUNTKEY= <storage_account_key>
#     LOCALFILENAME= <local_file_name>
#     CONTAINERNAME= <container_name>
#     BLOBNAME= <blob_name>

#     #download from blob
#     t1=time.time()
#     blob_service=BlockBlobService(account_name=STORAGEACCOUNTNAME,account_key=STORAGEACCOUNTKEY)
#     blob_service.get_blob_to_path(CONTAINERNAME,BLOBNAME,LOCALFILENAME)
#     t2=time.time()
#     print(("It takes %s seconds to download "+blobname) % (t2 - t1))
      
      
    blob = BlobClient(account_url="https://mlopsfoundationamlsa.blob.core.windows.net"
                  container_name="mlops-foundation",
                  blob_name="raw_data/titanic_dataset.csv",
                  credential="iS2psbL4ar7bBOiBHxPMlHTmlhykt3dOdMGh4ZyR+mzfdoFFm+nwyI8u8ayN6a1YJmotA/Ge14LrL0jZSJDboA==")

    with open("./titanic_dataset.csv", "wb") as f:
        data = blob.download_blob()
        req_data=pd.read_csv(data)
        #data.readinto(f)

    # Initialize a dictionary to store dataframe objects with names
    data_dict = {}

    # Add key value pairs to the dictionary
    data_dict["passenger_data"] = req_data
    data_dict["transaction_data"] = req_data

    return data_dict
