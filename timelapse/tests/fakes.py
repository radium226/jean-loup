import pendulum
from pendulum import DateTime, Time
from io import BytesIO
from pathlib import Path

from timelapse.capabilities import CanPiSugar, CanSystem, CanCamera
from timelapse.picture_format import PictureFormat
from timelapse.controller import FILE_EXTENSIONS_BY_PICTURE_FORMAT


class FakePiSugar(CanPiSugar):
    def __init__(self):
        self.is_powered_on: bool = True
        self.override_now: DateTime | None = None
        self._wakeup_time = None

    @property
    def wakeup_time(self) -> Time | None:
        return self._wakeup_time

    @wakeup_time.setter
    def wakeup_time(self, value: Time | None) -> None:
        print(f"Setting wakeup time at {value}! ")
        self._wakeup_time = value

    def power_off(self, delay: int = 0) -> None:
        print(f"Powering off in {delay}! ")
        self.is_powered_on = False

    def now(self) -> DateTime:
        return self.override_now or pendulum.now()


class FakeSystem(CanSystem):
    def __init__(self):
        self.services: list[str] = []
        self.override_now: DateTime | None = None
        self.is_powered_on: bool = True

    def now(self) -> DateTime:
        return self.override_now or pendulum.now()

    def power_off(self) -> None:
        print("Powering off! ")
        self.is_powered_on = False

    def start_service(self, service_name: str) -> None:
        print(f"Starting {service_name} service! ")
        self.services.append(service_name)

    def stop_service(self, service_name: str) -> None:
        print(f"Stopping {service_name} service! ")
        self.services.remove(service_name)


class FakeCamera(CanCamera):
    def __init__(self):
        self.pictures_taken: list[tuple[DateTime, BytesIO]] = []

    def take_picture(
        self, picture_format: PictureFormat = PictureFormat.PNG
    ) -> BytesIO:
        print("Taking picture! ")
        date_time = pendulum.now()
        file_extension = FILE_EXTENSIONS_BY_PICTURE_FORMAT[picture_format]
        with (
            Path(__file__).parent
            / "bamboo.{extension}".format(extension=file_extension)
        ).open("rb") as f:
            picture = BytesIO(f.read())
            self.pictures_taken.append(
                (
                    date_time,
                    picture,
                )
            )
            return picture
