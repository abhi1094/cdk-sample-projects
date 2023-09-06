import argparse
import boto3
import botocore
import time
import json
import os
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

with open('data-glue-message.json', 'r') as json_file:
    json_data = json.load(json_file)

server_ip_mapping = json_data.get('server_mappings', {})

target_region = os.environ.get('AWS_TARGET_REGION')
target_account_id = os.environ.get('TARGET_ACCOUNT_ID')

user_supplied_parmater = "reload", "resume"


def start_glue_job(task, retries=2, extra_args=None):
    print("I am here")

    glue = boto3.client('glue', region_name='eu-west-1')

    category = task["category"]
    table = task["table"]
    ip_address = task["ip_address"]
    database = task["database"]
    server = task["server_num"]

    database_lowercase = database[0].lower() + database[1:]

    job_name = f'{table}_export_mssqlToRaw'

    # try:

    print(f"Starting Glue job: {job_name}")

    base_args = {
        '--jdbc_url': f"jdbc:sqlserver://{ip_address}:1433;database={database}",
        "--source_table": table,
        "--target_path_prefix": f"{server}/{database_lowercase}/dbo/{server}/"
    }

    if extra_args:
        base_args.update(extra_args)

    print(base_args)
    retry_count = 0
    while retry_count <= retries:
        try:
            response = glue.start_job_run(
                JobName=job_name,
                Arguments=base_args
            )
            run_id = response['JobRunId']

            print(f"Started {job_name} for {database} with run ID {run_id}")

            while True:
                response_status = glue.get_job_run(JobName=job_name, RunId=run_id)
                status = response_status['JobRun']['JobRunState']
                if status == 'SUCCEEDED':
                    print(f"Job {job_name} completed successfully")
                    return True
                elif status in ('FAILED', 'STOPPED'):
                    print(f"Job {job_name} failed")
                    break
                time.sleep(30)
            
            print(f"Retrying job {job_name}...")
        except Exception as e:
            print(f"Job {job_name} failed. Retrying...Error: {e}")
        retry_count += 1
        time.sleep(60)
    
    return False

def main(extra_args):
    with ThreadPoolExecutor() as executor:
        all_jobs_successful = True
        for server_num, ip_address in server_ip_mapping.items():

            for category, tables in json_data["categories"].items():
                tasks = []
            
                for database in json_data["databases"]:

                    tasks.extend([
                        {
                            'server_num': server_num,
                            'database': database,
                            'table': table,
                            'category': category,
                            'ip_address': ip_address
                        }
                        for table in tables
                    ])

                print(tasks)
                results = executor.map(lambda task: start_glue_job(task, extra_args=extra_args), tasks)
                
                if not all(results):
                    all_jobs_successful = False
    if all_jobs_successful:
        print("proceed with another job")
    else:
        print("some glue jobs failed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--extra_args', type=str, nargs='*', help='Additional key-value pair arguments', required=False)

    args = parser.parse_args()
    extra_args_dict = dict(arg.split('=') for arg in args.extra_args) if args.extra_args else {}

    main(extra_args_dict)
