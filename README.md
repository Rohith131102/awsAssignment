# awsAssignment
## Question-1
### a. Create an IAM role with S3 full access

`
aws iam create-role --role-name rohith  --assume-role-policy-document file://trustpolicy.json
`

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

<img width="896" alt="Screenshot 2023-05-17 at 4 40 01 PM" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/27e63556-160e-4b00-9586-a61742952bee">

**providing full s3 access to the role**

` 
aws iam attach-role-policy --role-name rohith --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
`

### b.Create an EC2 instance with above role Creating an instance profile

`
aws iam create-instance-profile --instance-profile-name rohith_instance
`

Attaching the role to the instance profile

`
aws iam add-role-to-instance-profile --instance-profile-name rohith_instance  --role-name rohith 
`

Running the instance

`
aws ec2 run-instances --image-id ami-0889a44b331db0194 --instance-type t3.micro --key-name rohith --iam-instance-profile Name="rohith_instance"
`

1.AMI ID of the Amazon Linux 2 AMI - image-id = ami-0889a44b331db0194

2.instance-type = t3.micro

3.instance-profile='rohith_instance'

<img width="1172" alt="Screenshot 2023-05-19 at 1 02 04 PM" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/787dedd2-ae78-43a5-9ae0-89774b9f1e8e">


creating the Bucket

`
aws s3api create-bucket --bucket rohiths3bucket1311 --region ap-south-1 --create-bucket-configuration LocationConstraint=ap-south-1
`
<img width="1196" alt="Screenshot 2023-05-18 at 11 45 41 AM" src="https://github.com/Rohith131102/awsAssignment/assets/123619674/fb82e637-9f46-426d-b74e-0eeca41c6176">

## Question-2

Put files in S3 bucket from lambda

creating custom role for aws lambda which will have only put object access

```

import boto3
import json
from botocore.exceptions import ClientError



iam = boto3.client('iam')

#  Put files in S3 bucket from lambda
#  a. Create custom role for AWS lambda which will have only put object access

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



#  b. Add role to generate and access Cloud watch logs

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
