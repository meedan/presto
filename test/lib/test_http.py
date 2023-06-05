from fastapi.testclient import TestClient
import unittest
from unittest.mock import AsyncMock, patch
from lib.http import app
from lib.queue.queue import Queue

class TestFingerprintItem(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch.object(Queue, 'create', new_callable=AsyncMock)
    @patch.object(Queue, 'push_message')
    def test_fingerprint_item(self, mock_push_message, mock_create):
        mock_queue = mock_create.return_value
        mock_queue.input_queue_name = "input_queue"
        mock_queue.output_queue_name = "output_queue"

        test_data = {"key": "value"}

        response = self.client.post("/fingerprint_item/test_fingerprinter", json=test_data)
        mock_create.assert_called_once_with("test_fingerprinter", "test_fingerprinter-output")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Message pushed successfully"})


    @patch('lib.http.post_url')
    def test_trigger_callback(self, mock_post_url):
        mock_post_url.return_value = None
        message_with_callback = {"some_key": "some_value", "callback_url": "http://example.com"}
        response = self.client.post("/trigger_callback", json=message_with_callback)
        mock_post_url.assert_called_with("http://example.com", message_with_callback)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Message Called Back Successfully"})


    @patch('lib.http.post_url')
    def test_trigger_callback_fail(self, mock_post_url):
        mock_post_url.return_value = None
        message_with_callback = {"some_key": "some_value"}
        response = self.client.post("/trigger_callback", json=message_with_callback)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "No Message Callback, Passing"})

if __name__ == "__main__":
    unittest.main()
