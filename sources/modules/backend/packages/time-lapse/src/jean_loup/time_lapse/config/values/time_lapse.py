from pydantic import BaseModel

from ...types_for_pydantic import Time


class TimeLapse(BaseModel):

    enabled: bool

    wakeup_time: Time

    delay_in_minutes: int

    threshold_in_seconds: int