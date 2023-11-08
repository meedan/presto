import unittest
from unittest.mock import MagicMock, patch
import urllib.request
from lib.model.audio import Model
import acoustid
from acoustid import FingerprintGenerationError

from lib import schemas
FINGERPRINT_RESPONSE = (170.6, b'AQAA3VFYJYrGJMj74EOZUCfCHGqYLBZO8UiX5bie47sCV0xwBTe49IiVHHrQnIImJyP-44rxI2cYiuiHMCMDPcqJrBcwnYeryBX6rccR_4Iy_YhfXESzqELJ5ASTLwhvNM94KDp9_IB_6NqDZ5I9_IWYvDiNCc1z8IeuHXkYpfhSg8su3M2K5lkrFM-PK3mQH8lznEpidLEoNAeLyWispQpqvfgRZjp0lHaENAmzBeamoRIZMrha5IsyHM6H7-jRhJlSBU1FLgiv4xlKUQmNptGOU3jzIj80Jk5xsQp0UegxJtmSCpeS5PiDozz0MAb5BG5z9MEPIcy0HeWD58M_4sotlNOF8UeuLJEgJt4xkUee4cflI1nMI4uciBLeGu9z9NjH4x9iSXoELYs04pqCSCvx5ei1Tzi3NMFRmsa2DD2POxVCR4IPMSfySC-u0EKuE6IOqz_6zJh8BzZlgc1IQkyTGdeLa4cT7bi2E30e_OgTI4xDPCGLJ_gvZHlwT7EgJc2XIBY_4fnBPENC_YilsGjDJzhJoeyCJn9A1kaeDUw4VA_-41uDGycO8w_eWlCU66iio0eYL8hVK_gD5QlyMR7hzzh-vDm6JE_hcTpq5cFTdFcKZfHxRMTZCS2VHKdOfDve5Hh0hCV9JEtMSbhxSSMuHU9y4kaTx5guHIGsoEAAwoASjmDlkSAEOCSoQEw4IDgghiguAEZAAMaAAYYAhBhACBEiiAGAIUCUUUgSESjgSBlKjZEEEIAFUEIBBRBinAAplFJKAIYQEAQSA4ywACkjgBFMAEoAQgYQwARB1gFmBCAECAAIMYYIoBxBBAAAFCKAAEgIBAQgAghgihIWBACEIUEIJEZIZIBRACGAGAEEIAGAUIBIhBCgRkI')
class TestAudio(unittest.TestCase):
    def setUp(self):
        self.audio_model = Model()

    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    @patch('acoustid.fingerprint_file')
    def test_process_audio_success(self, mock_fingerprint_file, mock_request, mock_urlopen):
        mock_fingerprint_file.return_value = FINGERPRINT_RESPONSE
        mock_request.return_value = mock_request

        # Use the `with` statement for proper file handling
        with open("data/test-audio.mp3", 'rb') as f:
            contents = f.read()

        mock_urlopen.return_value = MagicMock(read=MagicMock(return_value=contents))

        audio = schemas.Message(body={"id": "123", "callback_url": "http://example.com/callback", "url": "https://example.com/audio.mp3"}, model_name="audio__Model")
        result = self.audio_model.process(audio)
        mock_request.assert_called_once_with(audio.body.url, headers={'User-Agent': 'Mozilla/5.0'})
        mock_urlopen.assert_called_once_with(mock_request)
        self.assertEqual(list, type(result))

    @patch('urllib.request.urlopen')
    @patch('urllib.request.Request')
    @patch('acoustid.fingerprint_file')
    @patch('acoustid.chromaprint.decode_fingerprint')
    def test_process_audio_failure(self, mock_decode_fingerprint, mock_fingerprint_file,
                                      mock_request, mock_urlopen):
        mock_fingerprint_file.side_effect = FingerprintGenerationError("Failed to generate fingerprint")
        mock_request.return_value = mock_request

        # Use the `with` statement for proper file handling
        with open("data/test-audio.mp3", 'rb') as f:
            contents = f.read()

        mock_urlopen.return_value = MagicMock(read=MagicMock(return_value=contents))

        audio = schemas.Message(body={"id": "123", "callback_url": "http://example.com/callback", "url": "https://example.com/audio.mp3"}, model_name="audio__Model")
        result = self.audio_model.process(audio)
        mock_request.assert_called_once_with(audio.body.url, headers={'User-Agent': 'Mozilla/5.0'})
        mock_urlopen.assert_called_once_with(mock_request)
        self.assertEqual([], result)

if __name__ == '__main__':
    unittest.main()
