# How to add retry logic in glue from point of failure

- We introduce a checkpoint mechanism that uses an Amazon S3 bucket (checkpoint_path) to store the progress of the Glue job. The processed_files list keeps track of the S3 file paths that have been processed so far.

- The Glue job reads the checkpoint data at the beginning of the job execution and resumes processing from the point of the last successful checkpoint (i.e., files that have not been processed yet).

- After successfully processing each table, the script updates the checkpoint by appending the processed S3 file path to the processed_files list. This checkpoint is then saved to S3 after processing each table.

- In the event of a failure, the Glue job will pick up from where it left off based on the checkpoint data. It will continue processing the remaining tables that were not successfully processed before the failure occurred.

