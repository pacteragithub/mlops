# Environment related utilities
import os
from environment_setup.env_variables import SOURCE_DIR, \
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

    # cleansing step creation
    # See the cleanse.py for details about input and output
    cleansing_step = PythonScriptStep(
        name="Cleanse Raw Data",
        script_name=CLEANSE_SCRIPT_PATH,
        arguments=["--dataset_name", dataset_name_param,
                   "--output_cleanse", cleansed_data],
        outputs=[cleansed_data],
        compute_target=aml_compute,
        runconfig=run_config,
        source_directory=SOURCE_DIR,
        allow_reuse=True
    )

    print("cleansingStep created.")

    # ****** Construct the Pipeline ****** #
    # Construct the pipeline
    pipeline_steps = [cleansing_step]
    train_pipeline = Pipeline(workspace=aml_workspace, steps=pipeline_steps)
    print("Pipeline is built.")

    # ******* Create an experiment and run the pipeline ********* #
    experiment = Experiment(workspace=aml_workspace, name='test-cleansing-pipeline')
    pipeline_run = experiment.submit(train_pipeline, regenerate_outputs=False)
    print("Pipeline submitted for execution.")

    pipeline_run.wait_for_completion()


if __name__ == '__main__':
    main()


