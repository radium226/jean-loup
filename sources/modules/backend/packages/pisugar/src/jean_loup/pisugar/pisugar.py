from typing import Protocol, Generator
import socket
from pendulum import DateTime, Time, now, timezone
from dataclasses import dataclass

from contextlib import ExitStack, contextmanager
from smbus import SMBus
from pathlib import Path
from retrying import retry

from subprocess import run



@dataclass
class BatteryLevel():

    ratio: float


class PiSugar(Protocol):
    def __enter__(self) -> "PiSugar": ...

    def __exit__(self, type, value, traceback) -> None: ...

    def now(self) -> DateTime: ...

    @property
    def wakeup_time(self) -> Time | None: ...

    @wakeup_time.setter
    def wakeup_time(self, value: Time | None) -> None: ...

    def power_off(self, delay: int | None = None) -> None: ...

    @property
    def battery_level(self) -> int: ...

    @staticmethod
    def fake() -> "PiSugar":
        return _Fake()

    @staticmethod
    def genuine(server_socket_path: Path | None = None) -> "PiSugar":
        return _Genuine(server_socket_path)




I2C_CHIP_ADDRESS = 0x57


def bcd_to_dec(bcd: int) -> int:
    return (bcd & 0x0F) + (((bcd & 0xF0) >> 4) * 10)

def dec_to_bcd(dec: int) -> int:
    return (dec % 10) | ((int(dec / 10)) << 4)


@dataclass(frozen=True)
class I2CDataAddresses():

    WRITE_PROTECTION = 0x0b

    RTC_YEAR = 0x31
    RTC_MONTH = 0x32
    RTC_DAY = 0x33

    RTC_HOURS = 0x35
    RTC_MINUTES = 0x36
    RTC_SECONDS = 0x37

    ALARM_HOURS = 0x45
    ALARM_MINUTES = 0x46
    ALARM_SECONDS = 0x47
    ALARM_WEEKDAYS = 0x44

    TIMING_BOOT = 0x40

    BATTERY_LEVEL = 0x2a


