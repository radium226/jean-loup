import pendulum
from pendulum import DateTime
from enum import StrEnum, auto
import socket
from pathlib import Path
import os
import json
from subprocess import run


class PictureFormat(StrEnum):

    JPEG = auto()
    PNG = auto()


class System():

    def __init__(self, 
        pisugar_config_path: Path = Path("/etc/pisugar-server/config.json"),
        pisugar_socket_path: Path = Path("/run/pisugar-server/pisugar-server.sock"),
    ):
        self.pisugar_config_path = pisugar_config_path

        self.pisugar_socket_path = pisugar_socket_path
        self.pisugar_socket = None


    def __enter__(self):
        pisugar_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        pisugar_socket = pisugar_socket.connect(str(self.pisugar_socket_path))
        self.pisugar_socket = pisugar_socket
        return self
    
    def __exit__(self, type, value, traceback):
        if ( pisugar_socket := self.pisugar_socket ):
            pisugar_socket.close()
            self.pisugar_socket = None

    @property
    def wake_up_at(self) -> DateTime:
        return pendulum.parse(json.loads(str(self.pisugar_config_path))["auto_wake_time"])

    def schedule_wakeup(self, at: DateTime) -> None:
        if ( pisugar_socket := self.pisugar_socket ):
            input = f"rtc_alarm_set {at.to_iso8601_string()} 127"
            pisugar_socket.sendall(input.encode('utf-8'))
            output = pisugar_socket.recv(1024)
            print(output)
        
    def shutdown(self) -> None:
        os.system("shutdown")

    def take_picture(self, file_path: Path) -> None:
        command = [
            "rpicam-still",
            "--immediate",
            "--autofocus-on-capture",
            "--encoder", "jpg",
            "--output", str(file_path)
        ]
        process = run(command)
        if process.returncode != 0:
            raise Exception("Unable to take picture! ")