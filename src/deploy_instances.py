"""
Module to:

- Create a new AWS Lambda function from ECR image
- Create a new SQS queue to be used as a source of events for the Lambda function
- Create a new SQS queue to be used as a destination to store the results of the Lambda function 
"""

import os
import sys
import time
import boto3
import botocore
from dotenv import load_dotenv, set_key, unset_key

def create_new_queue(sqs_client, queue_name: str, case: str):
    load_dotenv()
    key_name = f"{case.upper()}_SQS_URL"
    try:
        sqs_client.delete_queue(QueueUrl=os.getenv(key_name))
        print(f"Existing {case} queue was deleted!")
        unset_key(".env", key_name)
    except (sqs_client.exceptions.QueueDoesNotExist, botocore.exceptions.ParamValidationError):
        print(f"{case.capitalize()} queue does not exist!")
    
    try:
        print(f"Creating brand new {case} queue...")
        response = sqs_client.create_queue(
            QueueName=f"{queue_name}_{case}",
            Attributes={
                "DelaySeconds": "0",
                "MessageRetentionPeriod": "3600",
            },
        )
        queue_url = response["QueueUrl"]
        print(f"{case.capitalize()} queue created with URL:", queue_url)
        set_key(".env", f"\n{key_name}", queue_url)
        time.sleep(5)
    except sqs_client.exceptions.QueueDeletedRecently:
        for s in range(65, -1, -1):
            time.sleep(1)
            print(f"Waiting {s} seconds for the deletion of {case} queue...", end="\r")
        print()
        create_new_queue(sqs_client, queue_name, case)
        return

def create_new_lambda(lambda_client, function_name: str):
    load_dotenv()
    image_uri = f"{os.getenv('REPOSITORY_URI')}:latest"
    lambda_role_arn = os.getenv("AWS_LAMBDA_ROLE_ARN")
    try:
        lambda_client.delete_function(FunctionName=function_name)
        print("Existing Function was Deleted!")
        unset_key(".env", "FUNCTION_NAME")
        unset_key(".env", "FUNCTION_ARN")
    except (lambda_client.exceptions.ResourceNotFoundException, botocore.exceptions.ParamValidationError):
        print("Function does not exist!")
    
    response = lambda_client.create_function(
        FunctionName=function_name,
        PackageType="Image",
        Code={"ImageUri": image_uri},
        Role=lambda_role_arn,
        Environment={
            "Variables": {
                "DESTINATION_SQS_URL": os.getenv("DESTINATION_SQS_URL"),
            }
        },
        Timeout=30,
        MemorySize=128,
    )
    function_arn = response["FunctionArn"]
    print(f"Function {function_name} created with ARN:", function_arn)
    set_key(".env", "\nFUNCTION_NAME", function_name)
    set_key(".env", "\nFUNCTION_ARN", function_arn)
    time.sleep(5)

def create_new_event_source_mapping(lambda_client):
    load_dotenv()
    queue_name = os.getenv("ORIGIN_SQS_URL").split("/")[-1]
    event_source_arn = (
        f'arn:aws:sqs:{os.getenv("AWS_REGION")}:{os.getenv("AWS_ACCOUNT_ID")}:{queue_name}'
    )
    function_arn = os.getenv("FUNCTION_ARN")
    try:
        lambda_client.delete_event_source_mapping(UUID=os.getenv("EVENT_SOURCE_MAPPING_UUID"))
        print("Existing Event Source Mapping was Deleted!")
        unset_key(".env", "EVENT_SOURCE_MAPPING_UUID")
    except (lambda_client.exceptions.ResourceNotFoundException, botocore.exceptions.ParamValidationError):
        print("Event Source Mapping not found.")

    try:
        print("Configuring Lambda function with SQS event source mapping...")
        response = lambda_client.create_event_source_mapping(
            EventSourceArn=event_source_arn,
            FunctionName=function_arn,
            BatchSize=1,  # Number of messages to retrieve per batch (optional)
        )
        print("Lambda function configured with SQS event source mapping.")
        set_key(".env", "\nEVENT_SOURCE_MAPPING_UUID", response["UUID"])
    except lambda_client.exceptions.InvalidParameterValueException:
        print("Error: Invalid parameter value!")
        print("Event Source Mapping not created.")

def main(queue_name: str, function_name: str):
    load_dotenv()

    sqs_client = boto3.client(
        "sqs",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    for case in ["origin", "destination"]:
        create_new_queue(sqs_client, queue_name, case)

    lambda_client = boto3.client(
        "lambda",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    create_new_lambda(lambda_client, function_name)
    create_new_event_source_mapping(lambda_client)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python deploy_instances.py <queue_name> <function_name>")
        sys.exit(1)
