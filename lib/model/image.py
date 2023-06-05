from typing import Dict
import io
import urllib.request

from lib.model.model import Model

from pdqhashing.hasher.pdq_hasher import PDQHasher

class Model(Model):
    def compute_pdq(iobytes: io.BytesIO) -> str:
        """Compute perceptual hash using ImageHash library
        :param im: Numpy.ndarray
        :returns: Imagehash.ImageHash
        """
        pdq_hasher = PDQHasher()
        hash_and_qual = pdq_hasher.fromBufferedImage(iobytes)
        return hash_and_qual.getHash().dumpBitsFlat()

    def get_iobytes_for_image(self, image: Dict[str, str]) -> io.BytesIO:
        """
        Read file as bytes after requesting based on URL.
        """
        return io.BytesIO(
            urllib.request.urlopen(
                urllib.request.Request(
                    image.get("body", {})["url"],
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
            ).read()
        )

    def fingerprint(self, image: Dict[str, str]) -> Dict[str, str]:
        """
        Generic function for returning the actual response.
        """
        return {"hash_value": self.compute_pdq(self.get_iobytes_for_image(image))}
