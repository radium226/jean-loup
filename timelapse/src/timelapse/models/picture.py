from pydantic import BaseModel
from pathlib import Path

from ..types_for_pydantic import DateTime

from .picture_intent import PictureIntent


class Picture(BaseModel):
    date_time: DateTime

    intent: PictureIntent
    
    file_path: Path

    content: bytes | None = None