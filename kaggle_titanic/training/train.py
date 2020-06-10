import argparse
import os
import json
import joblib
from azureml.core import Run
from training.train_helper import split_data, train_model, get_model_metrics

dummy1 = os.path.abspath(os.curdir)

print(f"Root directory is {dummy1}")
print(f"Listing files in root directory {os.listdir(dummy1)}")
print("Create new features")

# Giving a description of this file
# when invoked on command line like python clean.py -h
parser = argparse.ArgumentParser("model training")
parser.add_argument("--model_name",
                    type=str, help="Name of the model",
                    default="titanic_classifier_model.pkl")
parser.add_argument("--output_model",
                    type=str, help="Model Output directory")

# Parse the arguments
args = parser.parse_args()

print(f"Argument 1 (Name of the model):, {args.model_name}")
print(f"Argument 2 (Output Directory of model):, {args.output_model}")

# Output path of this step
model_name = args.model_name
step_output_path = args.output_model

# Load the training parameters from the parameters file
with open("parameters.json") as f:
    pars = json.load(f)
try:
    train_args = pars["training"]
except KeyError:
    print("Could not load training values from file")
    train_args = {}

# Get the run context
run = Run.get_context()

# Get the feature eng data
feateng_data = run.input_datasets["feateng_data"]
feateng_df = feateng_data.to_pandas_dataframe()

# Tagging details to the run
run.input_datasets["training_data"] = feateng_data
run.parent.tag("dataset_id", value=feateng_data.id)

# Split the data into train and test
X_cols = ['Passenger_Class', 'Sex', 'SibSp', 'Parch', 'Fare']
target_col = "Survived"
data = split_data(feateng_df, X_cols, target_col)

# Train the model
model = train_model(data, train_args)

# Evaluate and log the metrics returned from the train function
metrics = get_model_metrics(model, data)
for (k, v) in metrics.items():
    run.log(k, v)
    run.parent.log(k, v)

# Pass model file to next step
os.makedirs(step_output_path, exist_ok=True)
model_output_path = os.path.join(step_output_path, model_name)
joblib.dump(value=model, filename=model_output_path)

# Also upload model file to run outputs for history
os.makedirs('outputs', exist_ok=True)
output_path = os.path.join('outputs', model_name)
joblib.dump(value=model, filename=output_path)
