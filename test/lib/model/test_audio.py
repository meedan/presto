import unittest
from unittest.mock import MagicMock, patch
import urllib.request
from lib.model.audio import AudioModel
import acoustid
from acoustid import FingerprintGenerationError


class TestAudio(unittest.TestCase):
    def setUp(self):
        self.audio_model = AudioModel()

    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    def test_fingerprint_audio_success(self, mock_request, mock_urlopen):
        # Mock successful fingerprint generation
        # mock_decode_fingerprint.return_value = (12345,)
        # mock_fingerprint_file.return_value = (4.3, b'AQAAAA')
        mock_request.return_value = mock_request
        mock_urlopen.return_value = MagicMock(read=MagicMock(return_value=open("data/test-audio.mp3", 'rb').read()))

        # Call the function
        audio = {"url": "https://example.com/audio.mp3"}
        result = self.audio_model.fingerprint_audio(audio)

        # Assert that the functions were called with the correct arguments
        mock_request.assert_called_once_with(audio["url"], headers={'User-Agent': 'Mozilla/5.0'})
        mock_urlopen.assert_called_once_with(mock_request)
        print(result)
        self.assertEqual(list, type(result["hash_value"]))

    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    @patch('acoustid.fingerprint_file')
    @patch('acoustid.chromaprint.decode_fingerprint')
    def test_fingerprint_audio_failure(self, mock_decode_fingerprint, mock_fingerprint_file,
                                      mock_request, mock_urlopen):
        # Mock failed fingerprint generation
        mock_fingerprint_file.side_effect = FingerprintGenerationError("Failed to generate fingerprint")
        mock_request.return_value = mock_request
        mock_urlopen.return_value = MagicMock(read=MagicMock(return_value=open("data/test-audio.mp3", 'rb').read()))

        # Call the function
        audio = {"url": "https://example.com/audio.mp3"}
        result = self.audio_model.fingerprint_audio(audio)

        # Assert that the functions were called with the correct arguments
        mock_request.assert_called_once_with(audio["url"], headers={'User-Agent': 'Mozilla/5.0'})
        mock_urlopen.assert_called_once_with(mock_request)
        self.assertEqual([], result["hash_value"])

if __name__ == '__main__':
    unittest.main()