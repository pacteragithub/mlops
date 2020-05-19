# Environment related utilities
import os
from ml_service.util.env_variables import Env

# Azure ML related packages
from azureml.core import Datastore, Experiment
from azureml.core.runconfig import RunConfiguration
from azureml.pipeline.core.graph import PipelineParameter
from azureml.pipeline.steps import PythonScriptStep
from azureml.pipeline.core import Pipeline, PipelineData

# Data Related
from kaggle_titanic.data_ingestion.dataprep import data_preparation

# Fetch compute and other params
from ml_service.util.aml_helpers import get_workspace, get_compute, get_environment
from ml_service.util.ds_registration_helpers import create_and_register_datasets

# other utilities
from distutils.util import strtobool
from datetime import datetime


def main():

    # Loading environment variable object
    e = Env()

    # SPN credentials needed to authenticate
    spn_credentials = {
        'tenant_id': e.tenant_id,
        'service_principal_id': e.app_id,
        'service_principal_password': e.app_secret,
    }

    # ******** Connect to Workspace, Setup Compute and Environment****** #
    aml_workspace = get_workspace(e.workspace_name, e.subscription_id, e.resource_group, spn_credentials)
    aml_compute = get_compute(aml_workspace, e.compute_name)
    environment = get_environment(aml_workspace, e.aml_env_name, "requirements.txt",
                                  create_new=strtobool(e.rebuild_env))

    # Setting run configuration
    run_config = RunConfiguration()
    run_config.environment = environment

    # ******** Assign datastore to save and register datasets ********** #
    if (e.datastore_name): # if valid name assign it
        datastore_name = e.datastore_name
    else: # get the default datastore tagged to the workspace
        datastore_name = aml_workspace.get_default_datastore().name

    run_config.environment.environment_variables["DATASTORE_NAME"] = datastore_name

    # ******** Creating and Registering Datasets *********************** #
    # Make a connection to the datastore
    datastore = Datastore.get(aml_workspace, datastore_name)

    # Pull Data from SQL or CSV and save it to local
    # dict_dfs is a dictionary with key value pairs {"dataset_name":DataFrame}
    dict_dfs = data_preparation()

    # SubFolder name on datastore would be created as per datetime
    # sub_folder_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    # folderpath_on_dstore = os.path.join(PATH_ON_DATASTORE, sub_folder_name, "")
    folderpath_on_dstore = os.path.join(e.path_on_datastore, "")

    try:
        create_and_register_datasets(aml_workspace, datastore_name, dict_dfs, strtobool(e.fresh_data_ingest),
                                     e.ingested_data_directory, folderpath_on_dstore)
    except Exception as e:
        print(str(e))

    # Parameters needed for this pipeline
    model_name_param = PipelineParameter(name="model_name", default_value=e.model_name)

    # Other variables used in the pipeline
    # src_directory_path = os.path.join(ROOT_DIR, SOURCE_DIR)

    # **************** Data Cleansing Step************************** #
    # Define parameters required for the step
    dataset_name_param = "passenger_data"

    # Define output after cleansing step
    cleansed_data = PipelineData('cleansed_data', datastore=datastore).as_dataset()

    # cleansing step creation
    # See the cleanse.py for details about input and output
    cleansing_step = PythonScriptStep(
        name="Cleanse Raw Data",
        script_name=e.cleanse_script_path,
        arguments=["--dataset_name", dataset_name_param,
                   "--output_cleanse", cleansed_data],
        outputs=[cleansed_data],
        compute_target=aml_compute,
        runconfig=run_config,
        source_directory=e.sources_directory_train,
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
        script_name=e.feateng_script_path,
        arguments=["--output_feateng", feateng_data],
        inputs=[cleansed_data.parse_delimited_files(file_extension=".csv")],
        outputs=[feateng_data],
        compute_target=aml_compute,
        runconfig=run_config,
        source_directory=e.sources_directory_train,
        allow_reuse=True
    )

    print("Feat Engineering Step created.")

    # **************** Model Training Step************************** #
    # Define output after cleansing step
    model_output = PipelineData('model_output', datastore=datastore)

    # See the train.py for details about input and outpu
    train_step = PythonScriptStep(
        name="Train Model",
        script_name=e.train_script_path,
        arguments=[
            "--model_name", model_name_param,
            "--output_model", model_output],
        inputs=[feateng_data.parse_delimited_files(file_extension=".csv")],
        outputs=[model_output],
        compute_target=aml_compute,
        runconfig=run_config,
        source_directory=e.sources_directory_train,
        allow_reuse=True
    )

    print("Model Training Step created.")

    # **************** Model Evaluation Step************************** #
    evaluate_step = PythonScriptStep(
        name="Evaluate Model ",
        script_name=e.evaluate_script_path,
        compute_target=aml_compute,
        source_directory=e.sources_directory_train,
        arguments=[
            "--model_name", model_name_param,
            "--allow_run_cancel", e.allow_run_cancel,
        ],
        runconfig=run_config,
        allow_reuse=False,
    )
    print("Model Evaluation Step created")

    # **************** Model Registration Step************************** #
    register_step = PythonScriptStep(
        name="Register Model ",
        script_name=e.register_script_path,
        compute_target=aml_compute,
        source_directory=e.sources_directory_train,
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
    if strtobool(e.run_evaluation):
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
        name=e.pipeline_name,
        description="Model training/retraining pipeline",
        version=e.build_id
    )
    print(f'Published pipeline: {published_pipeline.name}')
    print(f'for build {published_pipeline.version}')


if __name__ == '__main__':
    main()