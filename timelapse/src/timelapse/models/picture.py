from pydantic import BaseModel

from ..types_for_pydantic import DateTime, Path

from .picture_intent import PictureIntent


class Picture(BaseModel):
    date_time: DateTime

    intent: PictureIntent
    
    file_path: Path

    content: bytes | None = None