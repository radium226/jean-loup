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
        
    def schedule_service(self, service_name: str, date_time: DateTime) -> None:
        run(["systemctl", "stop", f"{service_name}.timer"])
        
        command = [
            "systemd-run", 
            "--on-calendar={date_time}".format(date_time=date_time.format("YYYY-MM-DD[ ]HH:mm:ss")),
            f"--unit={service_name}.service",
        ]
        info(" ".join(command))
        process = run(command)
        if process.returncode != 0:
            raise Exception(f"Unable to schedule {service_name} service! ")


# import pendulum
# from pendulum import DateTime
# from enum import StrEnum, auto
# import socket
# from pathlib import Path
# import os
# import json
# from subprocess import run
# from time import sleep
# from contextlib import contextmanager
# from typing import Generator


# class PictureFormat(StrEnum):

#     JPEG = auto()
#     PNG = auto()


# class System():

#     def __init__(self,
#         pisugar_config_path: Path = Path("/etc/pisugar-server/config.json"),
#         pisugar_socket_path: Path = Path("/run/pisugar-server/pisugar-server.sock"),
#     ):
#         self.pisugar_config_path = pisugar_config_path

#         self.pisugar_socket_path = pisugar_socket_path
#         self.pisugar_socket = None

#     def communicate_with_pisugar(self, input: str) -> str:
#         with self.open_pisugar_socket() as pisugar_socket:
#             print(f"input={input}")
#             pisugar_socket.sendall(input.encode('utf-8'))
#             output = pisugar_socket.recv(1024).decode('utf-8')

#             while True:
#                 output = pisugar_socket.recv(1024).decode('utf-8')
#                 if output != "single":
#                     break

#             print(f"output={output}")
#             return output

#     @contextmanager
#     def open_pisugar_socket(self) -> Generator[socket.socket, None, None]:
#         pisugar_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#         pisugar_socket.connect(str(self.pisugar_socket_path))
#         try:
#             yield pisugar_socket
#         finally:
#             pisugar_socket.close()

#     def __enter__(self):
#         return self

#     def __exit__(self, type, value, traceback):
#         pass

#     @property
#     def wake_up_at(self) -> DateTime:
#         with open(str(self.pisugar_config_path)) as f:
#             return pendulum.parse(json.load(f)["auto_wake_time"])

#     @property
#     def auto_power_on(self) -> bool:
#         self.communicate_with_pisugar("get auto_power_on") == "true"

#     @property
#     def wake_up_at(self) -> DateTime:
#         if self.communicate_with_pisugar("get rtc_alarm_enabled").replace("rtc_alarm_enabled: ", "") == "true":
#             with self.pisugar_config_path.open("r") as f:
#                 return pendulum.parse(json.load(f)["auto_wake_time"])
#         else:
#             return None

#     @wake_up_at.setter
#     def wake_up_at(self, value: DateTime | None) -> None:
#         if value is None:
#             self.communicate_with_pisugar("rtc_alarm_disable")
#         else:
#             self.communicate_with_pisugar(f"rtc_alarm_set {value} 127")

#     @auto_power_on.setter
#     def auto_power_on(self, value: bool) -> None:
#        self.communicate_with_pisugar("set_auto_power_on {value}".format(value = "true" if value else "false"))

#     def now(self) -> DateTime:
#         return pendulum.now()

#         output = self.communicate_with_pisugar("get rtc_time")
#         return pendulum.parse(output.replace("rtc_time: ", ""))

#     def shutdown(self) -> None:
#         command = ["systemctl", "--no-block", "poweroff", "--check-inhibitors=no"]
#         process = run(command)
#         if process.returncode != 0:
#             raise Exception("Unable to shutdown! ")

#     def take_picture(self, file_path: Path) -> None:
#         command = [
#             "rpicam-still",
#             "--nopreview",
#             "--immediate",
#             "--autofocus-on-capture",
#             "--output", str(file_path)
#         ]
#         process = run(command)
#         if process.returncode != 0:
#             raise Exception("Unable to take picture! ")
