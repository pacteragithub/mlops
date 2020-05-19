# Environment related utilities
import os
from environment_setup.env_variables import ROOT_DIR, SOURCE_DIR, \
    DATASTORE_NAME, FRESH_DATA_INGEST, SAVE_INGESTED_DATA_DIR, PATH_ON_DATASTORE,\
    CLEANSE_SCRIPT_PATH, FEATENG_SCRIPT_PATH,\
    TRAIN_SCRIPT_PATH, MODEL_NAME, EVALUATE_SCRIPT_PATH, REGISTER_SCRIPT_PATH,\
    ALLOW_RUN_CANCEL, RUN_EVALUATION, TRAINING_PIPELINE_NAME, BUILD_ID

# Azure ML related packages
from azureml.core import Datastore, Experiment
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, PipelineData

# Data Related
from kaggle_titanic.data_ingestion.dataprep import data_preparation

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
    # sub_folder_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    # folderpath_on_dstore = os.path.join(PATH_ON_DATASTORE, sub_folder_name, "")
    folderpath_on_dstore = os.path.join(PATH_ON_DATASTORE, "")

    try:
        create_and_register_datasets(aml_workspace, datastore_name, dict_dfs, literal_eval(FRESH_DATA_INGEST),
                                     SAVE_INGESTED_DATA_DIR, folderpath_on_dstore)
    except Exception as e:
        print(str(e))

    # Parameters needed for this pipeline
    model_name_param = PipelineParameter(name="model_name", default_value=MODEL_NAME)

    # Other variables used in the pipeline
    src_directory_path = os.path.join(ROOT_DIR, SOURCE_DIR)

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
        source_directory=src_directory_path,
        allow_reuse=True
    )

    print("Data Cleansing Step created.")

    # **************** Feature Engineering Step************************** #
    # Define output after Feature Engineering step
    feateng_data = PipelineData('feateng_data', datastore=datastore).as_dataset()

    # Feature engineering step creation
    # See the feateng.py for details about input and output
    feateng_step = PythonScriptStep(
        name="Feature Engineering",
        script_name=FEATENG_SCRIPT_PATH,
        arguments=["--output_feateng", feateng_data],
        inputs=[cleansed_data.parse_delimited_files(file_extension=".csv")],
        outputs=[feateng_data],
        compute_target=aml_compute,
        runconfig=run_config,
        source_directory=src_directory_path,
        allow_reuse=True
    )

    print("Feat Engineering Step created.")

    # **************** Model Training Step************************** #
    # Define output after cleansing step
    model_output = PipelineData('model_output', datastore=datastore)

    # See the train.py for details about input and outpu
    train_step = PythonScriptStep(
        name="Train Model",
        script_name=TRAIN_SCRIPT_PATH,
        arguments=[
            "--model_name", model_name_param,
            "--output_model", model_output],
        inputs=[feateng_data.parse_delimited_files(file_extension=".csv")],
        outputs=[model_output],
        compute_target=aml_compute,
        runconfig=run_config,
        source_directory=src_directory_path,
        allow_reuse=True
    )

    print("Model Training Step created.")

    # **************** Model Evaluation Step************************** #
    evaluate_step = PythonScriptStep(
        name="Evaluate Model ",
        script_name=EVALUATE_SCRIPT_PATH,
        compute_target=aml_compute,
        source_directory=src_directory_path,
        arguments=[
            "--model_name", model_name_param,
            "--allow_run_cancel", ALLOW_RUN_CANCEL,
        ],
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Model Evaluation Step created")

    # **************** Model Registration Step************************** #
    register_step = PythonScriptStep(
        name="Register Model ",
        script_name=REGISTER_SCRIPT_PATH,
        compute_target=aml_compute,
        source_directory=src_directory_path,
        inputs=[model_output],
        arguments=[
            "--model_name", model_name_param,
            "--output_model", model_output,
        ],
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Model Registration Step created")

    # Check run_evaluation flag to include or exclude evaluation step.
    if literal_eval(RUN_EVALUATION):
        print("Include evaluation step before register step.")
        evaluate_step.run_after(train_step)
        register_step.run_after(evaluate_step)
        steps = [cleansing_step, feateng_step, train_step, evaluate_step, register_step]
    else:
        print("Exclude evaluation step and directly run register step.")
        register_step.run_after(train_step)
        steps = [cleansing_step, feateng_step, train_step, register_step]

    # ******************* Construct & Publish the Pipeline ************************ #
    # Construct the pipeline
    train_pipeline = Pipeline(workspace=aml_workspace, steps=steps)
    print("Pipeline is built.")

    train_pipeline._set_experiment_name
    train_pipeline.validate()
    published_pipeline = train_pipeline.publish(
        name= TRAINING_PIPELINE_NAME,
        description="Model training/retraining pipeline",
        version=BUILD_ID
    )
    print(f'Published pipeline: {published_pipeline.name}')
    print(f'for build {published_pipeline.version}')


if __name__ == '__main__':
    main()


