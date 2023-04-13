import unittest
from unittest.mock import MagicMock

from botocore.exceptions import ClientError
import boto3

from lib.s3 import upload_file_to_s3

class TestUploadFileToS3(unittest.TestCase):
    def setUp(self):
        self.bucket = "test-bucket"
        self.filename = "testfile.txt"
        self.s3_client_mock = MagicMock()

    def test_upload_file_to_s3_success(self):
        # Mock a successful upload
        self.s3_client_mock.upload_file.return_value = None
        boto3.client = MagicMock(return_value=self.s3_client_mock)

        # Call the function
        upload_file_to_s3(self.bucket, self.filename)

        # Assert that the upload was called with the correct arguments
        self.s3_client_mock.upload_file.assert_called_once_with(
            self.filename, self.bucket, self.filename.split('/')[-1]
        )

    def test_upload_file_to_s3_failure(self):
        # Mock a failed upload
        error_message = "Failed to upload file"
        self.s3_client_mock.upload_file.side_effect = ClientError(
            {"Error": {"Message": error_message}}, "upload_file"
        )
        boto3.client = MagicMock(return_value=self.s3_client_mock)

        # Call the function
        upload_file_to_s3(self.bucket, self.filename)

        # Assert that the upload was called with the correct arguments
        self.s3_client_mock.upload_file.assert_called_once_with(
            self.filename, self.bucket, self.filename.split('/')[-1]
        )

if __name__ == '__main__':
    unittest.main()