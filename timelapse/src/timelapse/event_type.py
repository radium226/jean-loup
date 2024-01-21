from enum import StrEnum, auto


class EventType(StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return name.replace("_", "-").lower()

    POWERED_ON = auto()

    CUSTOM_BUTTON_SINGLE_TAPPED = auto()

    CUSTOM_BUTTON_LONG_TAPPED = auto()

    CUSTOM_BUTTON_DOUBLE_TAPPED = auto()

    POWER_BUTTON_TAPPED = auto()

    TIMER_TRIGGERED = auto()
