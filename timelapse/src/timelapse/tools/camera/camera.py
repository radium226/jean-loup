from typing import Protocol
from io import BytesIO


class Camera(Protocol):
    
    def take_picture(self) -> BytesIO:
        ...