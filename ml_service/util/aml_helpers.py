from azureml.core.compute import ComputeTarget
from azureml.exceptions import ComputeTargetException
from azureml.core import Environment, Workspace
from azureml.core.authentication import ServicePrincipalAuthentication


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


def get_environment(workspace, environment_name, requirements_path, create_new=False):
    """
    Function which returns the environment object which can be attached to run context
    workspace (Workspace)   : AML workspace object
    environment_name (str)  : name of the environment
    return                  : environment object
    """

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


def get_workspace(workspace_name, subscription_id, resource_group, spn_credentials):

    # Connect to AML workspace using credentials
    aml_workspace = Workspace.get(
        name=workspace_name,
        subscription_id=subscription_id,
        resource_group=resource_group,
        auth=ServicePrincipalAuthentication(**spn_credentials)
    )

    print("get_workspace:")
    print(aml_workspace)

    return aml_workspace
