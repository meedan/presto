import urllib.request
import tempfile

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

    def get_tempfile(self):
        return tempfile.NamedTemporaryFile()

    def respond(self, audios):
        if not isinstance(audios, list):
            audios = [audios]
        for audio in audios:
            audio["response"] = fingerprint_audio(audio)
        return videos

    def fingerprint_audio(self, audio):
        remote_request = urllib.request.Request(audio["url"], headers={'User-Agent': 'Mozilla/5.0'})
        remote_response = urllib.request.urlopen(remote_request)
        temp_file = self.get_tempfile()
        with open(temp_file.name, 'wb') as out_file:
            out_file.write(remote_response.read())
        return {"hash_value": self.audio_hasher(temp_file.name)}
