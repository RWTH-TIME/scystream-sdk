from pydantic import BaseModel
import boto3
from botocore.client import ClientError
from scystream.sdk.env.settings import FileSettings


class S3Config(BaseModel):
    """
    Configuration for accessing an S3-compatible service.

    This model holds the necessary parameters to authenticate and connect
    to an S3-compatible service.

    :param S3_ACCESS_KEY: access key for authentication.
    :param S3_SECRET_KEY: secret key for authentication.
    :param S3_HOST: The endpoint URL for the S3-compatible service.
    :param S3_PORT: The port used by the S3-compatible service.
    """
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_HOST: str
    S3_PORT: str


class S3Operations():
    """
    A class that encapsulates operations on an S3-compatible service.

    This class includes methods to upload and download files to/from an
    S3 bucket. It also ensures the bucket exists before performing any
    operations.
    """

    def __init__(
        self,
        config: S3Config | FileSettings
    ):
        """
        Initializes the S3 client with the provided configuration.

        :param config: An instance of the S3Config model containing the
        necessary authentication and connection information.
        """
        self.boto_client = boto3.client(
            "s3",
            endpoint_url=f"{config.S3_HOST}:{config.S3_PORT}",
            aws_access_key_id=config.S3_ACCESS_KEY,
            aws_secret_access_key=config.S3_SECRET_KEY,
        )

    def _create_bucket_if_not_exists(self, bucket_name: str):
        """
        Creates an S3 bucket if it does not already exist.

        This method checks whether the specified bucket exists. If it does not,
        the bucket is created.

        :param bucket_name: The name of the S3 bucket to check or create.
        """
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
        """
        Uploads a file from the local filesystem to an S3 bucket.

        This method uploads a file to the specified S3 bucket, creating the
        bucket if it does not exist.

        :param path_to_file: The path to the local file that needs to be
            uploaded.
        :param bucket_name: The name of the S3 bucket where the file will be
            uploaded.
        :param target_name: The name the file will have once it is uploaded to
            the bucket.

        :raises ClientError: If there is an error with the S3 client, such as
            a failed upload.
        """
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
        """
        Downloads a file from an S3 bucket to a local path.

        This method downloads the specified file from the given S3 bucket
        and saves it to the local filesystem.

        :param bucket_name: The name of the S3 bucket from which to download
            the file.
        :param s3_object_name: The name of the file in the S3 bucket that will
            be downloaded.
        :param local_file_path: The local path where the downloaded file will
            be saved.

        :raises ClientError: If there is an error with the S3 client, such as
            a failed download.
        """
        self.boto_client.download_file(
            bucket_name, s3_object_name, local_file_path)
