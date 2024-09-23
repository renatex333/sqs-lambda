import os
import io
import sys
import boto3
import concurrent.futures
from dotenv import load_dotenv

def main(num_executions: int = 10):
    """
    Args:
    num_executions: int
        Define the number of concurrent executions/calls
    """

    load_dotenv()

    # Lambda function name: do_something_concurrent_<YOUR_INSPER_USERNAME>
    function_name = "do_something_concurrent_renatex"

    # Create a Boto3 client for AWS Lambda
    lambda_client = boto3.client(
        "lambda",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )


    try:
        # Create a thread pool executor with the desired number of threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_executions) as executor:
            # List to store the future objects
            futures = []

            # Submit the Lambda invocations to the executor
            for _ in range(num_executions):
                future = executor.submit(
                    lambda_client.invoke,
                    FunctionName=function_name,
                    InvocationType="RequestResponse",
                )
                futures.append(future)

            # Process the results as they become available
            for future in concurrent.futures.as_completed(futures):
                print("-" * 40)
                response = future.result()
                payload = response["Payload"]
                txt = io.BytesIO(payload.read()).read().decode("utf-8")
                print(f"Response:\n{txt}")

    except Exception as e:
        print(e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(int(sys.argv[1]))
    main()
