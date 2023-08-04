import unittest
from unittest.mock import MagicMock, patch
import urllib.request
from lib.model.audio import Model
import acoustid
from acoustid import FingerprintGenerationError

from lib import schemas
class TestAudio(unittest.TestCase):
    def setUp(self):
        self.audio_model = Model()

    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    def test_fingerprint_audio_success(self, mock_request, mock_urlopen):
        mock_request.return_value = mock_request
        mock_urlopen.return_value = MagicMock(read=MagicMock(return_value=open("data/test-audio.mp3", 'rb').read()))
        audio = schemas.Message(body=schemas.AudioInput(id="123", callback_url="http://example.com/callback", url="https://example.com/audio.mp3"))
        result = self.audio_model.fingerprint(audio)
        mock_request.assert_called_once_with(audio.body.url, headers={'User-Agent': 'Mozilla/5.0'})
        mock_urlopen.assert_called_once_with(mock_request)
        self.assertEqual(list, type(result["hash_value"]))

    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    @patch('acoustid.fingerprint_file')
    @patch('acoustid.chromaprint.decode_fingerprint')
    def test_fingerprint_audio_failure(self, mock_decode_fingerprint, mock_fingerprint_file,
                                      mock_request, mock_urlopen):
        mock_fingerprint_file.side_effect = FingerprintGenerationError("Failed to generate fingerprint")
        mock_request.return_value = mock_request
        mock_urlopen.return_value = MagicMock(read=MagicMock(return_value=open("data/test-audio.mp3", 'rb').read()))
        audio = schemas.Message(body=schemas.AudioInput(id="123", callback_url="http://example.com/callback", url="https://example.com/audio.mp3"))
        result = self.audio_model.fingerprint(audio)
        mock_request.assert_called_once_with(audio.body.url, headers={'User-Agent': 'Mozilla/5.0'})
        mock_urlopen.assert_called_once_with(mock_request)
        self.assertEqual([], result["hash_value"])

if __name__ == '__main__':
    unittest.main()