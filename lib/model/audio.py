from typing import Union, List, Dict
import os
import tempfile

from lib.model.model import Model
import acoustid

class Model(Model):
    def audio_hasher(self, filename: str) -> List[int]:
        """
        Given a filename corresponding to an audio clip, generate the acoustid fingerprint.
        They are lists of integers.
        """
        try:
            return acoustid.chromaprint.decode_fingerprint(
                acoustid.fingerprint_file(filename)[1]
            )[0]
        except acoustid.FingerprintGenerationError:
            return []

    def fingerprint(self, audio: Dict[str, str]) -> Dict[str, Union[str, List[int]]]:
        temp_file_name = self.get_tempfile_for_url(audio.get("body", {})["url"])
        try:
            hash_value = self.audio_hasher(temp_file_name)
        finally:
            os.remove(temp_file_name)
        return {"hash_value": hash_value}
