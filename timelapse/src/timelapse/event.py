from enum import StrEnum, auto
from typing import Protocol
from dataclasses import dataclass


class EventType(StrEnum):

    POWER_ON = auto()

    BUTTON_SINGLE_TAP = auto()
    
    BUTTON_LONG_TAP = auto()

    BUTTON_DOUBLE_TAP = auto()


class Event(Protocol):

    @property
    def type(self) -> EventType:
        ...


@dataclass
class PowerOnEvent(Event):

    type = EventType.POWER_ON


@dataclass
class ButtonTapEvent(Event)
    
    type = EventType.BUTTON_TAP