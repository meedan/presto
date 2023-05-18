from typing import Union, List, Dict
import os
import tempfile

from lib.model.model import Model
import acoustid

class AudioModel(Model):
    def audio_hasher(self, filename: str) -> List[int]:
        try:
            return acoustid.chromaprint.decode_fingerprint(
                acoustid.fingerprint_file(filename)[1]
            )[0]
        except acoustid.FingerprintGenerationError:
            return []

    def respond(self, audios: Union[List[Dict[str, str]], Dict[str, str]]) -> List[Dict[str, str]]:
        if not isinstance(audios, list):
            audios = [audios]
        for audio in audios:
            audio["response"] = self.fingerprint_audio(audio)
        return audios

    def fingerprint_audio(self, audio: Dict[str, str]) -> Dict[str, Union[str, List[int]]]:
        temp_file_name = self.get_tempfile_for_url(audio["url"])
        try:
            hash_value = self.audio_hasher(temp_file_name)
        finally:
            os.remove(temp_file_name)
        return {"hash_value": hash_value}
