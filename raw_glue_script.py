import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# SQL Server connection
jdbc_url = "jdbc:sqlserver://hostname:port;database=db"
connection_options = {
  "url": jdbc_url,
  "dbtable": "schema.table",
  "user": "username",
  "password": "password"
}

# Extract data frame from SQL Server 
datasource0 = glueContext.create_dynamic_frame.from_options(
  connection_type = "microsoft.sqlserver", 
  connection_options = connection_options
)

# Write to S3 in Parquet format 
datasink4 = glueContext.write_dynamic_frame.from_options(
  frame = datasource0,
  connection_type = "s3",
  connection_options = {"path": "s3://bucket/output/"},
  format = "parquet"
)

job.commit()