class _Genuine(PiSugar):

    DEFAULT_SERVER_SOCKET_PATH = Path("/var/run/pisugar/server.sock")

    I2C_BUS = 1

    exit_stack: ExitStack | None
    i2c_bus: SMBus | None

    def __init__(self, server_socket_path: Path | None = None) -> None:
        self.exit_stack = None
        self.server_socket_path = server_socket_path or self.DEFAULT_SERVER_SOCKET_PATH

    def __enter__(self) -> "PiSugar":
        self.exit_stack = ExitStack()

        self.i2c_bus = SMBus(self.I2C_BUS)
        self.exit_stack.callback(self.i2c_bus.close)

        return self
    
    @contextmanager
    def _open_server_socket(self) -> Generator[socket.socket, None, None]:
        server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_socket.connect(str(self.server_socket_path))
        try:
            yield server_socket
        finally:
            server_socket.close()

    def _communicate_with_server(self, input: str) -> str:
        with self._open_server_socket() as server_socket:
            server_socket.sendall(input.encode('utf-8'))
            output = server_socket.recv(1024).decode('utf-8')
            print(output)
            if "Invalid" in output:
                raise Exception("Invalid output! ")

            while True:
                if output not in ["single", "long", "double"]:
                    break
                output = server_socket.recv(1024).decode('utf-8')
                
            return output.replace("long", "").replace("single", "").replace("double", "").strip()
    
    
    def _write_byte_data(self, address: int, data: int) -> None:
        self.i2c_bus.write_byte_data(I2C_CHIP_ADDRESS, address, data)

    def _read_byte_data(self, address: int) -> int:
        return self.i2c_bus.read_byte_data(I2C_CHIP_ADDRESS, address)
    
    @contextmanager
    def _write_protection(self):
        self._write_byte_data(I2CDataAddresses.WRITE_PROTECTION, 0x29)
        try:
            yield
        finally:
            self._write_byte_data(I2CDataAddresses.WRITE_PROTECTION, 0xff)

    def __exit__(self, type, value, traceback) -> None:
        if exit_stack := self.exit_stack:
            exit_stack.close()

    def now(self) -> DateTime:
        year = self._read_byte_data(I2CDataAddresses.RTC_YEAR)
        year = bcd_to_dec(year)
        year = 2000 + year

        month = self._read_byte_data(I2CDataAddresses.RTC_MONTH)
        month = bcd_to_dec(month)
        
        day = self._read_byte_data(I2CDataAddresses.RTC_DAY)
        day = bcd_to_dec(day)

        hours = self._read_byte_data(I2CDataAddresses.RTC_HOURS)
        hours = bcd_to_dec(hours)
        
        minutes = self._read_byte_data(I2CDataAddresses.RTC_MINUTES)
        minutes = bcd_to_dec(minutes)
        
        seconds = self._read_byte_data(I2CDataAddresses.RTC_SECONDS)
        seconds = bcd_to_dec(seconds)
        
        date_time = DateTime(year, month, day, hours, minutes, seconds, tzinfo=timezone("UTC"))
        date_time = date_time.in_timezone("local")
        return date_time
        
    
    # Only the setter!
    def _rtc_date_time(self, value: DateTime) -> None:
        with self._write_protection():
            year = value.year
            self._write_byte_data(I2CDataAddresses.RTC_YEAR, year)
            month = value.month
            self._write_byte_data(I2CDataAddresses.RTC_MONTH, month)
            day = value.day
            self._write_byte_data(I2CDataAddresses.RTC_DAY, day)

            week_day = value.day_of_week

            hours = value.hour
            self._write_byte_data(I2CDataAddresses.RTC_HOURS, hours)
            minutes = value.minute
            self._write_byte_data(I2CDataAddresses.RTC_MINUTES, minutes)
            seconds = value.second
            self._write_byte_data(I2CDataAddresses.RTC_SECONDS, seconds)

    rtc_date_time = property(None, _rtc_date_time)

    @property
    @retry(stop_max_delay=10 * 60 * 1000, wait_fixed=60 * 1000)
    def wakeup_time(self) -> Time | None:
        if self._read_byte_data(I2CDataAddresses.TIMING_BOOT) & (0b1000_0000) == 0x00:
            return None
        
        hour = self._read_byte_data(I2CDataAddresses.ALARM_HOURS)
        hour = bcd_to_dec(hour)

        minute = self._read_byte_data(I2CDataAddresses.ALARM_MINUTES)
        minute = bcd_to_dec(minute)

        second = self._read_byte_data(I2CDataAddresses.ALARM_SECONDS)
        second = bcd_to_dec(second)

        time = Time(hour, minute, second)

        date_time = self.now()
        date_time = date_time.in_timezone("UTC")
        date_time = date_time.at(hour=time.hour, minute=time.minute, second=time.second)
        date_time = date_time.in_timezone("local")
        time = date_time.time()
        return time


    @wakeup_time.setter
    def wakeup_time(self, value: Time | None) -> None:
        if value:
            date_time = now().set(hour=value.hour, minute=value.minute, second=value.second)
            message = "rtc_alarm_set {date_time} 127".format(date_time=date_time.isoformat(timespec="seconds"))
            print(message)
            self._communicate_with_server(message)
        else:
            self._communicate_with_server("rtc_alarm_disable")
        # with self._write_protection():
        #     if value is None:
        #         # We disable the timing boot
        #         self._write_byte_data(I2CDataAddresses.TIMING_BOOT, 0b00000000)
        #     else:
        #         date_time = now().at(hour=value.hour, minute=value.minute, second=value.second)
        #         date_time = date_time.in_timezone("UTC")
        #         value = date_time.time()

        #         # We set the alarm for all days
        #         self._write_byte_data(I2CDataAddresses.ALARM_WEEKDAYS, 0b0111111)
        #         # And we set it for the give time
        #         hours = value.hour
        #         hours = dec_to_bcd(hours)
        #         self._write_byte_data(I2CDataAddresses.ALARM_HOURS, hours)

        #         minutes = value.minute
        #         minutes = dec_to_bcd(minutes)
        #         self._write_byte_data(I2CDataAddresses.ALARM_MINUTES, minutes)

        #         seconds = value.second
        #         seconds = dec_to_bcd(seconds)
        #         self._write_byte_data(I2CDataAddresses.ALARM_SECONDS, seconds)
        #         # We enable the timing boot
        #         self._write_byte_data(I2CDataAddresses.TIMING_BOOT, 0b10000000)
                
    def power_off(self, delay: int) -> None:
        if delay > 255:
            raise Exception("Delay must be between 0 and 255! ")
        
        # with self._write_protection():
        #     self._read_byte_data()
        
        # First, let's make everything writable
        run(["i2cset", "-y", "1", "0x57", "0x0B", "0x29"], check=True)

        # Then set the delay
        run(["i2cset", "-y", "1", "0x57", "0x09", "0x%0.2X" % delay], check=True)

        # Get the byte value
        ic2get_process = run(["i2cget", "-y", "1", "0x57", "0x02"], check=True, capture_output=True, text=True)
        old_value = int(ic2get_process.stdout, 0)
        
        index = 5 # See in the doc
        new_value = old_value & ~(1 << index)
        
        run(["i2cset", "-y", "1", "0x57", "0x02", "0x{:02x}".format(new_value)], check=True)

    @property
    def battery_level(self) -> int:
        value = self._read_byte_data(I2CDataAddresses.BATTERY_LEVEL)
        return BatteryLevel(float(value) / 100.00)



class _Fake(PiSugar):
    def __enter__(self) -> "PiSugar":
        return self

    def __exit__(self, type, value, traceback) -> None:
        pass

    def now(self) -> DateTime:
        return DateTime.now()

    @property
    def wakeup_time(self) -> Time | None:
        return None

    @wakeup_time.setter
    def wakeup_time(self, value: Time | None) -> None:
        pass

    def power_off(self, delay: int | None = None) -> None:
        pass

    @property
    def battery_level(self) -> int:
        return 100
