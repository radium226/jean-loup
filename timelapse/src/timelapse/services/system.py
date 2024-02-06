from typing import Protocol
import pendulum
from pendulum import DateTime
from subprocess import run

from ..logging import info


class System(Protocol):

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def power_off(self, delay: int) -> None:
        ...

    def start_service(self, service_name: str) -> None:
        ...

    def stop_service(self, service_name: str) -> None:
        ...
        
    def schedule_service(self, service_name: str, date_time: DateTime | None) -> None:
        ...

    @classmethod
    def genuine(cls) -> "System":
        return _GenuineSystem()
    
    @classmethod
    def fake(cls) -> "System":
        return _FakeSystem()
    

class _GenuineSystem(System):

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass
    
    def now(self) -> DateTime:
        return pendulum.now()

    def power_off(self, delay: int) -> None:
        run(["systemctl", "poweroff", "-i", f"--when=+{delay}"], check=True)

    def start_service(self, service_name: str) -> None:
        run(["systemctl", "start", f"{service_name}.service"], check=True)

    def stop_service(self, service_name: str) -> None:
        run(["systemctl", "stop", f"{service_name}.service"], check=True)
        
    def schedule_service(self, service_name: str, date_time: DateTime | None) -> None:
        run(["systemctl", "stop", f"{service_name}.timer"], check=False)
        
        if date_time is not None:
            command = [
                "systemd-run", 
                "--on-calendar={date_time}".format(date_time=date_time.format("YYYY-MM-DD[ ]HH:mm:ss")),
                f"--unit={service_name}.service",
            ]
            print(command)
            run(command, check=True)


class _FakeSystem(System):

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def now(self) -> DateTime:
        return pendulum.now()

    def power_off(self, delay: int) -> None:
        info("Powering off system in {delay} seconds... ", delay=delay)

    def start_service(self, service_name: str) -> None:
        info("Starting {service_name} service... ", service_name=service_name)

    def stop_service(self, service_name: str) -> None:
        info("Stopping {service_name} service... ", service_name=service_name)
        
    def schedule_service(self, service_name: str, date_time: DateTime | None) -> None:
        info("Scheduling {service_name} service at {date_time}... ", service_name=service_name, date_time=date_time)