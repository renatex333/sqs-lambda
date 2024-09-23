import os
import boto3
from dotenv import load_dotenv, set_key

def main():
    load_dotenv()

    queue_name = "lambda_origin_queue_renatex"

    # Create a Boto3 client for AWS Lambda
    sqs_client = boto3.client(
        "sqs",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    # Create a new SQS queue
    response = sqs_client.create_queue(
        QueueName=queue_name,
        Attributes={
            "DelaySeconds": "0",
            "MessageRetentionPeriod": "3600",  # 1 hour in seconds (could be days in real applications)
        },
    )

    # Get the queue URL
    queue_url = response["QueueUrl"]

    print("SQS queue created with URL:", queue_url)
    set_key(".env", "\nORIGIN_SQS_URL", queue_url)

if __name__ == "__main__":
    main()
