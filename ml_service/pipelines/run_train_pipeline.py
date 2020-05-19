from azureml.pipeline.core import PublishedPipeline
from azureml.core import Experiment
import argparse
from ml_service.util.aml_helpers import get_workspace
from environment_setup.env_variables import TRAINING_PIPELINE_NAME, EXPERIMENT_NAME,\
    BUILD_ID, BUILD_URI, MODEL_NAME


def main():

    parser = argparse.ArgumentParser("register")
    parser.add_argument(
        "--output_pipeline_id_file",
        type=str,
        default="pipeline_id.txt",
        help="Name of a file to write pipeline ID to"
    )
    parser.add_argument(
        "--skip_train_execution",
        action="store_true",
        help=("Do not trigger the execution. "
              "Use this in Azure DevOps when using a server job to trigger")
    )
    args = parser.parse_args()

    # ******** Connect to Workspace****** #
    aml_workspace = get_workspace()

    # Find the pipeline that was published by the specified build ID
    pipelines = PublishedPipeline.list(aml_workspace)
    matched_pipes = []

    for p in pipelines:
        if p.name == TRAINING_PIPELINE_NAME:
            if p.version == BUILD_ID:
                matched_pipes.append(p)

    if len(matched_pipes) > 1:
        published_pipeline = None
        raise Exception(f"Multiple active pipelines are published for build {BUILD_ID}.")  # NOQA: E501
    elif len(matched_pipes) == 0:
        published_pipeline = None
        raise KeyError(f"Unable to find a published pipeline for this build {BUILD_ID}")  # NOQA: E501
    else:
        published_pipeline = matched_pipes[0]
        print("published pipeline id is", published_pipeline.id)

        # Save the Pipeline ID for other AzDO jobs after script is complete
        if args.output_pipeline_id_file is not None:
            with open(args.output_pipeline_id_file, "w") as out_file:
                out_file.write(published_pipeline.id)

        if args.skip_train_execution is False:
            pipeline_parameters = {"model_name": MODEL_NAME}
            tags = {"BuildId": BUILD_ID}
            if BUILD_URI is not None:
                tags["BuildUri"] = BUILD_URI
            experiment = Experiment(
                workspace=aml_workspace,
                name=EXPERIMENT_NAME)
            run = experiment.submit(
                published_pipeline,
                tags=tags,
                pipeline_parameters=pipeline_parameters)

            print("Pipeline run initiated ", run.id)


if __name__ == "__main__":
    main()