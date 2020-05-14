from azureml.core.compute import ComputeTarget
from azureml.exceptions import ComputeTargetException


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
