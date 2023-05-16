import os
import tempfile
import urllib.request

from lib.model.model import Model
import acoustid

class AudioModel(Model):
    def audio_hasher(self, filename):
        try:
            return acoustid.chromaprint.decode_fingerprint(
                acoustid.fingerprint_file(filename)[1]
            )[0]
        except acoustid.FingerprintGenerationError:
            return []

    def respond(self, audios):
        if not isinstance(audios, list):
            audios = [audios]
        for audio in audios:
            audio["response"] = self.fingerprint_audio(audio)
        return audios

    def get_audio_tempfile(self, audio):
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(temp_file.name, 'wb') as out_file:
            out_file.write(
                urllib.request.urlopen(
                    urllib.request.Request(
                        audio["url"],
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                ).read()
            )
        return temp_file        

    def fingerprint_audio(self, audio):
        temp_file = self.get_audio_tempfile(audio)
        try:
            hash_value = self.audio_hasher(temp_file.name)
        finally:
            os.remove(temp_file.name)
        return {"hash_value": hash_value}
