import boto3
import botocore.exceptions
import time

def create_dms_replication_task(use_range_filter=False, range_condition=None):
    # Initialize the DMS client
    dms_client = boto3.client('dms')

    # Define default table mapping rule (no filter)
    table_mappings = '''
    {
        "rules": []
    }
    '''

    # If use_range_filter is True, create a custom table mapping rule with filter
    if use_range_filter and range_condition:
        table_mappings = '''
        {
            "rules": [
                {
                    "rule-type": "transformation",
                    "rule-id": "1",
                    "rule-action": "selection",
                    "rule-name": "FilterByRange",
                    "object-locator": {
                        "schema-name": "your_schema_name",
                        "table-name": "your_table_name"
                    },
                    "filters": [
                        {
                            "filter-type": "custom",
                            "custom-operator": "sql",
                            "value": "your_range_condition"
                        }
                    ]
                }
            ]
        }
        '''

    # Create the replication task with the chosen table mapping rule
    response = dms_client.create_replication_task(
        MigrationType='full-load',
        SourceEndpointArn='your_source_endpoint_arn',
        TargetEndpointArn='your_target_endpoint_arn',
        TableMappings=table_mappings,
        ReplicationTaskIdentifier='your_task_identifier'
    )

    print(response)

def create_dms_task(dms_client, replication_task_name, source_endpoint_arn, target_endpoint_arn, migration_type):
    try:
        # Get the DMS task details
        response = dms_client.describe_replication_tasks(Filters=[{'Name': 'replication-task-arn', 'Values': [task_arn]}])
        task = response['ReplicationTasks'][0]
    
        # Calculate the number of records to migrate in each chunk
        total_records = task['ReplicationTaskStats']['FullLoadProgressPercent']
        total_records_to_migrate = (chunk_size * total_records) // 100
    
        # Start the DMS task with the specified chunk size
        response = dms_client.start_replication_task(
            ReplicationTaskArn=task_arn,
            StartReplicationTaskType='start-replication',
            CdcStartPosition=task['ReplicationTaskStats']['FullLoadCdcStartPosition'],
            CdcStopPosition=task['ReplicationTaskStats']['FullLoadCdcStopPosition'],
            CdcStartTime=task['ReplicationTaskStats']['FullLoadCdcStartTime'],
            CdcStopTime=task['ReplicationTaskStats']['FullLoadCdcStopTime'],
            TableMappings=task['ReplicationTaskStats']['TableMappings'],
            ReplicationTaskSettings=task['ReplicationTaskStats']['ReplicationTaskSettings'],
            CdcStartPositionForChunk=total_records_to_migrate
        )
    
        print("DMS task started with chunk size:", chunk_size)
    except botocore.exceptions.ClientError as e:
        print("Error creating DMS task:", e)
        return None

def poll_dms_task_status(dms_client, replication_task_arn):
    while True:
        try:
            response = dms_client.describe_replication_tasks(
                Filters=[
                    {
                        'Name': 'replication-task-arn',
                        'Values': [replication_task_arn]
                    }
                ]
            )
            status = response['ReplicationTasks'][0]['Status']
            print("DMS task status:", status)

            if status == 'stopped':
                print("DMS task completed successfully.")
                break

            time.sleep(10)  # Poll every 10 seconds
        except botocore.exceptions.ClientError as e:
            print("Error polling DMS task status:", e)
            break

def poll_glue_job_status(glue_client, job_name):
    while True:
        try:
            response = glue_client.get_job_runs(JobName=job_name, MaxResults=1, Sort={'Column': 'STARTED', 'SortOrder': 'DESCENDING'})
            if not response['JobRuns']:
                print("Glue job run not found.")
                return False

            status = response['JobRuns'][0]['JobRunState']
            print("Glue job status:", status)

            if status == 'SUCCEEDED':
                print("Glue job completed successfully.")
                return True
            elif status == 'FAILED' or status == 'STOPPED':
                print("Glue job failed or stopped.")
                return False

            time.sleep(10)  # Poll every 10 seconds
        except botocore.exceptions.ClientError as e:
            print("Error polling Glue job status:", e)
            return False

if __name__ == "__main__":
    aws_role_arn = 'arn:aws:iam::YOUR_ACCOUNT_ID:role/YOUR_ROLE_NAME'
    aws_region = 'YOUR_AWS_REGION'

    sts_client = boto3.client('sts')
    assumed_role = sts_client.assume_role(RoleArn=aws_role_arn, RoleSessionName='AssumedRoleSession')

    session = boto3.Session(
        aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
        aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
        aws_session_token=assumed_role['Credentials']['SessionToken'],
        region_name=aws_region
    )

    dms_client = session.client('dms')

    eventbridge_client = session.client('events')

    # Replace these with your actual DMS task parameters
    source_endpoint_arn = 'SOURCE_ENDPOINT_ARN'
    target_endpoint_arn = 'TARGET_ENDPOINT_ARN'
    replication_task_name = 'MY_REPLICATION_TASK'
    migration_type = 'full-load'  # or 'cdc' for change data capture

    replication_task_arn = create_dms_task(dms_client, replication_task_name, source_endpoint_arn, target_endpoint_arn, migration_type)

    if replication_task_arn:
        poll_dms_task_status(dms_client, replication_task_arn)
    else:
        print("DMS task creation failed.")
