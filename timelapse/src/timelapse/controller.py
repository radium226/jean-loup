from pathlib import Path
from pendulum import DateTime, Time
from io import BytesIO

from contextlib import contextmanager, ExitStack
from typing import Generator, overload

from .logging import info
from .capabilities import CanCamera, CanSystem, CanPiSugar

from .pisugar import PiSugar
from .system import System
from .camera import Camera

from .event_type import EventType
from .state import State
from .picture_format import PictureFormat


PICTURE_FORMATS_BY_FILE_EXTENSION = {
    "jpg": PictureFormat.JPEG,
    "png": PictureFormat.PNG,
}

FILE_EXTENSIONS_BY_PICTURE_FORMAT = {
    picture_format: file_extension
    for picture_format, file_extension in PICTURE_FORMATS_BY_FILE_EXTENSION.items()
}


class Controller:
    DEFAULT_DATA_FOLDER_PATH = Path("/var/lib/timelapse")

    DEFAULT_PICTURE_FORMAT = PictureFormat.PNG

    def __init__(
        self, pisugar: CanPiSugar, system: CanSystem, camera: CanCamera, data_folder_path: Path = DEFAULT_DATA_FOLDER_PATH
    ) -> None:
        self.pisugar = pisugar
        self.system = system
        self.camera = camera

        self.data_folder_path = data_folder_path

    @property
    def current_state(self) -> State:
        return State(
            wakeup_time=self.pisugar.wakeup_time,
            current_date_time=self.pisugar.now(),
        )

    @classmethod
    @contextmanager
    def create(cls) -> Generator["Controller", None, None]:
        with ExitStack() as exit_stack:
            pisugar = exit_stack.enter_context(PiSugar.create())
            system = exit_stack.enter_context(System.create())
            camera = exit_stack.enter_context(Camera.create())
            info("Starting Controller... ")
            yield Controller(
                pisugar=pisugar,
                system=system,
                camera=camera,
            )
            info("Stopping Controller... ")

    def handle_event(self, event_type: EventType) -> None:
        state = self.current_state
        match (
            state,
            event_type,
        ):
            case (
                State(wakeup_time, current_date_time),
                EventType.POWERED_ON,
            ):
                info("Powered on! ")
                current_time = current_date_time.time()
                delay = current_time - wakeup_time if wakeup_time else None
                info(f"delay={delay} ")
                # If it has been powered off for a timelapse
                if delay is None or delay.in_seconds() > 60:
                    info("Starting services... ")
                    self.start_access_point()
                    self.start_website()
                else:
                    info("Taking picture for timelapse and powering off... ")
                    # Taking picture
                    picture_file_path = self._generate_picture_file_path(
                        current_date_time, PictureFormat.PNG
                    )
                    self.take_picture(picture_file_path)

                    # Setting next wakeup time
                    next_wakeup_time = (wakeup_time or current_date_time.time()).add(
                        minutes=5
                    )
                    self.schedule_wakeup(next_wakeup_time)

                    # Powering off
                    self.power_off()

            case (
                State(_, current_date_time),
                EventType.CUSTOM_BUTTON_LONG_TAPPED,
            ):
                info("Custom button long tapped! ")
                info("Schedule wakeup time! ... ")
                current_time = current_date_time.time()
                self.schedule_wakeup(current_time.add(minutes=5))

            case (
                State(_, current_date_time),
                EventType.CUSTOM_BUTTON_SINGLE_TAPPED,
            ):
                info("Custom button single tapped! ")
                info("Taking picture... ")
                picture_file_path = self._generate_picture_file_path(
                    current_date_time, PictureFormat.PNG
                )
                self.take_picture(picture_file_path)

            case (
                State(_, _),
                EventType.POWER_BUTTON_TAPPED,
            ):
                info("Power button tapped! ")
                info("Powering off... ")
                self.power_off()

    def start_access_point(self) -> None:
        self.system.start_service("timelapse-hotspot")

    def start_website(self) -> None:
        self.system.start_service("timelapse-website")

    @overload
    def take_picture(self) -> BytesIO:
        ...

    @overload
    def take_picture(self, __file_path: Path) -> None:
        ...

    @overload
    def take_picture(self, __file_path: Path, __picture_format: PictureFormat) -> None:
        ...

    @overload
    def take_picture(self, __picture_format: PictureFormat) -> BytesIO:
        ...

    def take_picture(
        self,
        file_path_or_picture_format: Path | PictureFormat | None = None,
        picture_format_or_none: PictureFormat | None = None,
    ) -> BytesIO | None:
        if file_path_or_picture_format is None and picture_format_or_none is None:
            file_path = None
            picture_format = self.DEFAULT_PICTURE_FORMAT
        elif (
            isinstance(file_path_or_picture_format, Path)
            and picture_format_or_none is None
        ):
            file_path = file_path_or_picture_format
            file_extension = (
                file_suffix[1:]
                if len(file_suffix := file_path.suffix) > 0
                else file_suffix
            )
            picture_format = PICTURE_FORMATS_BY_FILE_EXTENSION.get(
                file_extension, self.DEFAULT_PICTURE_FORMAT
            )
        elif (
            isinstance(file_path_or_picture_format, PictureFormat)
            and picture_format_or_none is None
        ):
            file_path = None
            picture_format = file_path_or_picture_format
        elif file_path_or_picture_format is None and isinstance(
            picture_format_or_none, PictureFormat
        ):
            file_path = None
            picture_format = picture_format_or_none
        elif isinstance(file_path_or_picture_format, Path) and isinstance(
            picture_format_or_none, PictureFormat
        ):
            file_path = file_path_or_picture_format
            picture_format = picture_format_or_none
        else:
            raise Exception("Invalid arguments")

        # Actually taking picture
        picture = self.camera.take_picture(picture_format or PictureFormat.PNG)

        # Optionally saving the picture in a file
        if file_path:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, "wb") as file:
                file.write(picture.getbuffer())
            return None
        else:
            return picture

    def power_off(self) -> None:
        self.pisugar.power_off(delay=30)
        self.system.power_off()

    def schedule_wakeup(self, time: Time | None) -> None:
        self.pisugar.wakeup_time = time

    def _generate_picture_file_path(
        self, current_date_time: DateTime, picture_format: PictureFormat
    ) -> Path:
        folder_path = self.data_folder_path / "pictures"
        file_extension = FILE_EXTENSIONS_BY_PICTURE_FORMAT[picture_format]
        file_path = folder_path / (
            "{date_time}.{extension}".format(
                date_time=current_date_time.format("YYYY-MM-DD_HH-mm-ss"),
                extension=file_extension,
            )
        )
        return file_path

    def now(self) -> DateTime:
        return self.pisugar.now()
