import os
import json
import boto3
from dotenv import load_dotenv

def main():
    load_dotenv()

    # Lambda function name: do_something_concurrent_<YOUR_INSPER_USERNAME>
    function_name = "do_something_concurrent_renatex"

    # Number of concurrent executions: 2
    concurrent_executions_limit = 2

    # Create a Boto3 client for AWS Lambda
    lambda_client = boto3.client(
        "lambda",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    # Set limits
    lambda_response = lambda_client.put_function_concurrency(
        FunctionName=function_name, ReservedConcurrentExecutions=concurrent_executions_limit
    )

    # JSON pretty print!
    json_formatted_str = json.dumps(lambda_response, indent=2)

    print(f"Response:\n{json_formatted_str}")

if __name__ == "__main__":
    main()
