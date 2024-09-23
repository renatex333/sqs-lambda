"""
AWS Lambda Function Tutorial to list all Lambda functions in your AWS account
"""

import os
import boto3
from dotenv import load_dotenv

def main():
    load_dotenv()

    # Create a Boto3 client for AWS Lambda
    lambda_client = boto3.client(
        "lambda",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )


    # Call the list_functions API to retrieve all Lambda functions
    response = lambda_client.list_functions(MaxItems=1000)

    # Extract the list of Lambda functions from the response
    functions = response["Functions"]

    print(f"You have {len(functions)} Lambda functions")


    # Print the name of each Lambda function
    if len(functions) > 0:
        print("Here are their names:")

    for function in functions:
        function_name = function["FunctionName"]
        print(function_name)

if __name__ == "__main__":
    main()
