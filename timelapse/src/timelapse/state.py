from dataclasses import dataclass
from pendulum import Time

@dataclass
class State():

    wakeup_time: Time | None

    current_time: Time