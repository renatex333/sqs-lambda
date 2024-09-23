import os
import boto3
from dotenv import load_dotenv, set_key

def main():

    load_dotenv()

    function_name = "read_write_sqs_renatex"

    queue_name = "lambda_origin_queue_renatex"

    # Destination queue URL
    environment_variables = {
        "DESTINATION_SQS_URL": os.getenv("DESTINATION_SQS_URL"),
    }

    # Timeout in seconds. Default is 3.
    timeout = 15

    # Lambda basic execution role
    lambda_role_arn = os.getenv("AWS_LAMBDA_ROLE_ARN")

    # Create a Boto3 client for AWS Lambda
    lambda_client = boto3.client(
        "lambda",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    try:
        lambda_client.delete_function(FunctionName=function_name)
        print("Existing Function was Deleted!")
    except lambda_client.exceptions.ResourceNotFoundException:
        pass

    # Read the contents of the zip file that you want to deploy
    data_dir = os.path.relpath("data", os.getcwd())
    zip_file_path = os.path.join(data_dir,"read_write.zip")
    with open(zip_file_path, "rb") as f:
        zip_to_deploy = f.read()

    lambda_response = lambda_client.create_function(
        FunctionName=function_name,
        Runtime="python3.10",
        Role=lambda_role_arn,
        Handler="read_write.lambda_handler",
        Code={"ZipFile": zip_to_deploy},
        Timeout=timeout,
        Environment={"Variables": environment_variables},
    )

    function_arn = lambda_response["FunctionArn"]

    print(f"Function Name: {lambda_response['FunctionName']}")
    print(f"Function ARN: {function_arn}")
    set_key(".env", "\nORIGIN_FUNCTION_ARN", function_arn)

    event_source_arn = (
        f'arn:aws:sqs:{os.getenv("AWS_REGION")}:{os.getenv("AWS_ACCOUNT_ID")}:{queue_name}'
    )

    # Configure the function's event source mapping with the SQS queue

    try:
        lambda_client.delete_event_source_mapping(UUID=os.getenv("EVENT_SOURCE_MAPPING_UUID"))
        print("Existing Mapping was Deleted!")
    except lambda_client.exceptions.ResourceNotFoundException:
        print("Mapping not found.")

    response = lambda_client.create_event_source_mapping(
        EventSourceArn=event_source_arn,
        FunctionName=function_arn,
        BatchSize=2,  # Number of messages to retrieve per batch (optional)
    )

    print("Lambda function created and configured with SQS event source mapping.")
    set_key(".env", "\nEVENT_SOURCE_MAPPING_UUID", response["UUID"])

if __name__ == "__main__":
    main()
