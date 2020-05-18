# Environment related utilities
import os
from environment_setup.env_variables import ROOT_DIR, SOURCE_DIR, \
    DATASTORE_NAME, FRESH_DATA_INGEST, SAVE_INGESTED_DATA_DIR, PATH_ON_DATASTORE,\
    CLEANSE_SCRIPT_PATH, FEATENG_SCRIPT_PATH,\
    TRAIN_SCRIPT_PATH, EVALUATE_SCRIPT_PATH, REGISTER_SCRIPT_PATH

# Azure ML related packages
from azureml.core import Datastore, Experiment
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, PipelineData

# Data Related
from kaggle_titanic.data_ingestion import data_preparation

# Fetch compute and other params
from ml_service.util.aml_helpers import get_workspace_compute_env
from ml_service.util.ds_registration_helpers import create_and_register_datasets

# other utilities
from ast import literal_eval
from datetime import datetime


def get_srcdir_and_filename(src_directory, rel_script_path):

    file_full_path = os.path.abspath(os.path.join(src_directory, rel_script_path))
    src_dir_path = os.path.dirname(file_full_path)
    script_name = os.path.basename(file_full_path)

    return src_dir_path, script_name


def main():

    # ******** Connect to Workspace, Setup Compute and Environment****** #
    aml_workspace, aml_compute, environment = get_workspace_compute_env()

    # Setting run configuration
    run_config = RunConfiguration()
    run_config.environment = environment

    # ******** Assign datastore to save and register datasets ********** #
    if (DATASTORE_NAME): # if valid name assign it
        datastore_name = DATASTORE_NAME
    else: # get the default datastore tagged to the workspace
        datastore_name = aml_workspace.get_default_datastore().name

    datastore = Datastore.get(aml_workspace, datastore_name)

    # ******** Creating and Registering Datasets *********************** #
    # Pull Data from SQL or CSV and save it to local
    # dict_dfs is a dictionary with key value pairs {"dataset_name":DataFrame}
    dict_dfs = data_preparation()

    # SubFolder name on datastore would be created as per datetime
    sub_folder_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    folderpath_on_dstore = os.path.join(PATH_ON_DATASTORE, sub_folder_name, "")

    try:
        create_and_register_datasets(aml_workspace, datastore_name, dict_dfs, literal_eval(FRESH_DATA_INGEST),
                                     SAVE_INGESTED_DATA_DIR, folderpath_on_dstore)
    except Exception as e:
        print(str(e))

    # **************** Data Cleansing Step************************** #
    # Define parameters required for the step
    dataset_name_param = "passenger_data"

    # Define output after cleansing step
    cleansed_data = PipelineData('cleansed_data', datastore=datastore).as_dataset()

    # Get full path of the cleansing scriot, folder name and script name
    cleansing_src_dir_path, cleansing_script_name = get_srcdir_and_filename(SOURCE_DIR, CLEANSE_SCRIPT_PATH)

    # cleansing step creation
    # See the cleanse.py for details about input and output
    cleansing_step = PythonScriptStep(
        name="Cleanse Raw Data",
        script_name=cleansing_script_name,
        arguments=["--dataset_name", dataset_name_param,
                   "--output_cleanse", cleansed_data],
        outputs=[cleansed_data],
        compute_target=aml_compute,
        runconfig=run_config,
        source_directory=cleansing_src_dir_path,
        allow_reuse=True
    )

    print("Data Cleansing Step created.")

    # **************** Feature Engineering Step************************** #
    # Define output after cleansing step
    feateng_data = PipelineData('feateng_data', datastore=datastore).as_dataset()

    # Get full path of the cleansing scriot, folder name and script name
    feateng_src_dir_path, feateng_script_name = get_srcdir_and_filename(SOURCE_DIR, FEATENG_SCRIPT_PATH)

    # Feature engineering step creation
    # See the feateng.py for details about input and output
    feateng_step = PythonScriptStep(
        name="Creates new features",
        script_name=feateng_script_name,
        arguments=["--output_feateng", feateng_data],
        inputs=[cleansed_data.parse_delimited_files(file_extension=".csv")],
        outputs=[feateng_data],
        compute_target=aml_compute,
        runconfig=run_config,
        source_directory=feateng_src_dir_path,
        allow_reuse=True
    )

    print("Feat Engineering Step created.")

    # ****** Construct the Pipeline ****** #
    # Construct the pipeline
    pipeline_steps = [cleansing_step, feateng_step]
    train_pipeline = Pipeline(workspace=aml_workspace, steps=pipeline_steps)
    print("Pipeline is built.")

    # ******* Create an experiment and run the pipeline ********* #
    experiment = Experiment(workspace=aml_workspace, name='test-cln_feateng_pipe')
    pipeline_run = experiment.submit(train_pipeline, regenerate_outputs=True)
    print("Pipeline submitted for execution.")

    pipeline_run.wait_for_completion()


if __name__ == '__main__':
    main()


