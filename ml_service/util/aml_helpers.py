# Import User controlled enviroment variables
import os
from environment_setup.env_variables import AML_WORKSPACE_NAME, COMPUTE_CLUSTER_NAME,\
    AML_ENV_NAME, AML_REBUILD_ENVIRONMENT, REQUIREMENTS_PATH

# Azure ml related
from azureml.core.compute import ComputeTarget
from azureml.exceptions import ComputeTargetException
from azureml.core import Environment, Workspace
from azureml.core.authentication import ServicePrincipalAuthentication

# Other utilities
from ast import literal_eval


def get_compute(workspace, compute_name):
    """
    Function which returns a compute object which can used for pipeline execution
    workspace (Workspace)   : AML Workspace object
    compute_name (str)      : name of the compute target in the workspace
    return                  : Compute object
    """
    # Initializing a None value
    aml_compute = None

    try:
        aml_compute = ComputeTarget(workspace=workspace, name=compute_name)
        print(f"Found existing AML compute target {compute_name} and using it")
    except ComputeTargetException as e:
        print(e)
        exit(1)

    return aml_compute


def get_environment(workspace, environment_name, create_new=False):
    """
    Function which returns the environment object which can be attached to run context
    workspace (Workspace)   : AML workspace object
    environment_name (str)  : name of the environment
    return                  : environment object
    """
    # File path of requirement.txt
    requirements_path = REQUIREMENTS_PATH

    try:
        environments = Environment.list(workspace=workspace)
        restored_environment = None
        for env in environments:
            if env == environment_name:
                restored_environment = environments[environment_name]

        if restored_environment is None or create_new:
            new_env = Environment.from_pip_requirements(environment_name, requirements_path)
            restored_environment = new_env
            restored_environment.register(workspace)

        if restored_environment is not None:
            print(restored_environment)
        return restored_environment
    except Exception as e:
        print(e)
        exit(1)


def get_workspace_compute_env():
    """
    Function to connect to workspace, get compute and register environment needed for AML
    """

    # Intialize everything to none
    aml_workspace = None; aml_compute = None; environment = None

    # Loading user controlled environment variables
    workspace_name = AML_WORKSPACE_NAME                     # User controlled in .env file
    subscription_id = os.environ.get('SUBSCRIPTION_ID')     # Loaded by DevOps
    resource_group = os.environ.get('RESOURCE_GROUP')       # Loaded by DevOps

    # Service Principal Authentication
    spn_credentials = {
        'tenant_id': os.environ['TENANT_ID'],
        'service_principal_id': os.environ['SPN_ID'],
        'service_principal_password': os.environ['SPN_PASSWORD'],
    }

    # Connect to AML workspace using credentials
    aml_workspace = Workspace.get(
        name=workspace_name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        auth=ServicePrincipalAuthentication(**spn_credentials)
    )
    print("get_workspace:")
    print(aml_workspace)

    # Get aml compute
    aml_compute = get_compute(workspace=aml_workspace,
                              compute_name=COMPUTE_CLUSTER_NAME)

    # Create a reusable ML environment
    environment = get_environment(
        aml_workspace, AML_ENV_NAME , create_new= literal_eval(AML_REBUILD_ENVIRONMENT))

    return aml_workspace, aml_compute, environment