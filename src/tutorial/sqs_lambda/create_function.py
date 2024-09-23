"""
Module to create a new AWS Lambda function local zip file.
"""

import os
import boto3
import random
import string
from dotenv import load_dotenv, set_key

def main():
    load_dotenv()

    function_name = "lambda_sqs_renatex"

    lambda_role_arn = os.getenv("AWS_LAMBDA_ROLE_ARN")

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
    zip_file_path = os.path.join(data_dir,"lambda_send_sqs.zip")
    with open(zip_file_path, "rb") as f:
        zip_to_deploy = f.read()

    response = lambda_client.create_function(
        FunctionName=function_name,
        Runtime="python3.9",
        Role=lambda_role_arn,
        Handler="lambda_send_sqs.lambda_handler",
        Code={"ZipFile": zip_to_deploy},
        Environment={
            "Variables": {
                "DESTINATION_SQS_URL": os.getenv("DESTINATION_SQS_URL"),
            }
        },
        Timeout=15,  # Optional: function timeout in seconds
    )

    print("Lambda Function Created Successfully!")
    print(f"Function Name: {response['FunctionName']}")
    print(f"Function ARN: {response['FunctionArn']}")
    set_key(".env", "\nFUNCTION_ARN", response["FunctionArn"])

if __name__ == "__main__":
    main()
