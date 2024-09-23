"""
Module to delete the instances created by deploy_instances.py
"""

import os
import boto3
import botocore
from dotenv import load_dotenv, unset_key

def delete_event_source_mapping(lambda_client, uuid: str):
    """
    Delete the Lambda Event Source Mapping
    """
    try:
        lambda_client.delete_event_source_mapping(UUID=uuid)
        print("Event Source Mapping deleted:", uuid)
    except lambda_client.exceptions.ResourceNotFoundException:
        print("Event Source Mapping does not exist!")
    except botocore.exceptions.ParamValidationError:
        print(f"Event Source Mapping UUID ('{uuid}') is invalid!")

def delete_queue(sqs_client, queue_url: str):
    """
    Delete the SQS queue
    """
    try:
        sqs_client.delete_queue(QueueUrl=queue_url)
        print("Queue deleted:", queue_url)
    except sqs_client.exceptions.QueueDoesNotExist:
        print("Queue does not exist!")
    except botocore.exceptions.ParamValidationError:
        print(f"Queue URL ('{queue_url}') is invalid!")

def delete_lambda(lambda_client, function_name: str):
    """
    Delete the Lambda function
    """
    try:
        lambda_client.delete_function(FunctionName=function_name)
        print("Function deleted:", function_name)
    except lambda_client.exceptions.ResourceNotFoundException:
        print("Function does not exist!")
    except botocore.exceptions.ParamValidationError:
        print(f"Function name ('{function_name}') is invalid!")

def delete_instances():
    """
    Delete the instances created by deploy_instances.py
    """
    load_dotenv()

    # Initialize the clients
    sqs_client = boto3.client(
        "sqs",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    lambda_client = boto3.client(
        "lambda",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    # Delete the Event Source Mapping
    delete_event_source_mapping(lambda_client, os.getenv("EVENT_SOURCE_MAPPING_UUID"))

    # Delete the SQS queues
    for case in ["ORIGIN", "DESTINATION"]:
        key = f"{case}_SQS_URL"
        delete_queue(sqs_client, os.getenv(key))
        unset_key(".env", key)

    # Delete the Lambda function
    delete_lambda(lambda_client, os.getenv("FUNCTION_NAME"))
    unset_key(".env", "FUNCTION_NAME")
    unset_key(".env", "FUNCTION_ARN")

if __name__ == "__main__":
    delete_instances()
