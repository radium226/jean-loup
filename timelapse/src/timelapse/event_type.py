from enum import StrEnum, auto


class EventType(StrEnum):
    POWER_ON = auto()

    CUSTOM_BUTTON_SINGLE_TAP = auto()

    CUSTOM_BUTTON_LONG_TAP = auto()

    CUSTOM_BUTTON_DOUBLE_TAP = auto()

    POWER_BUTTON_TAP = auto()
