from typing import Dict, Any
import os
import uuid
import shutil
import pathlib

import tmkpy
import urllib.error
import urllib.request
from lib.model.model import Model
from lib import s3
from lib import schemas
from lib.helpers import get_environment_setting

class Model(Model):
    def __init__(self):
        """
        Set some basic constants during operation, create local folder for tmk workspace.
        """
        self.directory = "./video_files"
        self.ffmpeg_dir = "/usr/local/bin/ffmpeg"
        self.model_name = os.environ.get("MODEL_NAME")
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
        prefix = (get_environment_setting("QUEUE_PREFIX") or "").replace(".", "__").replace("_", "-") or "local-"
        return f"{prefix}tmk-videos"

    def process(self, video: schemas.Message) -> schemas.GenericItem:
        """
        Main fingerprinting routine - download video to disk, get short hash,
        then calculate larger TMK hash and upload that to S3.
        """
        temp_file_name = self.get_tempfile_for_url(video.body.url)
        try:
            tmk_file_output = tmkpy.hashVideo(temp_file_name,self.ffmpeg_dir)
            hash_value=tmk_file_output.getPureAverageFeature()
            video_filename = str(uuid.uuid4())
            tmk_file_output.writeToOutputFile(
                self.tmk_file_path(video_filename),
                self.tmk_program_name()
            )
            s3.upload_file_to_s3_using_filename(self.tmk_bucket(), self.tmk_file_path(video_filename))
        finally:
            for file_path in [self.tmk_file_path(video_filename), temp_file_name]:
                if os.path.exists(file_path):
                    os.remove(file_path)
        return {"folder": self.tmk_bucket(), "filepath": self.tmk_file_path(video_filename), "hash_value": hash_value}

    @classmethod
    def validate_input(cls, data: Dict) -> None:
        """
        Validate input data. Must be implemented by all child "Model" classes.
        """
        pass

    @classmethod
    def parse_input_message(cls, data: Dict) -> Any:
        """
        Validate input data. Must be implemented by all child "Model" classes.
        """
        return None
