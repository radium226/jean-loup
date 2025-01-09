from typing import Protocol
from pendulum import DateTime, Time
from dataclasses import dataclass

from contextlib import ExitStack, contextmanager
from smbus import SMBus



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
    def genuine() -> "PiSugar":
        raise Exception("Not implemented! ")




I2C_CHIP_ADDRESS = 0x57


@dataclass(frozen=True)
class I2CDataAddresses():

    WRITE_PROTECTION = 0x0b

    RTC_YEAR = 0x30
    RTC_MONTH = 0x31
    RTC_DAY = 0x32

    RTC_HOURS = 0x31
    RTC_MINUTES = 0x32
    RTC_SECONDS = 0x33

    ALARM_HOURS = 0x45
    ALARM_MINUTES = 0x46
    ALARM_SECONDS = 0x47
    ALARM_WEEKDAYS = 0x44

    TIMING_BOOT = 0x40

    BATTERY_LEVEL = 0x2a


class _Genuine(PiSugar):


    I2C_BUS = 1

    WRITE_PROTECTION_DATA_ADDRESS = 0x0B

    exit_stack: ExitStack | None
    i2c_bus: SMBus | None

    def __init__(self):
        self.exit_stack = None

    def __enter__(self) -> "PiSugar":
        self.exit_stack = ExitStack()

        i2c_bus = SMBus(self.RPI_I2C_BUS)
        self.i2c_bus = self.exit_stack.enter_context(i2c_bus)

        return self
    
    def _write_byte_data(self, address: int, data: int) -> None:
        self.i2c_bus.write_byte_data(I2C_CHIP_ADDRESS, address, data)

    def _read_byte_data(self, address: int) -> int:
        return self.i2c_bus.read_byte_data(I2C_CHIP_ADDRESS, address)
    
    @contextmanager()
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
        month = self._read_byte_data(I2CDataAddresses.RTC_MONTH)
        day = self._read_byte_data(I2CDataAddresses.RTC_DAY)

        hours = self._read_byte_data(I2CDataAddresses.RTC_HOURS)
        minutes = self._read_byte_data(I2CDataAddresses.RTC_MINUTES)
        seconds = self._read_byte_data(I2CDataAddresses.RTC_SECONDS)

        return DateTime(year, month, day, hours, minutes, seconds)
        
    
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
    def wakeup_time(self) -> Time | None:
        if self._read_byte_data(I2CDataAddresses.TIMING_BOOT) == 0x00:
            return None
        hour = self._read_byte_data(I2CDataAddresses.ALARM_HOURS)
        minute = self._read_byte_data(I2CDataAddresses.ALARM_MINUTES)
        second = self._read_byte_data(I2CDataAddresses.ALARM_SECONDS)
        return Time(hour, minute, second)

    @wakeup_time.setter
    def wakeup_time(self, value: Time | None) -> None:
        with self._write_protection():
            if value is None:
                # We disable the timing boot
                self._write_byte_data(I2CDataAddresses.TIMING_BOOT, 0b00000000)
            else:
                # We set the alarm for all days
                self._write_byte_data(I2CDataAddresses.ALARM_WEEKDAYS, 0b0111111)
                # And we set it for the give time
                hours = value.hour
                self._write_byte_data(I2CDataAddresses.ALARM_HOURS, hours)
                minutes = value.minute
                self._write_byte_data(I2CDataAddresses.ALARM_MINUTES, minutes)
                seconds = value.second
                self._write_byte_data(I2CDataAddresses.ALARM_SECONDS, seconds)
                # We enable the timing boot
                self._write_byte_data(I2CDataAddresses.TIMING_BOOT, 0b10000000)
                
    def power_off(self, delay: int | None = None) -> None:
        ...

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
