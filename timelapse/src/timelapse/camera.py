from typing import Generator
from contextlib import contextmanager
from io import BytesIO
from subprocess import run, PIPE

from .logging import info

from .capabilities import CanCamera
from .picture_format import PictureFormat


ENCODINGS_BY_PICTURE_FORMAT = {
    PictureFormat.JPEG: "jpeg",
    PictureFormat.PNG: "png",
}


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
        command = [
            "rpicam-still",
            "--nopreview",
            "--immediate",
            "--autofocus-on-capture",
            "--encoding", ENCODINGS_BY_PICTURE_FORMAT[picture_format],
            "--output", "-"
        ]
        process = run(command, stdout=PIPE)
        if process.returncode != 0:
            raise Exception("Unable to take picture! ")
        
        return BytesIO(process.stdout)
