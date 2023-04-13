import uuid
import shutil
import tempfile
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

    def get_tempfile(self):
        return tempfile.NamedTemporaryFile()

    def respond(self, videos):
        if not isinstance(videos, list):
            videos = [videos]
        for video in videos:
            video["response"] = self.fingerprint_video(video)
        return videos

    def tmk_file_path(self, filename, create_path=True):
        if create_path:
            pathlib.Path(f"{self.directory}/").mkdir(parents=True, exist_ok=True)
        return f"{self.directory}/{filename}.tmk"

    def tmk_program_name(self):
        return "PrestoVideoEncoder"

    def fingerprint_video(self, video):
        temp_video_file = self.get_tempfile()
        remote_request = urllib.request.Request(video["url"], headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(remote_request) as response, open(temp_video_file.name, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        tmk_file_output = tmkpy.hashVideo(temp_video_file.name,self.ffmpeg_dir)
        hash_value=tmk_file_output.getPureAverageFeature()
        video_filename = str(uuid.uuid4())
        tmk_file_output.writeToOutputFile(
            self.tmk_file_path(video_filename),
            self.tmk_program_name()
        )
        s3.upload_file_to_s3("presto_tmk_videos", self.tmk_file_path(video_filename))
        return {"outfile": self.tmk_file_path(video_filename), "hash_value": hash_value}
