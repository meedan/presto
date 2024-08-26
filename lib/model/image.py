from typing import Dict, Any
import io
import urllib.request

from lib.model.model import Model

from pdqhashing.hasher.pdq_hasher import PDQHasher
from lib import schemas

class Model(Model):
    def compute_pdq(self, iobytes: io.BytesIO) -> str:
        """Compute perceptual hash using ImageHash library
        :param im: Numpy.ndarray
        :returns: Imagehash.ImageHash
        """
        pdq_hasher = PDQHasher()
        hash_and_qual = pdq_hasher.fromBufferedImage(iobytes)
        return hash_and_qual.getHash().dumpBitsFlat()

    def get_iobytes_for_image(self, image: schemas.Message) -> io.BytesIO:
        """
        Read file as bytes after requesting based on URL.
        """
        return io.BytesIO(
            urllib.request.urlopen(
                urllib.request.Request(
                    image.body.url,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
            ).read()
        )

    def process(self, image: schemas.Message) -> schemas.GenericItem:
        """
        Generic function for returning the actual response.
        """
        return {"hash_value": self.compute_pdq(self.get_iobytes_for_image(image))}


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