# AWS Lambda with SQS Queues

Welcome to this AWS project! This project utilizes an origin SQS queue to trigger an AWS Lambda function that analyzes product reviews, determining their polarity (sentiment analysis), and sends the results to a destination SQS queue.

### Example JSON for Product Reviews:

```json
{
  "username": "john1",
  "message": "best product I ever bought!"
}
```

## Installation

To install the required project dependencies, run the following command:

```bash
pip install -r requirements.txt
```

## Project Structure

- **`data/`**: Contains ZIP files of the Lambda functions.
- **`src/`**: The main source code responsible for deploying the Lambda function and managing the SQS queues on AWS.
- **`tests/`**: Contains unit and integration tests to ensure code stability.

## Usage

### Configure AWS CLI

Before starting, ensure you have the [AWS CLI installed](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and set up your credentials by running:

```bash
aws configure --profile mlops
```

To make this profile the default, use one of the following commands depending on your environment:

**Linux:**

```bash
export AWS_PROFILE=mlops
```

**Windows CMD:**

```bash
set AWS_PROFILE=mlops
```

**Windows PowerShell:**

```bash
$env:AWS_PROFILE = "mlops"
```

### Create and Configure ECR Repository

1. Build the Docker image for the Lambda function using the following command:

```bash
docker build --platform linux/amd64 -t lambda-sqs-image:test .
```

2. To test the containerized application locally, ensure the following environment variable is exported:
   - `DESTINATION_SQS_URL`: URL of the SQS queue that will receive the Lambda function responses.

```bash
docker run -p 9500:8080 lambda-sqs-image:test
curl "http://localhost:9500/2015-03-31/functions/function/invocations" -d "{}"
curl -X POST -H "Content-Type: application/json" -d '{"body": "{\"username\": \"jake\", \"message\": \"best product I ever bought\"}"}' "http://localhost:9500/2015-03-31/functions/function/invocations"
```

3. Create an AWS ECR repository to store your Docker images:

```bash
repository_name="lambda-sqs-repo-renatex"

aws ecr create-repository --repository-name "$repository_name" --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE --query 'repository.{repositoryArn:repositoryArn, repositoryUri:repositoryUri}' --output text | awk '{print "REPOSITORY_ARN=\""$1"\"\nREPOSITORY_URI=\""$2"\""}' | tee -a .env
```

4. Log in to ECR using Docker:

```bash
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin AWS_ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com
```

5. Rebuild the Docker image if necessary, tag it, and push it to the ECR repository:

```bash
docker build --platform linux/amd64 -t lambda-sqs-image:test .

docker tag lambda-sqs-image:test REPOSITORY_URI:latest

docker push REPOSITORY_URI:latest
```

### Deploy the Lambda Function and SQS Queues

To deploy the Lambda function from the ECR image and create both origin and destination SQS queues, run:

```bash
python3 src/deploy_instances.py <queue_name> <function_name>
```

### Testing the Deployed Instances

To test the Lambda function and SQS queues, run:

```bash
python tests/test_deployed_instances.py
```

## References

- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [Lambda Concurrency Documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-concurrency.html)
