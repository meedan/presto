import boto3

def upload_file_to_s3(bucket: str, filename: str):
    """
    Generic upload helper for s3. Could be moved over to helpers folder...
    """
    # Set up the S3 client
    s3_client = boto3.client('s3')
    # Extract the file name from the local file path
    file_name = filename.split('/')[-1]
    # Upload the file to S3
    try:
        s3_client.upload_file(filename, bucket, file_name)
        print(f'Successfully uploaded file {file_name} to S3 bucket.')
    except Exception as e:
        print(f'Failed to upload file {file_name} to S3 bucket: {e}')
