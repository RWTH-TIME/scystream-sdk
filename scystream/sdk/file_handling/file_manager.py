from pydantic import BaseModel


class S3Config(BaseModel):
    """
    Configuration needed for setting up the connection to a S3 bucket.
    """
    access_key: str
    secret_key: str
    endpoint: str


class FileOperations:
    def __init__(self, spark_session):
        self.spark_session = spark_session

    def upload_file_to_s3(self, local_path, s3_path):
        """Upload a file to S3 using Spark"""
        # This will not work! Setup s3 connection
        df = self.spark_session.read.text(
            local_path)
        df.write.text(s3_path)
        print(f"Uploaded {local_path} to {s3_path}")

    def download_file_from_s3(self, s3_path, local_dest_path):
        """Download a file from S3 using Spark"""
        df = self.spark_session.read.text(s3_path)
        df.write.text(local_dest_path)
        print(f"Downloaded {s3_path} to {local_dest_path}")
