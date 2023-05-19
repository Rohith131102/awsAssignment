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
