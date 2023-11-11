from typing import Dict
import io

from lib.model.generic_image import GenericImageModel
from lib import schemas
from torchvision import transforms
import torch
from lib.logger import logger
import numpy as np
from PIL import Image
import urllib.request

class Model(GenericImageModel):
    def __init__(self):
        super().__init__()
        #FIXME: Load from a Meedan S3 bucket
        try:
            self.model = torch.jit.load("sscd_disc_mixup.torchscript.pt")
        except:
            logging.info("Downloading SSCD model...")
            m=urllib.request.urlopen("https://dl.fbaipublicfiles.com/sscd-copy-detection/sscd_disc_mixup.torchscript.pt").read()
            with open("sscd_disc_mixup.torchscript.pt","wb") as fh:
                fh.write(m)
            self.model = torch.jit.load("sscd_disc_mixup.torchscript.pt")
        logging.info("SSCD model loaded")

    def compute_sscd(self, iobytes: io.BytesIO) -> str:
        """Compute perceptual hash using ImageHash library
        :param im: Numpy.ndarray #FIXME
        :returns: Imagehash.ImageHash #FIXME
        """
        normalize = transforms.Normalize(
            mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225],
        )
        small_288 = transforms.Compose([
            transforms.Resize(288),
            transforms.ToTensor(),
            normalize,
        ])
        skew_320 = transforms.Compose([
            transforms.Resize([320, 320]),
            transforms.ToTensor(),
            normalize,
        ])

        image = Image.open(iobytes)
        batch = small_288(image).unsqueeze(0)
        embedding = self.model(batch)[0, :]
        return np.asarray(embedding.detach().numpy()).tolist()

    def compute_imagehash(self, iobytes: io.BytesIO) -> str:
        return self.compute_sscd(iobytes)
