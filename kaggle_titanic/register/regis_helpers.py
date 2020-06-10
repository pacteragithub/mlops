import os
import traceback
from azureml.core import Dataset
from azureml.core.model import Model as AMLModel


def model_already_registered(model_name, exp, run_id):
    model_list = AMLModel.list(exp.workspace, name=model_name, run_id=run_id)
    if len(model_list) >= 1:
        e = ("Model name:", model_name, "in workspace",
             exp.workspace, "with run_id ", run_id, "is already registered.")
        print(e)
        raise Exception(e)
    else:
        print("Model is not registered for this run.")


def register_aml_model(model_path, model_name, model_tags,
                       exp, run_id, dataset_id,
                       build_id: str = 'none', build_uri=None):
    try:
        tagsValue = {"area": "kaggle_titanic",
                     "run_id": run_id,
                     "experiment_name": exp.name}
        tagsValue.update(model_tags)

        if (build_id != 'none'):
            model_already_registered(model_name, exp, run_id)
            tagsValue["BuildId"] = build_id
            if (build_uri is not None):
                tagsValue["BuildUri"] = build_uri

        model = AMLModel.register(
            workspace=exp.workspace,
            model_name=model_name,
            model_path=model_path,
            tags=tagsValue,
            datasets=[('training data',
                       Dataset.get_by_id(exp.workspace, dataset_id))])
        os.chdir("..")
        print(
            "Model registered: {} \nModel Description: {} "
            "\nModel Version: {}".format(
                model.name, model.description, model.version
            )
        )
    except Exception:
        traceback.print_exc(limit=None, file=None, chain=True)
        print("Model registration failed")
        raise
