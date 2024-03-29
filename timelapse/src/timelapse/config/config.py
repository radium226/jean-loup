from typing import overload, Union
from pathlib import Path
import json
from deepmerge import Merger
from pendulum import Time
from ipaddress import IPv4Address, IPv4Network

from .values import (
    ConfigValues,
    TimeLapse,
    Hotspot,
    Website,
    PiSugar,
)


class Config:

    DEFAULT_FILE_PATH = Path("/etc/timelapse/config.json")

    DEFAULT_VALUES = ConfigValues(
        storage_folder_path=Path("/var/lib/timelapse"),
        time_lapse=TimeLapse(
            enabled=True,
            wakeup_time=Time(12, 0, 0),
            delay_in_minutes=60,
            threshold_in_seconds=60,
        ),
        hotspot=Hotspot(
            enabled=True,
            ssid="Jean-Loup",
            domain="bambou",
            ip_network=IPv4Network("192.168.50.1/24", strict=False),
            wireless_hardware_device="phy0",
        ),
        website=Website(
            enabled=True,
            ui_folder_path=Path("/usr/lib/timelapse/website/ui"),
            host=IPv4Address("0.0.0.0"),
            port=8080,
        ),
        pi_sugar=PiSugar(
            server_socket_path=Path("/run/pisugar/server.sock"),
        )
    )

    file_path: Path | None
    obj: dict
    
    def __init__(self, obj_or_values: dict | ConfigValues, /, file_path: Path | None = None):
        self.file_path = file_path
        self.obj = (
            obj_or_values 
            if isinstance(obj_or_values, dict) 
            else obj_or_values.model_dump()
        )

    @classmethod
    def default(cls, /, file_path: Path | None = None) -> "Config":
        return cls(cls.DEFAULT_VALUES, file_path=file_path)

    @classmethod
    def from_file(cls, file_path: Path | None) -> "Config":
        if ( file_path or cls.DEFAULT_FILE_PATH ).exists():
            with ( file_path or cls.DEFAULT_FILE_PATH ).open("r") as f:
                obj = json.load(f)
                if isinstance(obj, dict):
                    return cls(obj, file_path=file_path)
                else:
                    raise Exception("Config file is invalid! ")
        else:
            return Config({})

    @overload
    def override_with(self, other: "Config") -> "Config":
        ...

    @overload
    def override_with(self, other: dict) -> "Config":
        ...

    @overload
    def override_with(self, other: Path) -> "Config":
        ...   

    def override_with(self, other: Union["Config", dict, Path]) -> "Config":
        print(other)
        if isinstance(other, Config):
            other_obj = other.obj
            other_file_path = None

        elif isinstance(other, dict):
            other_obj = other
            other_file_path = None

        elif isinstance(other, Path):
            other_obj = json.loads(other.read_text())
            other_file_path = other
        else:
            print(type(other))

        merger = Merger(
            [
                (list, ["append"]),
                (dict, ["merge"]),
                (set, ["union"])
            ],
            # next, choose the fallback strategies,
            # applied to all other types:
            ["override"],
            # finally, choose the strategies in
            # the case where the types conflict:
            ["override"]
        )
        return Config(
            merger.merge(
                self.obj, 
                other_obj,
            ), 
            file_path=self.file_path
        )

    @property
    def values(self) -> ConfigValues:
        return ConfigValues.model_validate(self.obj)
    
    def save_values(self, /, file_path: Path | None = None):
        file_path = file_path or self.file_path or self.DEFAULT_FILE_PATH
        with file_path.open("w") as f:
            f.write(self.values.model_dump_json())