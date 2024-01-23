import pendulum
from pendulum import DateTime, Time
from io import BytesIO
from pathlib import Path

from timelapse.services import (
    Camera,
    PiSugar,
    System,
    Storage,
)

from timelapse.models import (
    PictureFormat,
    Picture,
    PictureIntent,
    PictureID,
)


class PiSugarMock(PiSugar):

    def __init__(self):
        self.is_powered_on: bool = True
        self.override_now: DateTime | None = None
        self._wakeup_time: Time | None = None

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

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


class SystemMock(System):
    def __init__(self):
        self.scheduled_services: list[tuple[str, DateTime]] = []
        self.services: list[str] = []
        self.override_now: DateTime | None = None
        self.is_powered_on: bool = True

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def now(self) -> DateTime:
        return self.override_now or pendulum.now()

    def power_off(self, delay: int) -> None:
        print(f"Powering off (in {delay}s)! ")
        self.is_powered_on = False

    def start_service(self, service_name: str) -> None:
        print(f"Starting {service_name} service! ")
        self.services.append(service_name)

    def stop_service(self, service_name: str) -> None:
        print(f"Stopping {service_name} service! ")
        self.services.remove(service_name)

    def schedule_service(self, service_name: str, date_time: DateTime | None) -> None:
        if date_time is None:
            print(f"Unscheduling {service_name} service! ")
            self.scheduled_services = [
                scheduled_service
                for scheduled_service in self.scheduled_services
                if scheduled_service[0] != service_name
            ]
        else:
            self.scheduled_services.append((service_name, date_time, ))


class CameraMock(Camera):
    def __init__(self):
        self.pictures_taken: list[tuple[DateTime, BytesIO]] = []

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def take_picture(
        self, format: PictureFormat
    ) -> BytesIO:
        print("Taking picture! ")
        date_time = pendulum.now()
        file_extension = format.value
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


class StorageMock(Storage):

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def list_pictures(self) -> list[Picture]:
        return []
    
    def save_picture(self, date_time: DateTime, intent: PictureIntent, content: BytesIO) -> Picture:
        return Picture(
            date_time=date_time,
            intent=intent,
            file_path=Path(""),
        )
    
    def load_picture_content(self, picture_or_picture_id: Picture | PictureID) -> BytesIO:
        raise Exception("Not implemented! ")
    
    def load_picture_thumbnail(self, picture_or_picture_id: Picture | PictureID) -> BytesIO:
        raise Exception("Not implemented! ")