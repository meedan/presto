import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from lib.logger import logger


def upload_file_to_s3_using_filename(bucket: str, filename: str):
    """
    Generic upload helper for s3. Could be moved over to helpers folder...
    """
    s3_client = get_s3_client()
    # Extract the file name from the local file path
    try:
        s3_client.head_bucket(Bucket=bucket)
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket' or int(e.response['Error']['Code']) in [403, 404]:
            # Create the bucket since it does not exist
            s3_client.create_bucket(Bucket=bucket)
            logger.info(f'Created bucket {bucket} in MinIO.') # is this accurate? i.e. is this code only for minio?
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


def upload_file_to_s3(bucket: str, filename: str, content: str):
    try:
        s3_client = get_s3_client()
    except Exception as e:
        logger.error(f'Failed to establish connection to the S3 client: {e}')
        return
    try:
        s3_client.put_object(
            Bucket=bucket, Key=filename, Body=content
        )
        logger.info(f'Successfully uploaded {filename} content to S3 bucket {bucket}.')
    except Exception as e:
        logger.error(f'Failed to upload {filename} content to S3 bucket {bucket}: {e}')


def load_file_from_s3(bucket: str, filename: str):
    try:
        s3_client = get_s3_client()
    except Exception as e:
        logger.error(f'Failed to establish connection to the S3 client: {e}')
        return None
    try:
        response = s3_client.get_object(
            Bucket=bucket, Key=filename
        )
        logger.info(f'Successfully loaded file {filename} from S3 bucket {bucket}.')
        return response['Body'].read().decode('utf-8')
    except Exception as e:
        logger.error(f'Failed to load file {filename} from S3 bucket {bucket}: {e}')
        return None


def file_exists_in_s3(bucket: str, filename: str):
    try:
        s3_client = get_s3_client()
    except Exception as e:
        logger.error(f'Failed to establish connection to the S3 client: {e}')
        return False
    try:
        s3_client.head_object(Bucket=bucket, Key=filename)
        return True
    except Exception as e:
        return False


def get_s3_client():
    s3_url = os.getenv('S3_ENDPOINT')
    region = os.getenv('AWS_DEFAULT_REGION')
    secure = s3_url and s3_url.startswith('https')
    # Set up the S3 client
    s3_client = boto3.client('s3',
                             endpoint_url=s3_url,
                             region_name=region,
                             use_ssl=secure)
    return s3_client
