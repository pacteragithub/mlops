# Environment related utilities
import os
from ml_service.util.env_variables import Env

# Azure core ML modules
from azureml.core import Workspace, Dataset, Datastore

# Data Ingestion related
from kaggle_titanic.data_ingestion import data_preparation
from ml_service.util.ingestion_helpers import write_file_to_local, upload_and_register_dataset

# Other utilities
from ast import literal_eval
from datetime import datetime


def main():

    # Loading environment variables
    e = Env()

    # Connect to AML workspace using credentials
    aml_workspace = Workspace.get(
        name=e.workspace_name,
        subscription_id=e.subscription_id,
        resource_group=e.resource_group
    )
    print("get_workspace:")
    print(aml_workspace)

    # Check if the datastore environment variable is valid or not
    if (e.datastore_name): # if valid name assign it
        datastore_name = e.datastore_name
    else: # get the default datastore tagged to the workspace
        datastore_name = aml_workspace.get_default_datastore().name

    # Read the rerun data ingestion from environment variables
    rerun_data_ingest = literal_eval(e.fresh_data_ingest)

    # Directory to the save prepared dataset
    ingested_data_directory = e.ingested_data_directory

    # Target path on the datastore where the data should be saved
    target_path = e.path_on_datastore

    # SubFolder name on datastore would be created as per datetime
    sub_folder_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    folderpath_on_dstore = os.path.join(target_path, sub_folder_name, "")

    # Pull Data from SQL or CSV and save it to local
    # dict_dfs is a dictionary with key value pairs {"dataset_name":DataFrame}
    dict_dfs = data_preparation()

    # Iterate for each dataset in the dict_df
    for key, value in dict_dfs.items():

        # Assign key and values to the required variables
        dataset_name = key
        req_df = value

        # Check if the dataset exists in the aml workspace
        ds_unavailable = dataset_name not in aml_workspace.datasets

        # If dataset is not already registered or fresh data ingest flag rerun dataset creation
        if ds_unavailable or rerun_data_ingest:

            if ds_unavailable:
                print(f"Dataset {dataset_name} unavailable on datastore {datastore_name}\n"
                      f"Dataset Creation and Registration triggered for the first time")
            else:
                print(f"Dataset {dataset_name} already exists on datastore {datastore_name}\n"
                      f"Dataset Creation and Registration triggered due to change in data or code base")

            # Write files to a local path and get full paths
            req_full_file_path = write_file_to_local(dataset_name, req_df, ingested_data_directory)

            # Upload files to the datastore
            status = upload_and_register_dataset(req_full_file_path, dataset_name, aml_workspace,
                                                 datastore_name, folderpath_on_dstore)

            # Print based on status
            print(f"--"*50)
            print(f"{status.upper()}: Dataset {dataset_name} is uploaded to {datastore_name}"
                  f" and registered on workspace {aml_workspace.name}")
            print(f"--" * 50)
        else:
            print(f"Dataset {dataset_name} is already available on datastore {datastore_name}\n"
                  f"No Dataset Creation and Registration was triggered using")


if __name__ == '__main__':
    main()