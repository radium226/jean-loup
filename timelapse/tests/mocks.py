import pendulum
from pendulum import DateTime, Time
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

    is_powered_on: bool
    override_now: DateTime | None
    _wakeup_time: Time | None

    def __init__(self):
        self.is_powered_on = True
        self.override_now = None
        self._wakeup_time = None

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

    scheduled_services: list[tuple[str, DateTime]]
    services: list[str]
    override_now: DateTime | None
    is_powered_on: bool

    def __init__(self):
        self.scheduled_services = []
        self.services = []
        self.override_now = None
        self.is_powered_on = True

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
    pictures_taken: list[tuple[DateTime, bytes]]
    def __init__(self):
        self.pictures_taken = []

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def take_picture(
        self, format: PictureFormat
    ) -> bytes:
        print("Taking picture! ")
        date_time = pendulum.now()
        file_extension = format.value
        content_file_path = Path(__file__).parent / "bamboo.{extension}".format(extension=file_extension)
        content = content_file_path.read_bytes()
        self.pictures_taken.append(
            (
                date_time,
                content,
            )
        )
        return content


class StorageMock(Storage):

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def list_pictures(self) -> list[Picture]:
        return []
    
    def save_picture(self, date_time: DateTime, intent: PictureIntent, content: bytes) -> Picture:
        return Picture(
            id=date_time.format("YYYY-MM-DD_HH-mm-ss"),
            date_time=date_time,
            intent=intent,
        )
    
    def load_picture_content(self, picture_or_picture_id: Picture | PictureID) -> bytes | None:
        raise Exception("Not implemented! ")
    
    def load_picture_thumbnail(self, picture_or_picture_id: Picture | PictureID) -> bytes | None:
        raise Exception("Not implemented! ")