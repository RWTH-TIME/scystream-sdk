from pydantic import BaseModel
import boto3
from botocore.client import ClientError


class S3Config(BaseModel):
    access_key: str
    secret_key: str
    endpoint: str
    port: int


class S3Operations():
    def __init__(
        self,
        config: S3Config
    ):
        self.boto_client = boto3.client(
            "s3",
            endpoint_url=f"{config.endpoint}:{
                config.port}",
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
        )

    def _create_bucket_if_not_exists(self, bucket_name: str):
        try:
            self.boto_client.head_bucket(Bucket=bucket_name)
        except ClientError:
            self.boto_client.create_bucket(Bucket=bucket_name)

    def upload_file(
        self,
        path_to_file: str,
        bucket_name: str,
        target_name: str
    ):
        # TODO: Validate target_name to be not dangerous/invalid
        self._create_bucket_if_not_exists(bucket_name)
        self.boto_client.upload_file(
            path_to_file, bucket_name, target_name)

    def download_file(
        self,
        bucket_name: str,
        s3_object_name: str,
        local_file_path: str
    ):
        self.boto_client.download_file(
            bucket_name, s3_object_name, local_file_path)
