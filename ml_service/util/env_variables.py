import os
from dotenv import load_dotenv


class Singleton(object):
    _instances = {}

    def __new__(class_, *args, **kwargs):
        if class_ not in class_._instances:
            class_._instances[class_] = super(Singleton, class_).__new__(class_, *args, **kwargs)  # noqa E501
        return class_._instances[class_]


class Env(Singleton):

    def __init__(self):
        load_dotenv()

        # Project Directory variables
        self._sources_directory_train = os.environ.get("SOURCES_DIR_TRAIN")
        self._ingested_data_directory = os.environ.get("SAVE_INGESTED_DATA_DIR")
        self._ingested_data_filename = os.environ.get("SAVE_INGESTED_DATA_FILENAME")
        self._fresh_data_ingest = os.environ.get("FRESH_DATA_INGEST")

        # Model Output variables
        self._model_name = os.environ.get("MODEL_NAME")
        self._model_version = os.environ.get('MODEL_VERSION')

        # Model Training related variables
        self._train_script_path = os.environ.get("TRAIN_SCRIPT_PATH")
        self._evaluate_script_path = os.environ.get("EVALUATE_SCRIPT_PATH")
        self._register_script_path = os.environ.get("REGISTER_SCRIPT_PATH")

        # Datastore related information
        self._datastore_name = os.environ.get("DATASTORE_NAME")
        self._path_on_datastore = os.environ.get("PATH_ON_DATASTORE")
        self._dataset_name = os.environ.get("DATASET_NAME")
        self._dataset_version = os.environ.get("DATASET_VERSION")

        # Azure ML workspace variables
        self._workspace_name = os.environ.get("WORKSPACE_NAME")
        self._experiment_name = os.environ.get("EXPERIMENT_NAME")

        # Azure DevOps related
        self._resource_group = os.environ.get("RESOURCE_GROUP")
        self._subscription_id = os.environ.get("SUBSCRIPTION_ID")

        # self._build_id = os.environ.get("BUILD_BUILDID")
        # self._pipeline_name = os.environ.get("TRAINING_PIPELINE_NAME")
        # self._image_name = os.environ.get('IMAGE_NAME')
        # self._db_cluster_id = os.environ.get("DB_CLUSTER_ID")
        # self._score_script = os.environ.get("SCORE_SCRIPT")
        # self._build_uri = os.environ.get("BUILD_URI")
        # self._run_evaluation = os.environ.get("RUN_EVALUATION", "true")
        # self._allow_run_cancel = os.environ.get(
        #     "ALLOW_RUN_CANCEL", "true")
        # self._aml_env_name = os.environ.get("AML_ENV_NAME")
        # self._rebuild_env = os.environ.get("AML_REBUILD_ENVIRONMENT",
        #                                    "false").lower().strip() == "true"

    @property
    def workspace_name(self):
        return self._workspace_name

    @property
    def resource_group(self):
        return self._resource_group

    @property
    def subscription_id(self):
        return self._subscription_id

    # @property
    # def tenant_id(self):
    #     return self._tenant_id
    #
    # @property
    # def app_id(self):
    #     return self._app_id
    #
    # @property
    # def app_secret(self):
    #     return self._app_secret
    #
    # @property
    # def vm_size(self):
    #     return self._vm_size
    #
    # @property
    # def compute_name(self):
    #     return self._compute_name
    #
    # @property
    # def db_cluster_id(self):
    #     return self._db_cluster_id
    #
    # @property
    # def build_id(self):
    #     return self._build_id
    #
    # @property
    # def pipeline_name(self):
    #     return self._pipeline_name

    @property
    def sources_directory_train(self):
        return self._sources_directory_train

    @property
    def ingested_data_directory(self):
        return self._ingested_data_directory

    @property
    def ingested_data_filename(self):
        return self._ingested_data_filename
    @property
    def fresh_data_ingest(self):
        return self._fresh_data_ingest

    @property
    def train_script_path(self):
        return self._train_script_path

    @property
    def evaluate_script_path(self):
        return self._evaluate_script_path

    @property
    def register_script_path(self):
        return self._register_script_path

    @property
    def model_name(self):
        return self._model_name

    @property
    def experiment_name(self):
        return self._experiment_name

    # @property
    # def vm_priority(self):
    #     return self._vm_priority
    #
    # @property
    # def min_nodes(self):
    #     return self._min_nodes
    #
    # @property
    # def max_nodes(self):
    #     return self._max_nodes

    @property
    def model_version(self):
        return self._model_version
    #
    # @property
    # def image_name(self):
    #     return self._image_name

    # @property
    # def score_script(self):
    #     return self._score_script

    # @property
    # def build_uri(self):
    #     return self._build_uri
    #
    @property
    def dataset_name(self):
        return self._dataset_name

    @property
    def datastore_name(self):
        return self._datastore_name

    @property
    def path_on_datastore(self):
        return self._path_on_datastore

    @property
    def dataset_version(self):
        return self._dataset_version

    # @property
    # def run_evaluation(self):
    #     return self._run_evaluation
    #
    # @property
    # def allow_run_cancel(self):
    #     return self._allow_run_cancel
    #
    # @property
    # def aml_env_name(self):
    #     return self._aml_env_name
    #
    # @property
    # def rebuild_env(self):
    #     return self._rebuild_env