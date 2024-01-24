from typing import Protocol
from subprocess import run, PIPE
from pathlib import Path
from time import sleep

from ..logging import warn, debug
from ..models import PictureFormat


class Camera(Protocol):

    def __enter__(self):
        ...

    def __exit__(self, type, value, traceback):
        ...
    
    def take_picture(self, format: PictureFormat) -> bytes:
        ...

    @classmethod
    def genuine(cls) -> "Camera":
        debug("Using genuine camera! ")
        return _GenuineCamera()
    
    @classmethod
    def fake(cls) -> "Camera":
        warn("Using fake camera! ")
        return _FakeCamera()


class _GenuineCamera(Camera):

    ENCODINGS_BY_PICTURE_FORMAT = {
        PictureFormat.JPEG: "jpeg",
        PictureFormat.PNG: "png",
    }

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def take_picture(self, format: PictureFormat) -> bytes:
        command = [
            "rpicam-still",
                "--nopreview",
                "--immediate",
                "--autofocus-on-capture",
                "--encoding", self.ENCODINGS_BY_PICTURE_FORMAT[format],
                "--output", "-"
        ]
        process = run(command, stdout=PIPE, check=True)
        return process.stdout
    


class _FakeCamera(Camera):

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def take_picture(self, format: PictureFormat) -> bytes:
        debug(f"Taking picture (format={format})... ")
        sleep(2)
        with ( Path(__file__).parent / f"fake.{format}" ).open("rb") as file:
            return file.read()