from lib.model.model import Model

from lib import schemas
import urllib.request
import io

class GenericImageModel(Model):

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

        return self.compute_imagehash(self.get_iobytes_for_image(image))