from typing import Generator
from contextlib import contextmanager
import pendulum
from pendulum import DateTime

from .logging import info


class PiSugar:

    def __init__(self):
        pass

    
    @classmethod
    @contextmanager
    def create(cls) -> Generator["PiSugar", None, None]:
        info("Starting PiSugar service... ")
        yield PiSugar()
        info("Stopping PiSugar service... ")

    def now(self) -> DateTime:
        # FIXME: We should ask to the PiSugar RTC
        return pendulum.now()
    
    @property
    def wake_up_at(self) -> DateTime | None:
        return None
    
    def power_off(self, delay: int) -> None:
        pass