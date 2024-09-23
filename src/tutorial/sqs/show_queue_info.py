import os
import boto3
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


    # Get the attributes of the SQS queue
    response = sqs_client.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["All"])

    # Extract the desired attributes from the response
    attributes = response["Attributes"]
    approximate_message_count = attributes["ApproximateNumberOfMessages"]
    approximate_message_not_visible_count = attributes[
        "ApproximateNumberOfMessagesNotVisible"
    ]

    print("Approximate number of visible messages:", approximate_message_count)
    print(
        "Approximate number of messages not visible:", approximate_message_not_visible_count
    )

if __name__ == "__main__":
    main()
