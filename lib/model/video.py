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
        self.directory = "./video_files"
        self.ffmpeg_dir = "/usr/local/bin/ffmpeg"
        pathlib.Path(self.directory).mkdir(parents=True, exist_ok=True)

    def respond(self, videos: Union[List[Dict[str, str]], Dict[str, str]]) -> List[Dict[str, str]]:
        if not isinstance(videos, list):
            videos = [videos]
        for video in videos:
            video["response"] = self.fingerprint_video(video)
        return videos

    def tmk_file_path(self, filename: str, create_path: bool = True) -> str:
        if create_path:
            pathlib.Path(f"{self.directory}/").mkdir(parents=True, exist_ok=True)
        return f"{self.directory}/{filename}.tmk"

    def tmk_program_name(self) -> str:
        return "PrestoVideoEncoder"

    def tmk_bucket(self) -> str:
        return "presto_tmk_videos"

    def fingerprint_video(self, video: Dict[str, str]) -> Dict[str, str]:
        temp_file_name = self.get_tempfile_for_url(video["url"])
        tmk_file_output = tmkpy.hashVideo(temp_file_name,self.ffmpeg_dir)
        hash_value=tmk_file_output.getPureAverageFeature()
        video_filename = str(uuid.uuid4())
        tmk_file_output.writeToOutputFile(
            self.tmk_file_path(video_filename),
            self.tmk_program_name()
        )
        s3.upload_file_to_s3(self.tmk_bucket(), self.tmk_file_path(video_filename))
        os.remove(temp_file_name)
        return dict(**video, **{"bucket": self.tmk_bucket(), "outfile": self.tmk_file_path(video_filename), "hash_value": hash_value})
