import os
import boto3

def send_sqs_message(message):
    sqs = boto3.client("sqs")
    queue_url = os.environ.get("DESTINATION_SQS_URL")
    response = sqs.send_message(QueueUrl=queue_url, MessageBody=message)
    return response

def lambda_handler(event, context):
    # Read batch of messages
    for record in event["Records"]:
        payload = record["body"]

        # Send each message to destination queue
        send_sqs_message(f"process: {payload}")

    return event["Records"]