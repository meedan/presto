from typing import Union, List, Dict
import os
import uuid
import shutil
import pathlib

import tmkpy
import urllib.error
import urllib.request
from lib.model.model import Model
from lib import s3

class VideoModel(Model):
    def __init__(self):
        """
        Set some basic constants during operation, create local folder for tmk workspace.
        """
        self.directory = "./video_files"
        self.ffmpeg_dir = "/usr/local/bin/ffmpeg"
        pathlib.Path(self.directory).mkdir(parents=True, exist_ok=True)

    def tmk_file_path(self, filename: str, create_path: bool = True) -> str:
        """
        Sanity check for creating the directory as we created during init -
        then return filename for proposed TMK file.
        """
        if create_path:
            pathlib.Path(f"{self.directory}/").mkdir(parents=True, exist_ok=True)
        return f"{self.directory}/{filename}.tmk"

    def tmk_program_name(self) -> str:
        """
        Constant for identifying program. Needed for TMK library.
        """
        return "PrestoVideoEncoder"

    def tmk_bucket(self) -> str:
        """
        Constant for identifying bucket. Needed for uploading output.
        """
        return "presto_tmk_videos"

    def fingerprint(self, video: Dict[str, str]) -> Dict[str, str]:
        """
        Main fingerprinting routine - download video to disk, get short hash,
        then calculate larger TMK hash and upload that to S3.
        """
        temp_file_name = self.get_tempfile_for_url(video["url"])
        try:
            tmk_file_output = tmkpy.hashVideo(temp_file_name,self.ffmpeg_dir)
            hash_value=tmk_file_output.getPureAverageFeature()
            video_filename = str(uuid.uuid4())
            tmk_file_output.writeToOutputFile(
                self.tmk_file_path(video_filename),
                self.tmk_program_name()
            )
            s3.upload_file_to_s3(self.tmk_bucket(), self.tmk_file_path(video_filename))
        finally:
            os.remove(temp_file_name)
        return dict(**video, **{"bucket": self.tmk_bucket(), "outfile": self.tmk_file_path(video_filename), "hash_value": hash_value})
