from typing import Generator
from contextlib import contextmanager
import pendulum
from pendulum import Time, DateTime
from subprocess import run
import socket
from pathlib import Path

from .logging import info
from .capabilities import CanPiSugar


class PiSugar(CanPiSugar):

    SERVER_SOCKET_PATH = Path("/run/pisugar/server.sock")

    def __init__(self):
        pass

    @classmethod
    @contextmanager
    def create(cls) -> Generator["PiSugar", None, None]:
        info("Starting PiSugar service... ")
        # FIXME: We need to update the pisugar-server to wait for the socket to be created
        yield PiSugar()
        info("Stopping PiSugar service... ")


    @contextmanager
    def _open_server_socket(self) -> Generator[socket.socket, None, None]:
        server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_socket.connect(str(self.SERVER_SOCKET_PATH))
        try:
            yield server_socket
        finally:
            server_socket.close()

    def _communicate_with_server(self, input: str) -> str:
        print("We are here! ")
        with self._open_server_socket() as server_socket:
            print(f"input={input}")
            server_socket.sendall(input.encode('utf-8'))
            output = server_socket.recv(1024).decode('utf-8')
            if "Invalid" in output:
                raise Exception("Invalid output! ")

            while True:
                print(f"tata {output}")
                print(f"toto {output}")
                if output not in ["single", "long", "double"]:
                    print("Youpi")
                    break
                output = server_socket.recv(1024).decode('utf-8')
                
            print(f"output={output}")
            return output.replace("long", "").replace("single", "").replace("double", "").strip()



    def now(self) -> DateTime:
        output = self._communicate_with_server("get rtc_time")
        if isinstance(date_time := pendulum.parse(output.replace("rtc_time: ", "")), DateTime):
            return date_time
        else:
            raise Exception("Unable to get date time! ")

    @property
    def wakeup_time(self) -> Time | None:
        output = self._communicate_with_server("get rtc_alarm_enabled").replace("rtc_alarm_enabled: ", "").strip()
        info(f"rtc_alarm_enabled={output}")
        if output == "true":
            output = self._communicate_with_server("get rtc_alarm_time").replace("rtc_alarm_time: ", "").strip()
            info(f"rtc_alarm_time={output}")
            if isinstance(date_time := pendulum.parse(output), DateTime):
                return date_time.time()
            else:
                raise Exception("Unable to get wakeup time! ")
        else:
            return None
        

    @wakeup_time.setter
    def wakeup_time(self, value: Time | None) -> None:
        if value:
            date_time = pendulum.now().set(hour=value.hour, minute=value.minute, second=value.second)
            self._communicate_with_server(f"rtc_alarm_set {date_time} 127")
        else:
            self._communicate_with_server("rtc_alarm_disable")

    def power_off(self, delay: int = 0) -> None:
        if delay > 255:
            raise Exception("Delay must be between 0 and 255! ")
        
        # FIXME: It's wrong: we should use I2C directly and do the AND stuff which is in the doc
        commands = [
            ["i2cset", "-y", "1", "0x57", "0x0B", "0x29"],
            ["i2cset", "-y", "1", "0x57", "0x09", "0x%0.2X" % delay],
            ["i2cset", "-y", "1", "0x57", "0x02", "0x44"],
        ]
        for command in commands:
            process = run(command)
            if process.returncode != 0:
                raise Exception("Unable to power off! ")
        
        


