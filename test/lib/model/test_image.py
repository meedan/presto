import io
import unittest
from unittest.mock import patch, Mock
from urllib.error import URLError
from typing import Dict

from lib.model.image import Model
from lib import schemas

class TestModel(unittest.TestCase):

    @patch("pdqhashing.hasher.pdq_hasher.PDQHasher")
    def test_compute_pdq(self, mock_pdq_hasher):
        with open("img/presto_flowchart.png", "rb") as file:
            image_content = file.read()
        mock_hasher_instance = mock_pdq_hasher.return_value
        mock_hasher_instance.fromBufferedImage.return_value.getHash.return_value.dumpBitsFlat.return_value = '1001'
        result = Model().compute_pdq(io.BytesIO(image_content))
        self.assertEqual(result, '0011100000111011010110100001001110001011110100100010101011010111010110101010000111001010111000001010111111110000000101110010000011111110111110100100011111010010110110101111101100111001000000010010100101010111110001001101101011000110001000001110010000111100')

    @patch("urllib.request.urlopen")
    def test_get_iobytes_for_image(self, mock_urlopen):
        with open("img/presto_flowchart.png", "rb") as file:
            image_content = file.read()
        mock_response = Mock()
        mock_response.read.return_value = image_content
        mock_urlopen.return_value = mock_response
        image = schemas.parse_message({"body": {"id": "123", "callback_url": "http://example.com?callback", "url": "http://example.com/image.jpg"}, "model_name": "audio__Model"})
        result = Model().get_iobytes_for_image(image)
        self.assertIsInstance(result, io.BytesIO)
        self.assertEqual(result.read(), image_content)

    @patch("urllib.request.urlopen")
    def test_get_iobytes_for_image_raises_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError('test error')
        image = schemas.parse_message({"body": {"id": "123", "callback_url": "http://example.com?callback", "url": "http://example.com/image.jpg"}, "model_name": "audio__Model"})
        with self.assertRaises(URLError):
            Model().get_iobytes_for_image(image)

    @patch.object(Model, "get_iobytes_for_image")
    @patch.object(Model, "compute_pdq")
    def test_process(self, mock_compute_pdq, mock_get_iobytes_for_image):
        mock_compute_pdq.return_value = "1001"
        mock_get_iobytes_for_image.return_value = io.BytesIO(b"image_bytes")
        image = schemas.parse_message({"body": {"id": "123", "callback_url": "http://example.com?callback", "url": "http://example.com/image.jpg"}, "model_name": "audio__Model"})
        result = Model().process(image)
        self.assertEqual(result, "1001")


if __name__ == "__main__":
    unittest.main()
