import boto3
import time

glue = boto3.client('glue')

table_name = 'my_table' 

job_name = f'job_for_{table_name}'

print(f"Starting Glue job: {job_name}")

glue.start_job_run(JobName=job_name)

status = 'STARTING'
while status in ['STARTING', 'RUNNING']:
    time.sleep(10)
    response = glue.get_job_run(JobName=job_name, RunId=response['JobRunId'])
    status = response['JobRun']['JobRunState']
    print(f"Job status: {status}")

if status == 'SUCCEEDED':
    print("Glue job completed successfully!")
else:
    print(f"Glue job failed with status: {status}")
