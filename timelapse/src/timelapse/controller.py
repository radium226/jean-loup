from pathlib import Path
from pendulum import DateTime
from io import BytesIO
from dataclasses import dataclass
from enum import StrEnum, auto

from contextlib import contextmanager, ExitStack
from typing import Generator

from .logging import info

from .pisugar import PiSugar
from .system import System
from .camera import Camera


class EventType(StrEnum):

    POWER_ON = auto()

    BUTTON_SINGLE_TAP = auto()
    
    BUTTON_LONG_TAP = auto()

    BUTTON_DOUBLE_TAP = auto()


class Controller():

    def __init__(self, pisugar: PiSugar, system: System, camera: Camera) -> None:
        self.pisugar = pisugar
        self.system = system
        self.camera = camera

    @property
    def current_state(self) -> State:
        pass

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

    def get_by(self) -> None:
        info("Getting by! ")

    # def take_picture(self) -> BytesIO:
    #     return self.camera.take_picture()


    # def power_off(self) -> None:
    #     self.pisugar.power_off(delay=10)
    #     self.system.power_off()

    # def schedule_wakeup(self, at: DateTime | None) -> None:
    #     self.pisugar.schedule_wakeup(at=at)