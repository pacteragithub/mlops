# Environment related utilities
import os
from ml_service.util.env_variables import Env

# Azure core ML modules
from azureml.core import Workspace, Dataset, Datastore

# Data Ingestion related
from kaggle_titanic.data_ingestion import data_preparation

# Other utilities
from ast import literal_eval


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

    # Read dataset name from environment variables
    dataset_name = e.dataset_name

    # Check if the dataset exists in the aml workspace
    ds_unavailable = dataset_name not in aml_workspace.datasets
    rerun_data_ingest = literal_eval(e.fresh_data_ingest)

    # If dataset is not already registered or fresh data ingest flag rerun dataset creation
    if ds_unavailable or rerun_data_ingest:

        if ds_unavailable:
            print(f"Dataset {dataset_name} unavailable on datastore {datastore_name}\n"
                  f"Dataset Creation and Registration triggered for the first time")
        else:
            print(f"Dataset {dataset_name} already exists on datastore {datastore_name}\n"
                  f"Dataset Creation and Registration triggered due to change in data or code base")

        # Pull Data from SQL or CSV and save it to local
        req_data = data_preparation()

        # Filename of the complete path
        comp_file_path = e.ingested_data_directory + "/" + e.ingested_data_filename

        # Write to csv
        req_data.to_csv(comp_file_path)

        # Upload file to datastore linked to workspace
        # Get the datastore info from the workspace
        aml_datastore = Datastore.get(aml_workspace, datastore_name=datastore_name)

        # Target path on the datastore where the data should be saved
        target_path = e.path_on_datastore

        # Upload files to datastore in workspace
        aml_datastore.upload_files(files=[comp_file_path],  # Upload the titanic csv files in /data
                                   target_path=target_path,  # Put it in a folder path in the datastore
                                   overwrite=True,  # Replace existing files of the same name
                                   show_progress=True)

        # Path on datastore
        path_on_datastore = os.path.join(target_path, e.ingested_data_filename)

        # Register dataset
        dataset = Dataset.Tabular.from_delimited_files(
            path=(aml_datastore, path_on_datastore))

        try:
            dataset = dataset.register(
                workspace=aml_workspace,
                name=dataset_name,
                description='titanic training data',
                tags={'format': 'CSV'},
                create_new_version=True)

        except Exception as ex:
            print(ex)
    else:
        print(f"Dataset {dataset_name} is already available on datastore {datastore_name}\n"
              f"No Dataset Creation and Registration was performed during the run")


if __name__ == '__main__':
    main()