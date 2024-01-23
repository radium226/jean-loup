from contextlib import ExitStack
from pendulum import DateTime, Time
from pathlib import Path
from subprocess import run, PIPE
from io import BytesIO

from ..config import Config
from ..services import (
    PiSugar,
    Camera,
    System,
    Storage,
)
from ..logging import (
    info,
)
from ..models import (
    State,
    EventType,
    PictureFormat,
    PictureIntent,
    Picture,
    PictureID,
)


class Controller:

    config: Config
    exit_stack: ExitStack
    camera: Camera
    system: System
    pi_sugar: PiSugar

    def __init__(
        self, 
        config: Config, 
        /, 
        dry_run: bool = False,
        camera: Camera | None = None,
        system: System | None = None,
        pi_sugar: PiSugar | None = None,
        storage: Storage | None = None,
    ):
        self.config = config
        self.camera = camera or ( Camera.fake() if dry_run else Camera.genuine() )
        self.system = system or ( System.fake() if dry_run else System.genuine() )
        
        pi_sugar_server_socket_path = config.values.pi_sugar.server_socket_path
        self.pi_sugar = pi_sugar or ( PiSugar.fake() if dry_run else PiSugar.genuine(pi_sugar_server_socket_path) )
        
        storage_folder_path = config.values.storage_folder_path
        self.storage = storage or ( Storage.fake() if dry_run else Storage.genuine(storage_folder_path) )

        self.exit_stack = ExitStack()

    def __enter__(self):
        for service in [self.camera, self.system, self.pi_sugar]:
            self.exit_stack.enter_context(service)
        return self
    
    def __exit__(self, type, value, traceback):
        self.exit_stack.close()

    @property
    def current_state(self) -> State:
        return State(
            wakeup_time=self.pi_sugar.wakeup_time,
            current_date_time=self.pi_sugar.now(),
        )
    
    def schedule_next_wakeup(self, wakeup_time: Time | None, current_date_time: DateTime) -> None:
        wakeup_time = wakeup_time or current_date_time.time()
        wakeup_date_time = DateTime.combine(current_date_time.date(), wakeup_time)
        delay_in_minutes = self.config.values.time_lapse.delay_in_minutes
        next_wakeup_date_time = wakeup_date_time.add(minutes=delay_in_minutes)
        next_wakeup_time = next_wakeup_date_time.time()
        
        self.pi_sugar.wakeup_time = next_wakeup_time
        self.schedule_timer(next_wakeup_date_time)

    def schedule_timer(self, date_time: DateTime) -> None:
        self.system.schedule_service("timelapse-handle-event@timer-triggered", date_time)

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
                self.take_picture(PictureIntent.TIME_LAPSE)
                self.schedule_next_wakeup(wakeup_time, current_date_time)

            case (
                State(wakeup_time, current_date_time),
                EventType.POWERED_ON,
            ):
                current_time = current_date_time.time()
                delay = current_time - wakeup_time if wakeup_time else None
                # If it has been powered off for a timelapse
                threshold_in_seconds = self.config.values.time_lapse.threshold_in_seconds
                if delay is None or delay.in_seconds() < 0 or delay.in_seconds() > threshold_in_seconds:
                    info("Starting services... ")
                    if self.config.values.hotspot.enabled:
                        self.start_hotspot()
                    self.start_website()
                    if wakeup_time:
                        day_offset = 1 if current_time > wakeup_time else 0
                        timer_date_time = DateTime.combine(current_date_time.date(), wakeup_time).add(days=day_offset)
                        self.schedule_timer(timer_date_time)
                else:
                    info("Taking picture for timelapse and powering off... ")
                    self.take_picture(PictureIntent.TIME_LAPSE)
                    self.schedule_next_wakeup(wakeup_time, current_date_time)
                    self.power_off()

            case (
                State(_, current_date_time),
                EventType.CUSTOM_BUTTON_LONG_TAPPED,
            ):
                info("Custom button long tapped! ")
                self.schedule_next_wakeup(None, current_date_time)

            case (
                State(_, current_date_time),
                EventType.CUSTOM_BUTTON_SINGLE_TAPPED,
            ):
                self.take_picture(PictureIntent.AD_HOC)

            case (
                State(_, _),
                EventType.POWER_BUTTON_TAPPED,
            ):
                self.power_off()

    def start_hotspot(self) -> None:
        self.system.start_service("timelapse-hotspot")

    def start_website(self) -> None:
        self.system.start_service("timelapse-website")

    def take_picture(
        self,
        intent: PictureIntent,
    ) -> Picture:
        date_time = self.now()
        content = self.camera.take_picture(PictureFormat.PNG)
        picture = self.storage.save_picture(
            intent=intent,
            date_time=date_time,
            content=content,
        )
        return picture
    
    def load_picture_content(self, picture_id: PictureID) -> BytesIO:
        return self.storage.load_picture_content(picture_id)
    
    def load_picture_thumbnail(self, picture_id: PictureID) -> BytesIO:
        return self.storage.load_picture_thumbnail(picture_id)

    def power_off(self) -> None:
        self.pi_sugar.power_off(delay=20)
        self.system.power_off(delay=5)

    def now(self) -> DateTime:
        return self.pi_sugar.now()
    
    def list_pictures(self) -> list[Picture]:
        return self.storage.list_pictures()
    
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