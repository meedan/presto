import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from lib.logger import logger
def upload_file_to_s3(bucket: str, filename: str):
    """
    Generic upload helper for s3. Could be moved over to helpers folder...
    """
    s3_url = os.getenv('S3_ENDPOINT')
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_DEFAULT_REGION')
    secure = s3_url and s3_url.startswith('https')
    # Set up the S3 client
    s3_client = boto3.client('s3',
        endpoint_url=s3_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version='s3v4'),
        region_name=region,
        use_ssl=secure)
    # Extract the file name from the local file path
    try:
        s3_client.head_bucket(Bucket=bucket)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket' or int(e.response['Error']['Code']) == 404:
            # Create the bucket since it does not exist
            s3_client.create_bucket(Bucket=bucket)
            logger.info(f'Created bucket {bucket} in MinIO.')
        else:
            # Other errors like permissions issues
            logger.error(f'Error in accessing bucket {bucket}: {e}, {bucket} {filename}')
            raise e
    file_name = filename.split('/')[-1]
    # Upload the file to S3
    try:
        s3_client.upload_file(filename, bucket, file_name)
        logger.info(f'Successfully uploaded file {file_name} to S3 bucket.')
    except Exception as e:
        logger.error(f'Failed to upload file {file_name} to S3 bucket: {e}')
