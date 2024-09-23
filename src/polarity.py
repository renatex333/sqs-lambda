"""
Module to contain the polarity function for the sentiment analysis of product reviews
"""

import os
import json
import boto3
from textblob import TextBlob

def lambda_handler(event, context):
    """
    Handler function for the sentiment analysis lambda function
    """
    # Test if the event has a body
    if "body" not in event:
        return {
            "error": "No body in the request"
        }

    body = json.loads(event["body"])

    # Test if the body has a message and a username
    if "message" not in body or "username" not in body:
        return {
            "error": "No message or username in the request body"
        }

    username = body["username"]
    received_text = body["message"]
    blob = TextBlob(received_text)
    polarity = str(blob.polarity)

    # Send the message to the destination SQS queue

    # Create an SQS client
    sqs = boto3.client("sqs")

    # Define the queue URL
    queue_url = os.getenv("DESTINATION_SQS_URL")

    # Define the message to send
    message_body = {
        "username": username,
        "message": received_text,
        "polarity": polarity
    }

    message_body = json.dumps(message_body)

    # Send message to the queue
    response = sqs.send_message(QueueUrl=queue_url, MessageBody=message_body)
    return response
