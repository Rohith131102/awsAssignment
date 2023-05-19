# awsAssignment
## Question-1
### a. Create an IAM role with S3 full access

```
aws iam create-role --role-name rohith  --assume-role-policy-document file://trustpolicy.json
```

**TrustPolicy.json**

```

{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Principal": {
				"Service": "ec2.amazonaws.com"
			 },
	         "Action": "sts:AssumeRole"
		}
	]
}

```
<img width="896" alt="Screenshot 2023-05-17 at 4 40 01 PM" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/6abc3888-4e8f-4cb3-9d2d-296c19e24f67">


**providing full s3 access to the role**

```
aws iam attach-role-policy --role-name rohith --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### b.Create an EC2 instance with above role Creating an instance profile

```
aws iam create-instance-profile --instance-profile-name rohith_instance
```

Attaching the role to the instance profile

```
aws iam add-role-to-instance-profile --instance-profile-name rohith_instance  --role-name rohith 
```

Running the instance

```
aws ec2 run-instances --image-id ami-0889a44b331db0194 --instance-type t3.micro --key-name rohith --iam-instance-profile Name="rohith_instance"
```

1.AMI ID of the Amazon Linux 2 AMI - image-id = ami-0889a44b331db0194

2.instance-type = t3.micro

3.instance-profile='rohith_instance'

<img width="1199" alt="Screenshot 2023-05-19 at 3 35 55 PM" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/cfd57985-43e2-4f6e-8611-01023621e169">


creating the Bucket

```
aws s3api create-bucket --bucket rohiths3bucket1311 --region ap-south-1 --create-bucket-configuration LocationConstraint=ap-south-1
```
<img width="1196" alt="Screenshot 2023-05-18 at 11 45 41 AM" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/d0631cc2-4a2f-449b-873b-ab9114db1422">



## Question-2

Put files in S3 bucket from lambda

creating custom role for aws lambda which will have only put object access

```

import boto3
import json
from botocore.exceptions import ClientError

iam = boto3.client('iam')

#  Put files in S3 bucket from lambda
#  Create custom role for AWS lambda which will have only put object access

policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::rohiths3bucket1311/*"
            ]
        }
    ]
}

create_policy_response = iam.create_policy(
        PolicyName='rohith-putObject-policy',
        PolicyDocument=json.dumps(policy_document)
)

policy_arn = create_policy_response['Policy']['Arn']


role_name = 'rohith-putObject-role'
create_role_response = iam.create_role(
    RoleName=role_name,
    AssumeRolePolicyDocument=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    })
)

create_role_response = iam.attach_role_policy(
    RoleName=role_name,
    PolicyArn=policy_arn
)

# Add role to generate and access Cloud watch logs

cloudwatch_logs_policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:GetLogEvents"
            ],
            "Resource": "*"
        }
    ]
}

cloudwatch_logs_policy_response = iam.create_policy(
    PolicyName='rohith-cloudWatchLogs-policy',
    PolicyDocument=json.dumps(cloudwatch_logs_policy_document)
)

cloudwatch_logs_policy_arn = cloudwatch_logs_policy_response['Policy']['Arn']


iam.attach_role_policy(
    RoleName=role_name ,
    PolicyArn=cloudwatch_logs_policy_arn
)

```

<img width="1118" alt="Screenshot 2023-05-19 at 1 55 27 PM" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/ec88cca5-132f-4cbc-95b0-daa5a2f8f86c">


c. Create a new Lambda function using the above role

<img width="885" alt="Screenshot 2023-05-19 at 3 39 07 PM" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/ac2008d9-c2af-451b-8f9b-8241189a0755">



created a lambda function in which, wrote a python script in such a manner that it generates json in specified format and saves that file in the selected bucket. 

```
import boto3
import datetime, time
import json

s3 = boto3.resource('s3')

bucket_name = 'rohiths3bucket1311'
key_name = 'transaction{}.json'

cw_logs = boto3.client('logs')
log_group = 'lambda_logs'
log_stream = 'lambda_stream'
count=0
def set_concurrency_limit(function_name):
    lambda_client = boto3.client('lambda')
    response = lambda_client.put_function_concurrency(
        FunctionName=function_name,
        ReservedConcurrentExecutions=0
    )
    print(response)
def lambda_handler(event, context):
    global count
    count+=1
    try:
        transaction_id = 12345
        payment_mode = "card/netbanking/upi"
        Amount = 200.0
        customer_id = 101
        Timestamp = str(datetime.datetime.now())
        transaction_data = {
            "transaction_id": transaction_id,
            "payment_mode": payment_mode,
            "Amount": Amount,
            "customer_id": customer_id,
            "Timestamp": Timestamp
        }
        
        # Save JSON file in S3 bucket
        json_data = json.dumps(transaction_data)
        file_name = key_name.format(Timestamp.replace(" ", "_"))
        s3.Bucket(bucket_name).Object(file_name).put(Body=json_data)
        
        # Log the S3 object creation event
        log_message = f"Object created in S3 bucket {bucket_name}: {file_name}"
        cw_logs.put_log_events(
            logGroupName=log_group,
            logStreamName=log_stream,
            logEvents=[{
                'timestamp': int(round(time.time() * 1000)),
                'message': log_message
            }]
        )
        
        # Stop execution after 3 runs
        print(context)
        if count==1:
            print('First execution')
        elif count==2:
            print('Second execution')
        elif count==3:
            print('Third execution')
            print('Stopping execution')
            set_concurrency_limit('rohith-lambda')
    except Exception as exp:
        print(exp)
	
```

d. Schedule the job to run every minute. Stop execution after 3 runs

created a cloudwatch rule such that it runs every minute and attached to lambda function

<img width="853" alt="Screenshot 2023-05-19 at 3 40 48 PM" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/2801e09f-9300-44b3-b993-c336ef3704d7">

To stop exection after three runs I had initilized a count variable in which we increases upon after every execution and once the count reaches three, the executions stops by setting its concurrency to 0

e. Check if cloud watch logs are generated

<img width="1114" alt="Screenshot 2023-05-19 at 3 42 15 PM" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/b469d108-12e5-4aa5-98d8-0d74202d9ed3">


## Question-3
API gateway - Lambda integration

a. Modify lambda function to accept parameters

The function below, after modification, receives the parameters and returns the filename and success message.

```
import boto3
import datetime
import json

s3 = boto3.resource('s3')
bucket_name = 'rohiths3bucket1311'
key_name = 'file{}.json'

def lambda_handler(event, context):
    try:
        # Parse input data
        body = event['body']
        timestamp = str(datetime.datetime.now())
        body["timestamp"] = timestamp
        
        # Save JSON file in S3 bucket
        json_data = json.dumps(body)
        file_name = key_name.format(timestamp.replace(" ", "_"))
        s3.Object(bucket_name, file_name).put(Body=json_data)

        # Log the S3 object creation event
        print(f"Object created in S3 bucket {bucket_name}: {file_name}")

        return {
            "file_name": file_name,
            "status": "success"
        }

    except Exception as exp:
        print(e)
        return {
            "status": exp
        }
```

b. Create a POST API from API Gateway, pass parameters as request body to Lambda job. Return the filename and status code as a response.

steps used to create a post API
1. Navigate to the API Gateway console and click the "Create API" button.
2. Select "REST API" and click "Build" and  provide name for new api and then "Create API"
3. click "create resource" and provide name for resource 
4. add post method and Select "Lambda Function"
5. Enter the name of our Lambda function in the "Lambda Function" field and click "Save".
6. Go to integration request add mapping template "application/json". Put below code there
```
#set($inputRoot = $input.path('$'))
{
    "body": $input.json('$')
}
```
7. Deploy our API by clicking "Actions" > "Deploy API". Select "New Stage" and enter a name for your stage. Click "Deploy"

<img width="1166" alt="Screenshot 2023-05-19 at 3 43 11 PM" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/ec782fff-a9e9-472f-a9d2-7626acf88ad8">

<img width="922" alt="Screenshot 2023-05-19 at 3 44 10 PM" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/2544afb2-f0b1-428b-b869-0fd57d9bdf1d">

<img width="448" alt="Screenshot 2023-05-19 at 12 14 27 PM" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/3dd5d721-8a5e-46c8-910e-2d99b4523fa8">

c. Consume API from the local machine and pass unique data to lambda.
To send the file using local machine, used curl and below command will do the job.

<img width="1440" alt="Screenshot 2023-05-19 at 3 45 03 PM" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/dda00eed-4656-40d8-81f3-60a98f6fd076">


