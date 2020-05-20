from azureml.core import Run
from azureml.core import Workspace
from azureml.core.model import Model as AMLModel


def get_current_workspace() -> Workspace:
    """
    Retrieves and returns the latest model from the workspace
    by its name and tag. Will not work when ran locally.
    Parameters:
    None
    Return:
    The current workspace.
    """
    run = Run.get_context(allow_offline=False)
    experiment = run.experiment
    return experiment.workspace


def get_latest_model(model_name, tag_name=None, tag_value=None, aml_workspace=None):
    """
    Function to fetch the latest available model in the workspace
    """
    try:
        # Validate params. cannot be None.
        if model_name is None:
            raise ValueError("model_name[:str] is required")

        if aml_workspace is None:
            print("No workspace defined - using current experiment workspace.")
            aml_workspace = get_current_workspace()

        model_list = None
        tag_ext = ""

        # Get latest model
        # True: by name and tags
        if tag_name is not None and tag_value is not None:
            model_list = AMLModel.list(
                aml_workspace, name=model_name,
                tags=[[tag_name, tag_value]], latest=True
            )
            tag_ext = f"tag_name: {tag_name}, tag_value: {tag_value}."
        # False: Only by name
        else:
            model_list = AMLModel.list(
                aml_workspace, name=model_name, latest=True)

        # latest should only return 1 model, but if it does,
        # then maybe sdk or source code changed.

        # define the error messages
        too_many_model_message = ("Found more than one latest model. "
                                  f"Models found: {model_list}. "
                                  f"{tag_ext}")

        no_model_found_message = (f"No Model found with name: {model_name}. "
                                  f"{tag_ext}")

        if len(model_list) > 1:
            raise ValueError(too_many_model_message)
        if len(model_list) == 1:
            return model_list[0]
        else:
            print(no_model_found_message)
            return None
    except Exception:
        raise
