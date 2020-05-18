import argparse
import os
from azureml.core import Run
from feat_create import create_new_features

dummy1 = os.path.abspath(os.curdir)

print(f"Root directory is {dummy1}")
print(f"Listing files in root directory {os.listdir(dummy1)}")
print("Create new features")

# Giving a description of this file when invoked on command line like python clean.py -h
parser = argparse.ArgumentParser("feature creation")
parser.add_argument("--output_feateng", type=str, help="feat eng data directory")

# Parse the arguments
args = parser.parse_args()

print(f"Argument 1 (Feat Eng Data path):, {args.output_feateng}")

# Output path of this step
step_output_path = args.output_feateng

# Get the run context
run = Run.get_context()

# Get the cleansed data
cleansed_data = run.input_datasets["cleansed_data"]
cleansed_df = cleansed_data.to_pandas_dataframe()

# Call the function to create features
feateng_df = create_new_features(cleansed_df)

# Pass output to next step
if not (step_output_path is None):
    os.makedirs(step_output_path, exist_ok=True)
    full_output_path = os.path.join(step_output_path, "feateng_data.csv")
    write_df = feateng_df.to_csv(full_output_path)
