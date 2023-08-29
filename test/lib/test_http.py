from fastapi.testclient import TestClient
import unittest
from unittest.mock import patch
from lib.http import app
from lib.queue.worker import QueueWorker

class TestProcessItem(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch.object(QueueWorker, 'create')
    @patch.object(QueueWorker, 'push_message')
    def test_process_item(self, mock_push_message, mock_create):
        mock_queue = mock_create.return_value
        mock_queue.input_queue_name = "input_queue"
        mock_queue.output_queue_name = "output_queue"

        test_data = {"id": 1, "callback_url": "http://example.com", "text": "This is a test"}

        response = self.client.post("/process_item/test_process", json=test_data)
        mock_create.assert_called_once_with("test_process")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Message pushed successfully"})


    @patch('lib.http.post_url')
    def test_trigger_callback(self, mock_post_url):
        mock_post_url.return_value = None
        message_with_callback = {"id": 1, "callback_url": "http://example.com", "text": "This is a test"}
        response = self.client.post("/trigger_callback", json=message_with_callback)
        mock_post_url.assert_called_with("http://example.com", message_with_callback)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Message Called Back Successfully"})


    @patch('lib.http.post_url')
    def test_trigger_callback_fail(self, mock_post_url):
        mock_post_url.return_value = None
        message_with_callback = {"id": 1, "callback_url": "http://example.com", "text": "This is a test"}
        response = self.client.post("/trigger_callback", json=message_with_callback)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "No Message Callback, Passing"})

    def test_trigger_callback_fail(self):
        response = self.client.get("/ping")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"pong": 1})

if __name__ == "__main__":
    unittest.main()
