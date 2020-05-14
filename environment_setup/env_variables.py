import os
from os.path import join
from dotenv import load_dotenv

# Extracting the .env file path
dotenv_path = join(os.path.abspath(os.curdir), '.env')
load_dotenv()

# Requirements.txt path
REQUIREMENTS_PATH = join(os.path.abspath(os.curdir), 'requirements.txt')

# Folder related environment variables
SOURCES_DIR_TRAIN = os.environ.get('SOURCES_DIR_TRAIN')
SAVE_INGESTED_DATA_DIR = os.environ.get('SAVE_INGESTED_DATA_DIR')
FRESH_DATA_INGEST = os.environ.get('FRESH_DATA_INGEST')

# Datastore and dataset details
DATASTORE_NAME = os.environ.get('DATASTORE_NAME')
PATH_ON_DATASTORE = os.environ.get('PATH_ON_DATASTORE')
# DATASET_NAME = os.environ.get('DATASET_NAME')
# DATASET_VERSION = os.environ.get('DATASET_VERSION')
# CREATE_NEW_VERSION = os.environ.get('CREATE_NEW_VERSION')

# Azure ML Workspace Variables
WORKSPACE_NAME = os.environ.get('WORKSPACE_NAME')
EXPERIMENT_NAME = os.environ.get('EXPERIMENT_NAME')

# Azure compute related variables
COMPUTE_CLUSTER_NAME = os.environ.get('COMPUTE_CLUSTER_NAME')
AML_ENV_NAME = os.environ.get('AML_ENV_NAME')


# Model Training related variables
TRAIN_SCRIPT_PATH = os.environ.get('TRAIN_SCRIPT_PATH')
EVALUATE_SCRIPT_PATH = os.environ.get('EVALUATE_SCRIPT_PATH')
REGISTER_SCRIPT_PATH = os.environ.get('REGISTER_SCRIPT_PATH')

# Model Output Variables
MODEL_NAME = os.environ.get('MODEL_NAME')
MODEL_VERSION = os.environ.get('MODEL_VERSION')
