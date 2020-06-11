import numpy
import joblib
import os
import pandas as pd
from datetime import datetime
from azureml.core.model import Model
from inference_schema.schema_decorators \
    import input_schema, output_schema
from inference_schema.parameter_types.numpy_parameter_type \
    import NumpyParameterType
from azure.storage.blob import BlobServiceClient


def get_blob_client(now):
    # Connect to a blob service client
    blob_service_client = BlobServiceClient.\
        from_connection_string(os.getenv("CONNECTION_STRING"))

    # Instantiate a ContainerClient
    container_client = blob_service_client.\
        get_container_client(os.getenv("LOGS_CONTAINER"))

    # Check if the blob exists or not
    blob_list = container_client.list_blobs()
    check_blob_name = str(now.date()) + ".txt"

    blobExists = False
    blob_client = None

    for blob in blob_list:
        if blob.name == check_blob_name:
            blob_client = container_client.get_blob_client(check_blob_name)
            print(f"Blob already exists for today with name {check_blob_name}")
            # Set flag
            blobExists = True

    if not blobExists:
        print(f"Creating a new blob for today with name {check_blob_name}")
        blob_client = container_client.get_blob_client(check_blob_name)
        blob_client.create_append_blob()

    return blob_client


def prep_data_logging(data, result, timestamp):

    # Create dataframe
    tmp_df = pd.DataFrame(data)
    tmp_df.columns = ["col_" + str(colname) for colname in tmp_df.columns]

    # Adding predictions to list
    tmp_df["prediction"] = result.tolist()

    # Adding timestamp to list
    tmp_df["datetime"] = timestamp

    out_list = tmp_df.to_dict("records")

    return out_list


def init():
    # load the model from file into a global object
    global model

    # we assume that we have just one model
    # AZUREML_MODEL_DIR is an environment variable created during deployment.
    # It is the path to the model folder
    # (./azureml-models/$MODEL_NAME/$VERSION)

    model_path = Model.get_model_path(
        os.getenv("AZUREML_MODEL_DIR").split('/')[-2])

    model = joblib.load(model_path)


input_sample = numpy.array([[3, 0, 1, 0, 7.25],
                            [1, 1, 1, 0, 53.1]])
output_sample = numpy.array([0, 1])


# Inference_schema generates a schema for your web service
# It then creates an OpenAPI (Swagger) specification for the web service
# at http://<scoring_base_url>/swagger.json
@input_schema('data', NumpyParameterType(input_sample))
@output_schema(NumpyParameterType(output_sample))
def run(data, request_headers):
    result = model.predict(data)

    # Demonstrate how we can log custom data into the Application Insights
    # traces collection.
    # The 'X-Ms-Request-id' value is generated internally and can be used to
    # correlate a log entry with the Application Insights requests collection.
    # The HTTP 'traceparent' header may be set by the caller to implement
    # distributed tracing (per the W3C Trace Context proposed specification)
    # and can be used to correlate the request to external systems.
    print(('{{"RequestId":"{0}", '
           '"TraceParent":"{1}", '
           '"NumberOfPredictions":{2}}}'
           ).format(
               request_headers.get("X-Ms-Request-Id", ""),
               request_headers.get("Traceparent", ""),
               len(result)
    ))

    # Get today's date
    now = datetime.now()

    # Creates a log file for a day if doesn't exist
    blob_client = get_blob_client(now)

    # Get data in required format to be logged
    out_list = prep_data_logging(data, result,
                                 now.strftime("%Y-%m-%d_%H:%M:%S"))

    for item in out_list:
        blob_client.append_block(str(item))
        blob_client.append_block('\n')

    return {"result": result.tolist()}


if __name__ == "__main__":
    # Test scoring
    init()
    test_row = '{"data": [[3, 0, 1, 0, 7.25],[1, 1, 1, 0, 53.1]]}'
    prediction = run(test_row, {})
    print("Test result: ", prediction)
