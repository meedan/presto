from typing import Dict
import io

from lib.model.generic_image import GenericImageModel

from pdqhashing.hasher.pdq_hasher import PDQHasher
from lib import schemas

class Model(GenericImageModel):
    def compute_pdq(self, iobytes: io.BytesIO) -> str:
        """Compute perceptual hash using ImageHash library
        :param im: Numpy.ndarray
        :returns: Imagehash.ImageHash
        """
        pdq_hasher = PDQHasher()
        hash_and_qual = pdq_hasher.fromBufferedImage(iobytes)
        return hash_and_qual.getHash().dumpBitsFlat()

    def compute_imagehash(self, iobytes: io.BytesIO) -> str:
        return self.compute_pdq(iobytes)