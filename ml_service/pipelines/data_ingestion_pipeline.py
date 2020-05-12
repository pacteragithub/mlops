from azureml.core import Workspace, Dataset, Datastore
from azureml.core.runconfig import RunConfiguration
from ml_service.util.env_variables import Env
from kaggle_titanic.data_ingestion import data_creation
import os


def main():
    # Loading environment variables
    e = Env()

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
    # If dataset is not already registered or fresh data ingest flag rerun dataset creation
    if (dataset_name not in aml_workspace.datasets) or e.fresh_data_ingest:

        # Pull Data from SQL or CSV and save it to local
        req_data = data_creation()

        # Filename of the complete path
        comp_file_path = e.ingested_data_directory + "/" + e.ingested_data_filename + ".csv"

        # Write to csv
        req_data.to_csv(comp_file_path)

        # Upload file to datastore linked to workspace
        # Get the datastore info from the workspace
        aml_datastore = Datastore.get(aml_workspace, datastore_name=datastore_name)

        # Target path on the datastore where the data should be saved
        target_path = "training_data/"

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


if __name__ == '__main__':
    main()