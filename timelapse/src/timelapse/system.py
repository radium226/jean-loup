import pendulum
from pendulum import DateTime
from enum import StrEnum, auto
import socket
from pathlib import Path
import os
import json
from subprocess import run
from time import sleep


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
        sleep(15)
        pisugar_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        pisugar_socket.connect(str(self.pisugar_socket_path))
        self.pisugar_socket = pisugar_socket
        return self
    
    def __exit__(self, type, value, traceback):
        if ( pisugar_socket := self.pisugar_socket ):
            pisugar_socket.close()
            self.pisugar_socket = None

    @property
    def wake_up_at(self) -> DateTime:
        with open(str(self.pisugar_config_path)) as f:
            return pendulum.parse(json.load(f)["auto_wake_time"])
    
    def now(self) -> DateTime:
        if ( pisugar_socket := self.pisugar_socket ):
            input = f"get rtc_time"
            print(f"input={input}")
            pisugar_socket.sendall(input.encode('utf-8'))
            output = pisugar_socket.recv(1024)
            print(f"output={output}")
            return pendulum.parse(output.decode('utf-8').replace("rtc_time: ", ""))

    def schedule_wakeup(self, at: DateTime) -> None:
        if ( pisugar_socket := self.pisugar_socket ):
            input = f"rtc_alarm_set {at} 127"
            print(f"input={input}")
            pisugar_socket.sendall(input.encode('utf-8'))
            output = pisugar_socket.recv(1024)
            print(f"output={output}")
        
    def shutdown(self) -> None:
        command = ["systemctl", "--no-block", "poweroff", "--check-inhibitors=no"]
        process = run(command)
        if process.returncode != 0:
            raise Exception("Unable to shutdown! ")

    def take_picture(self, file_path: Path) -> None:
        command = [
            "rpicam-still",
            "--nopreview",
            "--immediate",
            "--autofocus-on-capture",
            "--output", str(file_path)
        ]
        process = run(command)
        if process.returncode != 0:
            raise Exception("Unable to take picture! ")