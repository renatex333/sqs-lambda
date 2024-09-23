import os
import boto3
import json
from dotenv import load_dotenv

def main():
    load_dotenv()

    # Replace with your queue URL or name
    queue_url = os.getenv("QUEUE_URL")

    # Create a Boto3 client for AWS Lambda
    sqs_client = boto3.client(
        "sqs",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    # Receive messages from the SQS queue
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        VisibilityTimeout=60,  # Timeout in seconds before the message becomes visible again
        WaitTimeSeconds=20,  # Wait up to 20 seconds for a message to be available
    )

    # Process received messages
    for message in response.get("Messages", []):
        message_text = message["Body"]

        # Print the message
        print(f"Received message: {message_text}")

        # Delete the processed message from the SQS queue
        sqs_client.delete_message(
            QueueUrl=queue_url,  # Replace with your queue URL or name
            ReceiptHandle=message["ReceiptHandle"],
        )

if __name__ == "__main__":
    main()
