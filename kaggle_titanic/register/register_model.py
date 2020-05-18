import json
import os
import sys
import argparse
import joblib
from azureml.core import Run
from register.regis_helpers import register_aml_model

run = Run.get_context()

ws = run.experiment.workspace
exp = run.experiment
run_id = 'amlcompute'

parser = argparse.ArgumentParser("register")
parser.add_argument("--run_id", type=str, help="Training run ID",)
parser.add_argument("--model_name",type=str, help="Name of the Model", default="titanic_classifier_model.pkl",)
parser.add_argument("--output_model", type=str, help="Model directory location")

args = parser.parse_args()
if (args.run_id is not None):
    run_id = args.run_id
if (run_id == 'amlcompute'):
    run_id = run.parent.id
model_name = args.model_name
model_path = args.output_model

print("Getting registration parameters")

# Load the registration parameters from the parameters file
with open("parameters.json") as f:
    pars = json.load(f)
try:
    register_args = pars["registration"]
except KeyError:
    print("Could not load registration values from file")
    register_args = {"tags": []}

model_tags = {}
for tag in register_args["tags"]:
    try:
        mtag = run.parent.get_metrics()[tag]
        model_tags[tag] = mtag
    except KeyError:
        print(f"Could not find {tag} metric on parent run.")

# load the model
print("Loading model from " + model_path)
model_file = os.path.join(model_path, model_name)
model = joblib.load(model_file)
parent_tags = run.parent.get_tags()

print(parent_tags)

try:
    build_id = parent_tags["BuildId"]
except KeyError:
    build_id = None
    print("BuildId tag not found on parent run.")
    print(f"Tags present: {parent_tags}")
try:
    build_uri = parent_tags["BuildUri"]
except KeyError:
    build_uri = None
    print("BuildUri tag not found on parent run.")
    print(f"Tags present: {parent_tags}")

if (model is not None):
        dataset_id = parent_tags["dataset_id"]
        if (build_id is None):
            register_aml_model(model_file, model_name, model_tags, exp, run_id, dataset_id)
        elif (build_uri is None):
            register_aml_model(model_file, model_name, model_tags, exp, run_id, dataset_id, build_id)
        else:
            register_aml_model(model_file, model_name, model_tags, exp, run_id, dataset_id, build_id, build_uri)
else:
    print("Model not found. Skipping model registration.")
    sys.exit(0)
