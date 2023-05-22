# PEER LEARNING DOCUMENT

## PROBLEM STATEMENT
<img width="663" alt="Screenshot 2023-05-22 at 12 52 33 PM 1" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/655ea2ae-03f6-4229-af6c-c493249733f5">




### Aswat Bisht's Approach
Link - https://github.com/bisht-ash/AWS
**Task-1**

He had written a set of commands and ran it from CLI in order to complete the question,At first he has configured AWS Through cli.
- Created a file policy.json and added the AssumeRolePolicyDocument. 
```
{
 	"Version": "2012-10-17",
 	"Statement": {
 		"Effect": "Allow",
 			"Principal": {
 				"Service": “s3.amazonaws.com”
 				“AWS” : “arn:aws:iam::4745*****588:user/bisht-ash”
 				},
 		"Action": "sts:AssumeRole"
 		}
 	}
 ```
- created a IAM role and added s3 full access permission to role
- To use the role he has used the following cli command
```
aws sts assume-role --role-arn arn:aws:iam::4745*****588:role/s3-role --role-session-name my-session --duration-seconds 3600<\pre>
```
-Made a profile and created an instance using that profile
-Finally created s3 bucket
```
aws s3api create-bucket --bucket gswbuck --region us-east-1 --profile s3-role-profile
```
**Task-2**
- Created a role with S3PutAccess and
AWSLambdaBasicExecutionRole
- Created a lambda function
- Attached the role to lambda function
- written a python script in lambda function to save Json in s3 bucket , to log the S3 object creation event and to stop the execution after 3 runs.
```
def lambda_handler(event, context):
    try:
        # Generate JSON in the given format
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
        bucket_name = 'gswbuck'
        key_name = 'transaction{}.json'
        json_data = json.dumps(transaction_data)
        file_name = key_name.format(Timestamp.replace(" ", "-"))
        s3.Bucket(bucket_name).Object(file_name).put(Body=json_data)

        # Log the S3 object creation event
        log_group = 'lambda_logs'
        log_stream = 'lambda_stream'

        log_message = f"Object created in S3 bucket {bucket_name}: {file_name}"
        cw_logs.create_log_group(logGroupName=log_group)
        cw_logs.create_log_stream(logGroupName=log_group, logStreamName=log_stream)
        cw_logs.put_log_events(
            logGroupName=log_group,
            logStreamName=log_stream,
            logEvents=[{
                'timestamp': int(round(time.time() * 1000)),
                'message': log_message
            }]
        )
        if context.invoked_function_arn.endswith(':1'):
                print('First execution')
            elif context.invoked_function_arn.endswith(':2'):
                print('Second execution')
            elif context.invoked_function_arn.endswith(':3'):
                print('Third execution')
            else:
                print('Stopping execution')
                return {
                    'statusCode': 200
                }
    
      except Exception as e:
            print(e)
            return {
                'statusCode': 500
            }
   ```
- Created a cloudwatch rule and checked whether logs are generated or not

**Task-3**
- created a lambda function and Attached the previously created role to this lambda function
-  He had written the necessary import and initiated the required instances and created handler function that does the following things:
     1. Parses the input data from the event parameter.
     2. Generates a timestamp using the current datetime, Adds the timestamp to the input data. 
    3.  Converts the modified input data to a JSON string.    
    4.  Uploads the JSON data to the specified S3 bucket and file name.        
    5.  Prints a log message indicating the successful creation of the S3 object, Return a response object with the file name and success status.
 ```
 import boto3
  import datetime
  import json

  s3 = boto3.resource('s3')

  bucket_name = 'gswbuck'
  key_name = 'file-{}.json'

  def lambda_handler(event, context):
      try:
          body = json.dumps(event['body'])

          timestamp = str(datetime.datetime.now())

          # body["timestamp"] = timestamp

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

      except Exception as e:
          print(e)
          return {
              "status": e
          }
 ```
 - created a new api via API gateway with post method ,added mapping template and then tested and deployed the api.
 - Finally checked whether the files are reflected in s3 bucket or not.


### Chakradhar's approach
Link - https://github.com/chakradharsrinivas16/aws-assignment
**Task-1**
- Created the IAM role using the AWS CLI command
```
aws iam create-role --role-name chakradhar-q1 --assume-role-policy-document file://trustpolicy.json
```
- Attached the S3 full access policy to the IAM role using the AWS CLI command
- Created an EC2 instance with above role, Creating an instance profile and  Attached the role to the instance profile.
- He started instance by writing python script using boto3 
- Finally, He created s3 bucket using AWS cli
```
aws s3api create-bucket --bucket chakradahars3 --region ap-south-1 --create-bucket-configuration LocationConstraint=ap-south-1 
```

**Task-2**
- Created custom role for AWS lambda which will only have put object access Creating policy for put object access using Python Boto3
 ```
 iam = boto3.client('iam')

policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::chakradahars3/*"
            ]
        }
    ]
}

create_policy_response = iam.create_policy(
        PolicyName='chakradhar-put-object-policy',
        PolicyDocument=json.dumps(policy_document)
)

policy_arn = create_policy_response['Policy']['Arn']


role_name = 'chakradhar-put-object-lambda-role'
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
```
- Attached policy to role
 ```
 create_role_response = iam.attach_role_policy(
    RoleName=role_name,
    PolicyArn=policy_arn
)
```
- Added role to generate and access Cloud watch logs and attached the policy to role.
- Created lambda function using above role.
- Scheduled the job to run every minute. Stop execution after 3 runs
```
import boto3
import datetime, time
import json

s3 = boto3.resource('s3')

bucket_name = 'chakradahars3'
key_name = 'transaction{}.json'

cw_logs = boto3.client('logs')
log_group = 'lambda_logs'
log_stream = 'lambda_stream'
counter=0
def set_concurrency_limit(function_name):
    lambda_client = boto3.client('lambda')
    response = lambda_client.put_function_concurrency(
        FunctionName=function_name,
        ReservedConcurrentExecutions=0
    )
    print(response)
def lambda_handler(event, context):
    global counter
    counter+=1
    try:
        # Generate JSON in the given format
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
        if counter==1:
            print('First execution')
        elif counter==2:
            print('Second execution')
        elif counter==3:
            print('Third execution')
            print('Stopping execution')
            set_concurrency_limit('chakradharlambdafunction')
    except Exception as e:
        print(e)
  ```
  - Finally, Checked whether logs are generated or not.
  
  **Task-3**
- Modified lambda function to accept parameters
```
import boto3
import datetime
import json

s3 = boto3.resource('s3')
bucket_name = 'chakradahars3'
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

    except Exception as e:
        print(e)
        return {
            "status": e
        }
 ```
- Created a POST API from API Gateway, pass parameters as request body to Lambda job. Return the filename and status code as a response.
- Consumed API from the local machine and pass unique data to lambda using curl.
