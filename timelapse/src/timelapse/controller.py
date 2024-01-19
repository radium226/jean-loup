from pathlib import Path
from pendulum import DateTime
from io import BytesIO
from subprocess import run, PIPE

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

    DEFAULT_DELAY_IN_MINUTES = 30

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
        info(f"state={state}")
        match (
            state,
            event_type,
        ):
            case (
                State(wakeup_time, current_date_time), 
                EventType.TIMER_TRIGGERED,
            ):
                info("Timer triggered! ")
                picture_file_path = self._generate_picture_file_path(
                    current_date_time, PictureFormat.PNG
                )
                self.take_picture(picture_file_path)

                # Setting next wakeup time
                wakeup_time = wakeup_time or current_date_time.time()
                wakeup_date_time = DateTime.combine(current_date_time.date(), wakeup_time)
                next_wakeup_time = wakeup_date_time.add(minutes=self.DEFAULT_DELAY_IN_MINUTES)
                self.schedule_wakeup(next_wakeup_time)
                

            case (
                State(wakeup_time, current_date_time),
                EventType.POWERED_ON,
            ):
                info("Powered on! ")
                current_time = current_date_time.time()
                delay = current_time - wakeup_time if wakeup_time else None
                info(f"delay={delay} ")
                # If it has been powered off for a timelapse
                if delay is None or delay.in_seconds() < 0 or delay.in_seconds() > 60:
                    info("Starting services... ")
                    self.start_access_point()
                    self.start_website()
                    if wakeup_time:
                        day_offset = 1 if current_time > wakeup_time else 0
                        wakeup_date_time = DateTime.combine(current_date_time.date(), wakeup_time).add(days=day_offset)
                        self.schedule_wakeup(wakeup_date_time)
                else:
                    info("Taking picture for timelapse and powering off... ")
                    # Taking picture
                    picture_file_path = self._generate_picture_file_path(
                        current_date_time, PictureFormat.PNG
                    )
                    self.take_picture(picture_file_path)

                    # Setting next wakeup time
                    wakeup_time = wakeup_time or current_date_time.time()
                    wakeup_date_time = DateTime.combine(current_date_time.date(), wakeup_time)
                    next_wakeup_time = wakeup_date_time.add(minutes=self.DEFAULT_DELAY_IN_MINUTES)
                    self.schedule_wakeup(next_wakeup_time)

                    # Powering off
                    self.power_off()

            case (
                State(_, current_date_time),
                EventType.CUSTOM_BUTTON_LONG_TAPPED,
            ):
                info("Custom button long tapped! ")
                info("Schedule wakeup time! ... ")
                first_wakeup_time = current_date_time.add(minutes=self.DEFAULT_DELAY_IN_MINUTES)
                self.schedule_wakeup(first_wakeup_time)

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
        self.pisugar.power_off(delay=20)
        self.system.power_off(delay=5)

    def schedule_wakeup(self, date_time: DateTime | None) -> None:
        self.pisugar.wakeup_time = date_time.time() if date_time else None
        if date_time:
            self.system.schedule_service("timelapse-handle-event@timer-triggered", date_time)
        else:
            # FIXME: We're fucked here!
            pass

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

    def save_picture(self, content: BytesIO) -> Path:
        current_date_time = self.pisugar.now()

        file_path = self._generate_picture_file_path(current_date_time, PictureFormat.PNG) # FIXME: We need to get rid of this PNG stuff
        with file_path.open("wb") as f:
            f.write(content.read())
        return file_path
    
    def list_pictures(self) -> list[Path]:
        return list((self.data_folder_path / "pictures").glob("*.png"))
    
    def generate_tumbnail(self, file_path: Path) -> BytesIO:
        command = [
            "ffmpeg",
            "-hide_banner", "-loglevel", "error",
            "-i", f"{file_path}",
            "-vf",
            "scale=320:-1",
            "-frames:v", "1",
            "-f", "image2", 
            "-c", "png",
            "-",
        ]
        
        return BytesIO(run(command, stdout=PIPE, check=True).stdout)
