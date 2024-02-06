from dataclasses import dataclass
from pendulum import Time, DateTime


@dataclass
class State:
    wakeup_time: Time | None

    current_date_time: DateTime
