import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [TempDir, JOB_NAME]
args = getResolvedOptions(sys.argv, ['TempDir', 'JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Function to extract data from S3
def extract_data(s3_path):
    return glueContext.create_dynamic_frame.from_options(
        connection_type = "s3",
        format = "csv",  # Update this to match the format of your data
        connection_options = {"paths": [s3_path]},
        transformation_ctx = "datasource"
    )

# Function to transform data
def transform_data(dynamic_frame):
    # Convert the Glue dynamic frame to Spark DataFrame
    try:

        spark = SparkSession.builder.getOrCreate()
        df = dynamic_frame.toDF()

        # Your data transformation logic here
        # For this example, let's insert a new row with fixed values

        # Create a new DataFrame with the new row data
        new_row_data = [(1000, 'John Doe', 30), (1001, 'Jane Smith', 28)]
        new_row_columns = ['id', 'name', 'age']
        new_row_df = spark.createDataFrame(new_row_data, new_row_columns)

        # Union the new row DataFrame with the original DataFrame
        transformed_df = df.union(new_row_df)

        # Convert the Spark DataFrame back to a Glue dynamic frame
        transformed_dynamic_frame = DynamicFrame.fromDF(transformed_df, glueContext, "transformed_dynamic_frame")

        raise Exception("Error occurred during transformation")

        return transformed_dynamic_frame

    except Exception as e:
        # Handle the error and raise it to trigger job failure
        print(f"Error occurred during transformation: {e}")
        raise e


# Function to load data back to S3
def load_data(dynamic_frame, s3_prefix):
    glueContext.write_dynamic_frame.from_options(
        frame = dynamic_frame,
        connection_type = "s3",
        connection_options = {"path": s3_prefix},
        format = "parquet",  # Update this to the desired output format
        transformation_ctx = "datasink"
    )

def main():
    # Get the S3 prefix (the data from SQL Server via DMS creates a new prefix)
    s3_prefix = "s3://your_bucket_name/prefix_from_sqlserver/" # Update this based on how the prefix is determined

    # Load checkpoint from S3
    checkpoint_path = "s3://your_bucket_name/glue_job_checkpoint/"  # Update this to your desired S3 location
    checkpoint_key = "glue_job_checkpoint_key"  # Update this to your desired key for the checkpoint file
    try:
        checkpoint = spark.read.option("header", "true").csv(checkpoint_path + checkpoint_key)
        processed_files = checkpoint.select("file_path").rdd.flatMap(lambda x: x).collect()
    except:
        processed_files = []

    try:
        # Process each table
        table_names = ["table1", "table2", "table3"] # Add more table names here
        for table_name in table_names:
            s3_path = s3_prefix + table_name
            if s3_path not in processed_files:
                data_frame = extract_data(s3_path)
                transformed_data_frame = transform_data(data_frame)
                load_data(transformed_data_frame, s3_path)
                processed_files.append(s3_path)

        # Save the checkpoint to S3
        checkpoint_df = spark.createDataFrame([(file_path,) for file_path in processed_files], ["file_path"])
        checkpoint_df.write.option("header", "true").csv(checkpoint_path + checkpoint_key)

        # Job completed successfully
        job.commit()
    except Exception as e:
        # Handle the failure and retry
        print(f"Error occurred during job execution: {e}")
        job.commit()

if __name__ == "__main__":
    main()
