import unittest
from unittest.mock import ANY, MagicMock, patch

import tempfile
import shutil
import uuid
import pathlib
import urllib.request
from lib.model.video import Model
from lib import s3
import tmkpy

class TestVideoModel(unittest.TestCase):
    def setUp(self):
        self.video_model = Model()

    @patch('tempfile.NamedTemporaryFile')
    def test_get_tempfile(self, mock_named_tempfile):
        self.video_model.get_tempfile()
        mock_named_tempfile.assert_called_once()

    @patch('urllib.request.urlopen')
    @patch('tmkpy.hashVideo')
    @patch('s3.upload_file_to_s3')
    @patch('pathlib.Path')
    def test_fingerprint_video(self, mock_pathlib, mock_upload_file_to_s3,
                               mock_hash_video, mock_urlopen):
        mock_hash_video_output = MagicMock()
        mock_hash_video_output.getPureAverageFeature.return_value = "hash_value"
        mock_hash_video.return_value = mock_hash_video_output
        mock_urlopen.return_value = MagicMock(read=MagicMock(return_value=open("data/test-video.mp4", "rb").read()))
        self.video_model.fingerprint({"body": {"url": "http://example.com/video.mp4"}})
        mock_urlopen.assert_called_once()
        mock_hash_video.assert_called_once_with(ANY, "/usr/local/bin/ffmpeg")

    @patch('pathlib.Path')
    def test_tmk_file_path(self, mock_pathlib):
        mock_pathlib.return_value.mkdir.return_value = None
        result = self.video_model.tmk_file_path("test_filename")
        self.assertEqual(result, f"{self.video_model.directory}/test_filename.tmk")
        mock_pathlib.assert_called_once_with(f"{self.video_model.directory}/")
        mock_pathlib.return_value.mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_tmk_program_name(self):
        result = self.video_model.tmk_program_name()
        self.assertEqual(result, "PrestoVideoEncoder")

    def test_respond_with_single_video(self):
        video = {"body": {"url": "http://example.com/video.mp4"}}
        mock_fingerprint = MagicMock()
        self.video_model.fingerprint = mock_fingerprint
        result = self.video_model.respond(video)
        mock_fingerprint.assert_called_once_with(video)
        self.assertEqual(result, [video])

    def test_respond_with_multiple_videos(self):
        videos = [{"body": {"url": "http://example.com/video1.mp4"}}, {"body": {"url": "http://example.com/video2.mp4"}}]
        mock_fingerprint = MagicMock()
        self.video_model.fingerprint = mock_fingerprint
        result = self.video_model.respond(videos)
        mock_fingerprint.assert_called_with(videos[1])
        self.assertEqual(result, videos)