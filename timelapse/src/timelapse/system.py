from typing import Generator
from contextlib import contextmanager
from subprocess import run

import pendulum
from pendulum import DateTime

from .capabilities import CanSystem

from .logging import info


class System(CanSystem):
    def __init__(self):
        pass

    @classmethod
    @contextmanager
    def create(cls) -> Generator["System", None, None]:
        info("Starting System service... ")
        yield System()
        info("Stopping System service... ")

    def now(self) -> DateTime:
        return pendulum.now()

    def power_off(self, delay: int) -> None:
        process = run(["systemctl", "poweroff", "-i", f"--when=+{delay}"])
        if process.returncode != 0:
            raise Exception("Unable to power off! ")

    def start_service(self, service_name: str) -> None:
        process = run(["systemctl", "start", f"{service_name}.service"])
        if process.returncode != 0:
            raise Exception(f"Unable to start {service_name} service! ")

    def stop_service(self, service_name: str) -> None:
        process = run(["systemctl", "stop", f"{service_name}.service"])
        if process.returncode != 0:
            raise Exception(f"Unable to start {service_name} service! ")
        
    def schedule_service(self, service_name: str, date_time: DateTime | None) -> None:
        run(["systemctl", "stop", f"{service_name}.timer"])
        
        if date_time is not None:
            command = [
                "systemd-run", 
                "--on-calendar={date_time}".format(date_time=date_time.format("YYYY-MM-DD[ ]HH:mm:ss")),
                f"--unit={service_name}.service",
            ]
            info(" ".join(command))
            process = run(command)
            if process.returncode != 0:
                raise Exception(f"Unable to schedule {service_name} service! ")