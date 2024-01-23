from pydantic import BaseModel

from ..types_for_pydantic import DateTime

from .picture_intent import PictureIntent
from .picture_id import PictureID


class Picture(BaseModel):
    id: PictureID

    date_time: DateTime

    intent: PictureIntent

    content: bytes | None = None