from enum import StrEnum, auto

def _to_camel_case(snake_str):
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))

def _to_lower_camel_case(snake_str):
    # We capitalize the first letter of each component except the first one
    # with the 'capitalize' method and join them together.
    camel_string = _to_camel_case(snake_str)
    return snake_str[0].lower() + camel_string[1:]



class EventType(StrEnum):
    def _generate_next_value_(name, start, count, last_values):
        return _to_lower_camel_case(name)

    POWERED_ON = auto()

    CUSTOM_BUTTON_SINGLE_TAPPED = auto()

    CUSTOM_BUTTON_LONG_TAPPED = auto()

    CUSTOM_BUTTON_DOUBLE_TAPPED = auto()

    POWER_BUTTON_TAPPED = auto()
