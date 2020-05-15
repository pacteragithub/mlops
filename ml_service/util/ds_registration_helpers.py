
import os
from azureml.core import Datastore, Dataset


def write_file_to_local(dataset_name, req_df, data_directory):
    """
    Function to write files to a path and return a list of file paths
    dataset_name (str)      : Dataset name
    req_df (DataFrame)      : DataFrame corresponding to the dataset_name
    data_directory (str)    : Location where the file should be saved
    return (str)            : Full path of the file written to local
    """
    # Initialize require file path to be None
    full_file_path = None

    # Get full path of directory
    directory_full_path = os.path.abspath(data_directory)

    # Creating a file name
    req_file_name = dataset_name + ".csv"

    # File path
    req_file_path = os.path.join(directory_full_path, req_file_name)

    try:
        # Writing to local
        req_df.to_csv(req_file_path)

        # if write is successful, Append the file path to the list
        full_file_path = req_file_path
    except Exception as ex:
        print(ex)

    return full_file_path


def upload_and_register_dataset(req_full_file_path, dataset_name, aml_workspace, datastore_name, folderpath_on_dstore):
    """
    Function to upload files to a datastore
    req_full_file_path (str)    : Full os path of the filename
    dataset_name (str)          : Name of the dataset with which it should be registered on aml workspace
    aml_workspace (Workspace)   : AML workspace object
    datastore_name (str)        : Name of the datastore tagged to AML workspace
    folderpath_on_dstore(str)   : Subfolder name where the datasets should be registered
    return                      : "success" or "failure" based on the upload status
    """

    # Status
    status = "success"

    # Connect to the datastore object in the AML workspace
    aml_datastore = Datastore.get(aml_workspace, datastore_name=datastore_name)

    try:
        # Upload files to datastore in workspace
        aml_datastore.upload_files(files=[req_full_file_path],  # Upload the titanic csv files in /data
                                   target_path=folderpath_on_dstore,  # Put it in a folder path in the datastore
                                   overwrite=True,  # Replace existing files of the same name
                                   show_progress=True)

        # Basefile name extracted from local path
        base_filename = os.path.basename(req_full_file_path)

        # Path on datastore (Joined with path on datastore and basefilename)
        path_on_datastore = os.path.join(folderpath_on_dstore, base_filename)

        # Register dataset
        dataset = Dataset.Tabular.from_delimited_files(
            path=(aml_datastore, path_on_datastore))

        try:
            dataset = dataset.register(
                workspace=aml_workspace,
                name=dataset_name,
                # description='titanic training data',
                tags={'format': 'CSV'},
                create_new_version=True)

        except Exception as ex:
            print(f"Error in registering dataset {dataset_name} on datastore {datastore_name}")
            print(ex)
            status = "failure"

    except Exception as ex:
        print(f"Error in uploading file {req_full_file_path} onto the datastore {datastore_name}\n")
        print(ex)
        status = "failure"

    return status


def create_and_register_datasets(aml_workspace, datastore_name, dict_dfs, rerun_data_ingest,
                                 ingested_data_directory, folderpath_on_dstore):
    """
    Function to create and register datasets

    """

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
            print(f"--"*75)
            print(f"{status.upper()}: Dataset {dataset_name} is uploaded to {datastore_name}"
                  f" on folder {folderpath_on_dstore}"
                  f" and registered on workspace {aml_workspace.name}")
            print(f"--" *75)
        else:
            print(f"Dataset {dataset_name} is already available on datastore {datastore_name}\n"
                  f"No Dataset Creation and Registration was triggered using")
