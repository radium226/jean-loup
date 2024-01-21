from typing import Protocol
from io import BytesIO
from pendulum import DateTime, Time

from .picture_format import PictureFormat


# We do this to be able to test stuff independently
class CanCamera(Protocol):
    def take_picture(
        self, picture_format: PictureFormat = PictureFormat.PNG
    ) -> BytesIO:
        ...


class CanPiSugar(Protocol):
    def now(self) -> DateTime:
        ...

    @property
    def wakeup_time(self) -> Time | None:
        ...

    @wakeup_time.setter
    def wakeup_time(self, value: Time | None) -> None:
        ...

    def power_off(self, delay: int = 0) -> None:
        ...


class CanSystem(Protocol):
    def now(self) -> DateTime:
        ...

    def power_off(self, delay: int) -> None:
        ...

    def start_service(self, service_name: str) -> None:
        ...

    def stop_service(self, service_name: str) -> None:
        ...

    def schedule_service(self, service_name: str, date_time: DateTime | None) -> None:
        ...
