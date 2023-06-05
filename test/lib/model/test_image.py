import io
import unittest
from unittest.mock import patch, Mock
from urllib.error import URLError
from typing import Dict

from lib.model.image import Model

class TestModel(unittest.TestCase):

    @patch("pdqhashing.hasher.pdq_hasher.PDQHasher")
    def test_compute_pdq(self, mock_pdq_hasher):
        mock_hasher_instance = mock_pdq_hasher.return_value
        mock_hasher_instance.fromBufferedImage.return_value.getHash.return_value.dumpBitsFlat.return_value = '1001'
        
        result = Model.compute_pdq(io.BytesIO(open("img/presto_flowchart.png", "rb").read()))
        self.assertEqual(result, '1001')

    @patch("urllib.request.urlopen")
    def test_get_iobytes_for_image(self, mock_urlopen):
        mock_response = Mock()
        mock_response.read.return_value = open("img/presto_flowchart.png", "rb").read()
        mock_urlopen.return_value = mock_response
        image_dict = {"body": {"url": "http://example.com/image.jpg"}}

        result = Model().get_iobytes_for_image(image_dict)
        self.assertIsInstance(result, io.BytesIO)
        self.assertEqual(result.read(), open("img/presto_flowchart.png", "rb").read())

    @patch("urllib.request.urlopen")
    def test_get_iobytes_for_image_raises_error(self, mock_urlopen):
        mock_urlopen.side_effect = URLError('test error')
        image_dict = {"body": {"url": "http://example.com/image.jpg"}}

        with self.assertRaises(URLError):
            Model().get_iobytes_for_image(image_dict)

    @patch.object(Model, "get_iobytes_for_image")
    @patch.object(Model, "compute_pdq")
    def test_fingerprint(self, mock_compute_pdq, mock_get_iobytes_for_image):
        mock_compute_pdq.return_value = "1001"
        mock_get_iobytes_for_image.return_value = io.BytesIO(b"image_bytes")
        image_dict = {"body": {"url": "http://example.com/image.jpg"}}
        result = Model().fingerprint(image_dict)
        self.assertEqual(result, {"hash_value": "1001"})


if __name__ == "__main__":
    unittest.main()