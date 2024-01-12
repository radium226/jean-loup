from typing import Generator
from contextlib import contextmanager
import pendulum
from pendulum import Time, DateTime

from .logging import info
from .capabilities import CanPiSugar


class PiSugar(CanPiSugar):
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
    def wakeup_time(self) -> Time | None:
        return None

    @wakeup_time.setter
    def wakeup_time(self, value: Time | None) -> None:
        pass

    def power_off(self, delay: int = 0) -> None:
        pass
