from typing import Dict
import io
import urllib.request

from lib.model.model import Model

from pdqhashing.hasher.pdq_hasher import PDQHasher
from lib import schemas
from torchvision import transforms
from PIL import Image
import torch
from lib.logger import logger
import requests
import numpy as np

class Model(Model):
    def compute_sscd(self, image_url: str) -> str:
        """Compute perceptual hash using ImageHash library
        :param im: Numpy.ndarray
        :returns: Imagehash.ImageHash
        """
        # pdq_hasher = PDQHasher()
        # hash_and_qual = pdq_hasher.fromBufferedImage(iobytes)
        # return hash_and_qual.getHash().dumpBitsFlat()
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

        model = torch.jit.load("sscd_disc_mixup.torchscript.pt")
        # img = Image.open(image_file_path).convert('RGB')

        response = requests.get(image_url)
        img = Image.open(io.BytesIO(response.content))
        # img = Image.open(image.body.url).convert('RGB')

        batch = small_288(img).unsqueeze(0)
        embedding = model(batch)[0, :]
        return np.asarray(embedding.detach().numpy()).tolist()

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

    def process(self, image: schemas.Message) -> schemas.ImageOutput:
        """
        Generic function for returning the actual response.
        """

        # get_image_embeddings("example-image-airplane1.png",
        #                      "/content/sscd-copy-detection/models_files/sscd_disc_mixup.torchscript.pt")
        return {"embeddings": self.compute_sscd(image.body.url)}
