import json
import boto3
import os

# Initialize the SNS client
sns_client = boto3.client('sns')
sns_topic_arn = os.environ['SNS_TOPIC_ARN']  # Read SNS topic ARN from Lambda environment variables

# Dictionary to keep track of job failure counts for specific jobs
failure_counts = {}

# Specify the Glue job names to monitor
jobs_to_monitor = ['job1', 'job2']  # Add the names of the jobs you want to monitor

def lambda_handler(event, context):
    for record in event['Records']:
        sns_message = json.loads(record['Sns']['Message'])
        job_name = sns_message['detail']['jobName']
        job_state = sns_message['detail']['state']

        # Check if the Glue job is in the list of jobs to monitor and if it has failed
        if job_name in jobs_to_monitor and job_state == 'FAILED':
            # Initialize the failure count if not already present
            failure_counts.setdefault(job_name, 0)
            
            # Increment the failure count for this job
            failure_counts[job_name] += 1
            
            # Check if this is the second consecutive failure
            if failure_counts[job_name] == 2:
                # Send an SNS notification for the second failure
                message = f"Glue job {job_name} has failed for the second time."
                sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Message=message,
                    Subject=f"Glue Job Second Failure: {job_name}"
                )
                
    return {
        'statusCode': 200,
        'body': json.dumps('Lambda function executed successfully.')
    }
