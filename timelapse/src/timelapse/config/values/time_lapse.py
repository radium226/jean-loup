from pydantic import BaseModel

from .time import Time


class TimeLapse(BaseModel):

    enabled: bool

    wakeup_time: Time