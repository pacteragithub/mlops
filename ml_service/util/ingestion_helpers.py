
import os
from azureml.core import Datastore, Dataset


def write_files_to_local(dict_dfs, data_directory):
    """
    Function to write files to a path and return a list of file paths
    dict_dfs        : Dictionary with key as dataset name and value as DataFrame
    data_directory  : Location where the file should be saved
    return          : dict of paths of all the files with key as datasetname and value as full path
    """

    # Initialize a list to store complete paths
    dict_comp_paths = {}

    # Get full path of directory
    directory_full_path = os.path.abspath(data_directory)

    # Iterate over the dictionary:
    for key in dict_dfs.keys():

        # Creating a file name
        req_file_name = key + ".csv"

        # File path
        req_file_path = os.path.join(directory_full_path, req_file_name)

        # required dataframe is value in the dictionary
        req_df = dict_dfs[key]

        try:
            # Writing to local
            req_df.to_csv(req_file_path)

            # if write is successful, Append the file path to the list
            dict_comp_paths[key] = req_file_path
        except Exception as ex:
            print(ex)

    return dict_comp_paths


def upload_and_register_datasets(dict_comp_paths_files, aml_workspace, datastore_name, target_path, sub_folder_name):
    """
    Function to upload files to a datastore
    dict_comp_paths_files   : Dictionary with dataset name as key and full path as value
    aml_workspace           : AML workspace object
    datastore_name          : Name of the datastore tagged to AML workspace
    target_path             :Folder path on the datastore
    sub_folder_name         : Subfolder name where the datasets should be registered
    return                  : "success" or "failure" based on the upload status
    """

    # Target path including subfolder
    target_sub_folder = os.path.join(target_path, sub_folder_name, "")

    for key, value in dict_comp_paths_files.items():

        # Assigning dataset name and full path of the file
        dataset_name = key
        comp_file_path = value

        # Connect to the datastore object in the AML workspace
        aml_datastore = Datastore.get(aml_workspace, datastore_name=datastore_name)

        try:
            # Upload files to datastore in workspace
            aml_datastore.upload_files(files=[comp_file_path],  # Upload the titanic csv files in /data
                                       target_path=target_sub_folder,  # Put it in a folder path in the datastore
                                       overwrite=True,  # Replace existing files of the same name
                                       show_progress=True)

            # Basefile name
            base_filename = os.path.basename(comp_file_path)

            # Path on datastore
            path_on_datastore = os.path.join(target_sub_folder, base_filename)

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
                print(f"Error in registering datasets on datastore")
                print(ex)

        except Exception as ex:
            print(f"Error in uploading files onto the datastore\n")
            print(ex)