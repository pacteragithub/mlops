from azureml.core import Run
import argparse
import traceback
from util.model_helper import get_latest_model

# Getting the run context
run = Run.get_context()

exp = run.experiment
ws = run.experiment.workspace
run_id = 'amlcompute'


# Giving a description of this file when invoked on command line like python clean.py -h
parser = argparse.ArgumentParser("evaluate")
parser.add_argument("--model_name", type=str, help="Name of the model", default="titanic_classifier_model.pkl")
parser.add_argument("--allow_run_cancel", type=str,
                    help="Set this to false to avoid evaluation step from cancelling run after an unsuccessful evaluation",  # NOQA: E501
                    default="true")

args = parser.parse_args()
if (args.run_id is not None):
    run_id = args.run_id
if (run_id == 'amlcompute'):
    run_id = run.parent.id
model_name = args.model_name
metric_eval = "accuracy"

allow_run_cancel = args.allow_run_cancel

try:
    firstRegistration = False
    tag_name = 'experiment_name'

    model = get_latest_model(
        model_name, tag_name, exp.name, ws)

    if (model is not None):
        production_model_metric = 0
        if (metric_eval in model.tags):
            production_model_metric = float(model.tags[metric_eval])
        new_model_metric = float(run.parent.get_metrics().get(metric_eval))
        if (production_model_metric is None or new_model_metric is None):
            print("Unable to find", metric_eval, "metrics, "
                  "exiting evaluation")
            if((allow_run_cancel).lower() == 'true'):
                run.parent.cancel()
        else:
            print(f"Current Production model {metric_eval} : production_model_metric"
                  f"New trained model {metric_eval}: {new_model_metric}")

        if (new_model_metric > production_model_metric):
            print("New trained model performs better, "
                  "thus it should be registered")
        else:
            print("New trained model metric is worse than or equal to "
                  "production model so skipping model registration.")
            if((allow_run_cancel).lower() == 'true'):
                run.parent.cancel()
    else:
        print("This is the first model, "
              "thus it should be registered")

except Exception:
    traceback.print_exc(limit=None, file=None, chain=True)
    print("Something went wrong trying to evaluate. Exiting.")
    raise
