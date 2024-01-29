from typing import Dict
import io

# from lib.model.generic_image import GenericImageModel
from lib.model.model import Model
from lib import schemas
from torchvision import transforms
import torch
from lib.logger import logger
import numpy as np
from PIL import Image
import urllib.request

IMAGENET_NORMALIZATION_MEAN = [0.485, 0.456, 0.406]
IMAGENET_NORMALIZATION_STD = [0.229, 0.224, 0.225]
class Model(Model):
    def __init__(self):
        super().__init__()
        #FIXME: Load from a Meedan S3 bucket
        try:
            self.model = torch.jit.load("sscd_disc_mixup.torchscript.pt")
        except ValueError:
            logger.info("Downloading SSCD model...")
            m=urllib.request.urlopen("https://dl.fbaipublicfiles.com/sscd-copy-detection/sscd_disc_mixup.torchscript.pt").read()
            with open("sscd_disc_mixup.torchscript.pt","wb") as fh:
                fh.write(m)
            self.model = torch.jit.load("sscd_disc_mixup.torchscript.pt")
        logger.info("SSCD model loaded")

    def compute_sscd(self, iobytes: io.BytesIO) -> str:
        """Compute perceptual hash using ImageHash library
        :param im: Numpy.ndarray #FIXME
        :returns: Imagehash.ImageHash #FIXME
        """
        # from SSCD-copy-detection readme https://github.com/facebookresearch/sscd-copy-detection/tree/main#preprocessing
        # Normalization using the mean and std of Imagenet
        normalize = transforms.Normalize(
            mean = IMAGENET_NORMALIZATION_MEAN , std = IMAGENET_NORMALIZATION_STD,
        )
        # It is recommended by publishers of SSCD-copy-detection to preprocess images for inference either resizing the small edge to 288 or resizing the image to a square tensor.
        # resizing the image to a square tensor is more effecient on gpus but can lead to skewed images and so loss of information. So, we are resizing the small edge to 288
        small_288 = transforms.Compose([
            transforms.Resize(288),
            transforms.ToTensor(),
            normalize,
        ])
        # Keeping the code example of resizing the image to a square tensor
        # skew_320 = transforms.Compose([
        #     transforms.Resize([320, 320]),
        #     transforms.ToTensor(),
        #     normalize,
        # ])

        image = Image.open(iobytes)
        batch = small_288(image).unsqueeze(0)
        embedding = self.model(batch)[0, :]
        return np.asarray(embedding.detach().numpy()).tolist()

    def compute_imagehash(self, iobytes: io.BytesIO) -> str:
        return self.compute_sscd(iobytes)
