import json
import base64
import boto3

cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    namespace = 'MyCustomNamespace'  # You can also use environment variables if needed
    
    for record in event['awslogs']['data']:
        payload = json.loads(base64.b64decode(record))
        log_events = payload['logEvents']

        for log_event in log_events:
            log = json.loads(log_event['message'])
            memory_utilized = log.get('MemoryUtilized')
            memory_reserved = log.get('MemoryReserved')
            container_id = log.get('ContainerId')

            if memory_reserved and memory_utilized:
                memory_utilization_percent = (memory_utilized / memory_reserved) * 100

                cloudwatch.put_metric_data(
                    Namespace=namespace,
                    MetricData=[
                        {
                            'MetricName': 'MemoryUtilizationPercentage',
                            'Dimensions': [
                                {
                                    'Name': 'ContainerId',
                                    'Value': container_id
                                }
                            ],
                            'Unit': 'Percent',
                            'Value': memory_utilization_percent
                        }
                    ]
                )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Successfully processed log events')
    }
