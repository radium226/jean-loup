from typing import Generator
from contextlib import contextmanager
from io import BytesIO

from .logging import info

from .capabilities import CanCamera
from .picture_format import PictureFormat


class Camera(CanCamera):
    def __init__(self):
        pass

    @classmethod
    @contextmanager
    def create(cls) -> Generator["Camera", None, None]:
        info("Starting Camera service... ")
        yield Camera()
        info("Stopping Camera service... ")

    def take_picture(
        self, picture_format: PictureFormat = PictureFormat.PNG
    ) -> BytesIO:
        raise NotImplementedError()
