from io import BytesIO

from .camera import Camera


class DefaultCamera(Camera):
    
    def take_picture(self) -> BytesIO:
        pass