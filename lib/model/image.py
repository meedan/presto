import io
import urllib.request

from lib.model.model import Model

from pdqhashing.hasher.pdq_hasher import PDQHasher

class ImageModel(Model):
    def compute_pdq(iobytes: io.BytesIO) -> str:
        """Compute perceptual hash using ImageHash library
        :param im: Numpy.ndarray
        :returns: Imagehash.ImageHash
        """
        #hash_vector, quality = pdqhash.compute(ensure_pil(im))
        #print(type(hash_vector))
        #print(hash_vector)
        #return hash_vector.ravel().tolist()
        pdq_hasher = PDQHasher()
        hash_and_qual = pdq_hasher.fromBufferedImage(iobytes)
        #hash_array =  imagehash.hex_to_hash(hash_and_qual.getHash().toHexString())
        #return  hash_array.hash.ravel().tolist()
        return hash_and_qual.getHash().dumpBitsFlat() #This is a string of 0's and 1's

    def get_iobytes_for_image(self, image: Dict[str, str]) -> io.BytesIO:
        """
        Read file as bytes after requesting based on URL.
        """
        return io.BytesIO(
            urllib.request.urlopen(
                urllib.request.Request(
                    image["url"],
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
            ).read()
        )

    def fingerprint(self, image: Dict[str, str]) -> Dict[str, str]:
        """
        Generic function for returning the actual response.
        """
        return {"hash_value": self.compute_pdq(self.get_iobytes_for_image(image))}
