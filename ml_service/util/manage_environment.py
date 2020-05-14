from azureml.core import Environment
from environment_setup.env_variables import REQUIREMENTS_PATH


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