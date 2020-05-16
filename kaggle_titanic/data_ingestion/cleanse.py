import argparse
import os
import json
from azureml.core import Run, Dataset
from clean_helpers import rename_columns

dummy1 = os.path.abspath(os.curdir)

print(f"Root directory is {dummy1}")
print(f"Listing files in root directory {os.listdir(dummy1)}")
print("Cleans the raw data")

# Giving a description of this file when invoked on command line like python clean.py -h
parser = argparse.ArgumentParser("cleanse")
parser.add_argument("--dataset_name", type=str, help="name of the registered dataset")
parser.add_argument("--output_cleanse", type=str, help="cleaned data directory")

# Parse the arguments
args = parser.parse_args()

print(f"Argument 1 (Name of the registered dataset):, {args.dataset_name}")
print(f"Argument 2 (Cleaned Data path):, {args.output_cleanse}")

# Get the run context
run = Run.get_context()

# Read necessary parameters
dataset_name = args.dataset_name
step_output_path = args.output_cleanse

# Access the registered dataset
try:
    ds_meta = Dataset.get_by_name(run.experiment.workspace, dataset_name)

    # Link dataset to the step run so it is trackable in the UI
    run.input_datasets["raw_data"] = ds_meta
    run.parent.tag("dataset_id", value=ds_meta.id)

except Exception as e:
    print(e)
    exit(1)

# Access the pandas datafame
req_dataset = ds_meta.to_pandas_dataframe()

# Perform necessary cleaning
with open("col_mapping.json") as f:
    pars = json.load(f)

# pars = {"Pclass":"Passenger_Class"}

cleaned_df = rename_columns(req_dataset, pars)

# Pass output to next step
if not (step_output_path is None):
    os.makedirs(step_output_path, exist_ok=True)
    full_output_path = os.path.join(step_output_path, "cleaned.csv")
    write_df = cleaned_df.to_csv(full_output_path)
