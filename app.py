from aws_cdk import core
from aws_cdk import aws_dms as dms
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_ec2 as ec2

class DMSStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC
        vpc = ec2.Vpc(self, "MyVPC", max_azs=2)  # Replace with your VPC configuration

        # Create an S3 bucket to store the migrated data with partitioning enabled
        partitioned_bucket = s3.Bucket(
            self,
            "PartitionedBucket",
            bucket_name="my-partitioned-bucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.KMS_MANAGED,
        )

        # Define the DMS replication instance and endpoints
        # Define the DMS replication instance
        replication_instance = dms.CfnReplicationInstance(
            self,
            "ReplicationInstance",
            replication_instance_identifier="MyReplicationInstance",
            replication_instance_class="dms.r5.large",
            publicly_accessible=False,
            engine_version="3.4.4",
            vpc_security_group_ids=[vpc.vpc_default_security_group],
            vpc_subnet_id=vpc.public_subnets[0].subnet_id,
        )

        # Define the list of source databases and tables to migrate
        source_databases = [
            {
                "server_name": "db1_endpoint",  # Replace with your SQL Server endpoint for database 1
                "port": 1433,
                "database_name": "db1_name",  # Replace with the name of database 1
                "username": "db1_username",  # Replace with the username for database 1
                "password": "db1_password",  # Replace with the password for database 1
                "tables": ["TableA", "TableB"],  # Replace with the names of tables to migrate from database 1
            },
            {
                "server_name": "db2_endpoint",  # Replace with your SQL Server endpoint for database 2
                "port": 1433,
                "database_name": "db2_name",  # Replace with the name of database 2
                "username": "db2_username",  # Replace with the username for database 2
                "password": "db2_password",  # Replace with the password for database 2
                "tables": ["TableC", "TableD"],  # Replace with the names of tables to migrate from database 2
            },
            # Add more databases with tables as needed
        ]

        # Create replication tasks for each table and enable partitioning
        for db in source_databases:
            for table in db["tables"]:
                # Create replication task for each table
                replication_task = dms.CfnReplicationTask(
                    self,
                    f"ReplicationTask-{db['database_name']}-{table}",
                    # Define the replication task details (source endpoint, target endpoint, etc.)
                    # ...
                    table_mappings= f"""
                        {{
                            "rules": [
                                {{
                                    "rule-type": "selection",
                                    "rule-id": "1",
                                    "rule-name": "1",
                                    "object-locator": {{
                                        "schema-name": "dbo",
                                        "table-name": "{table}"
                                    }},
                                    "rule-action": "include",
                                    "filters": []
                                }}
                            ],
                            "settings": {{
                                "targetPartitionEnabled": "true",  # Enable partitioning
                                "targetPartitionKeyOption": "DDL_PARAMETER",  # Use DDL_PARAMETER as the partition key option
                                "targetPartitionKey": "{{\\"year\\": \\"2023\\", \\"month\\": \\"04\\"}}"  # Provide an initial partition key value
                            }}
                        }}
                    """
                )

                # Set the target S3 bucket with partitioning for the replication task
                replication_task.node.add_dependency(partitioned_bucket)

app = core.App()
DMSStack(app, "DMSStack")
app.synth()
