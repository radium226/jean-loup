from pathlib import Path
from pendulum import DateTime, Time
from io import BytesIO
from dataclasses import dataclass
from enum import StrEnum, auto

from contextlib import contextmanager, ExitStack
from typing import Generator

from .logging import info

from .pisugar import PiSugar
from .system import System
from .camera import Camera

from .event_type import EventType
from .state import State


class Controller():

    def __init__(self, pisugar: PiSugar, system: System, camera: Camera) -> None:
        self.pisugar = pisugar
        self.system = system
        self.camera = camera

    @property
    def current_state(self) -> State:
        return State(
            wakeup_time=self.pisugar.wake_up_time,
            current_time=self.pisugar.now().time(),
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
        match (state, event_type, ):
            case (State(wakeup_time, current_time), EventType.POWER_ON, ):
                if wakeup_time is None or ( wakeup_time - current_time ).in_minutes() < 1:
                    self.take_picture()
                    next_wakeup_time = wakeup_time.add(minutes=5)
                    self.schedule_wakeup(next_wakeup_time)
                    self.power_off()
                else:
                    self.start_access_point()
                    self.start_website()

            case (State(_, current_time), EventType.CUSTOM_BUTTON_LONG_TAP, ):
                info("Schedule wakeup time! ... ")
                self.schedule_wakeup(current_time)

            case (State(_, _), EventType.CUSTOM_BUTTON_SINGLE_TAP, ):
                info("Taking picture... ")
                self.take_picture()

            case (State(_, _), EventType.POWER_BUTTON_TAP, ):
                info("Powering off... ")
                self.power_off()
        
    
    def start_access_point(self) -> None:
        self.system.start_service("timestamp-access-point")

    def start_website(self) -> None:
        self.system.start_service("timestamp-website")

    def take_picture(self) -> BytesIO:
        return self.camera.take_picture()

    def power_off(self) -> None:
        self.pisugar.power_off(delay=10)
        self.system.power_off()

    def schedule_wakeup(self, time: Time | None) -> None:
        self.pisugar.schedule_wakeup(time)