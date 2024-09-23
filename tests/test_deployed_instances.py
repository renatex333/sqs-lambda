import os
import io
import time
import json
import boto3
from dotenv import load_dotenv

def test_deployed_instances():
    load_dotenv()

    lambda_client = boto3.client(
        "lambda",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    sqs_client = boto3.client(
        "sqs",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    lambda_response = lambda_client.invoke(
        FunctionName=os.getenv("FUNCTION_NAME"),
        InvocationType="RequestResponse",
        Payload=json.dumps({"body": json.dumps({"username": "john1", "message": "best product I ever bought!"})})
    )
    print("Basic Lambda Function response:")
    print(io.BytesIO(lambda_response["Payload"].read()).read().decode("utf-8"))
    print()


    origin_queue_url = os.getenv("ORIGIN_SQS_URL")
    destination_queue_url = os.getenv("DESTINATION_SQS_URL")

    # Clear the queues
    try:
        sqs_client.purge_queue(QueueUrl=origin_queue_url)
        sqs_client.purge_queue(QueueUrl=destination_queue_url)
    except sqs_client.exceptions.PurgeQueueInProgress:
        pass
    finally:
        print("Clearing the queues...")
        print()

    # Send messages to the origin queue and 
    # display the messages in the destination queue
    messages = [
        {"username": "john1", "message": "best product I ever bought!"},
        {"username": "mary2", "message": "I love this product!"},
        {"username": "jane3", "message": "I recommend this product."},
        {"username": "joe4", "message": "I am disgusted with this product."},
        {"username": "jill5", "message": "I hate this product."},
        {"username": "jim6", "message": "worst product I ever bought!"},
    ]

    print("Sending messages to the origin queue...")
    for message in messages:
        try:
            send_response = sqs_client.send_message(
                QueueUrl=origin_queue_url,
                MessageBody=json.dumps(message),
            )
            print("Message sent to the queue:", send_response)
            print()
        except Exception as e:
            print(f"Failed to send message: {e}")
            print()

        time.sleep(5)  # Wait for the messages to be processed
    
        # Display the messages
        print("Destination Queue Messages:")
        print()
        try:
            receive_response = sqs_client.receive_message(
                QueueUrl=destination_queue_url
            )
            received_messages = receive_response.get("Messages", [])
            for message in received_messages:
                print("Message ID:", message["MessageId"])
                print("Message Body:", message["Body"])
                print()
        except Exception as e:
            print(f"Failed to receive messages: {e}")
            print()

if __name__ == "__main__":
    test_deployed_instances()