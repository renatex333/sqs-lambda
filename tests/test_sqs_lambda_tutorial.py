import os
import io
import json
import boto3
import requests
from dotenv import load_dotenv

def test_function(lambda_client, function_name):

    assert function_exists(lambda_client, function_name) == True, f"Function {function_name} does not exist"

    for i in range(5):
        response = function_invoke(lambda_client, function_name)
    

def function_exists(lambda_client, function_name) -> bool:
    """
    Check if the function exists
    """
    try:
        lambda_client.get_function(FunctionName=function_name)
        return True
    except lambda_client.exceptions.ResourceNotFoundException:
        return False
    
def function_invoke(lambda_client, function_name) -> dict:
    """
    Invoke the function
    """
    response = lambda_client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
    )

    payload = response["Payload"]

    return io.BytesIO(payload.read()).read().decode("utf-8")

def test_queue(sqs_client, queue_url):
    """
    Test the SQS queue
    """
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

def display_queue_messages(sqs_client, queue_url, queue_name):
    """
    Display the messages in the SQS queue
    """
    # Receive messages from the SQS queue
    response = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)

    # Extract the messages from the response
    messages = response.get("Messages", [])

    print(f"{queue_name}:")
    # Display the messages
    for message in messages:
        print("Message ID:", message["MessageId"])
        print("Message Body:", message["Body"])
        print()

def test_queue_send_message(sqs_client, queue_url):
    """
    Test the SQS queue by sending a message
    """
    # Send a message to the SQS queue
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody="Test Message",
    )

    print("Message sent to the queue:", response)

def test_event_mapping(lambda_client, sqs_client, function_name, origin_queue_url, destination_queue_url):
    """
    Test the event mapping
    """

    # Get the event mapping ID
    event_mapping_id = os.getenv("EVENT_SOURCE_MAPPING_UUID")

    print("Event Mapping ID:", event_mapping_id)

    # Test the event mapping
    display_queue_messages(sqs_client, origin_queue_url, "Origin Queue Messages")
    test_queue_send_message(sqs_client, origin_queue_url)
    display_queue_messages(sqs_client, origin_queue_url, "Origin Queue Messages")
    display_queue_messages(sqs_client, destination_queue_url, "Destination Queue Messages")

    # Test if origin and destination queues have messages
    test_queue(sqs_client, origin_queue_url)
    test_queue(sqs_client, destination_queue_url)

if __name__ == "__main__":
    load_dotenv()

    # Create a Boto3 client for AWS Lambda
    lambda_client = boto3.client(
        "lambda",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    origin_queue_url = os.getenv("ORIGIN_SQS_URL")
    destination_queue_url = os.getenv("DESTINATION_SQS_URL")

    # Create a Boto3 client for AWS Lambda
    sqs_client = boto3.client(
        "sqs",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    test_function(lambda_client, "lambda_sqs_renatex")
    test_function(lambda_client, "read_write_sqs_renatex")
    test_queue(sqs_client, origin_queue_url)
    test_queue(sqs_client, destination_queue_url)
    test_event_mapping(lambda_client, sqs_client, "read_write_sqs_renatex", origin_queue_url, destination_queue_url)
