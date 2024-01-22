from pathlib import Path
import json
from deepmerge import always_merger
from pendulum import Time

from .values import (
    ConfigValues,
    TimeLapse,
    Hotspot,
    Website,
)


class Config:

    DEFAULT_FILE_PATH = Path("/etc/timelapse/config.json")

    DEFAULT_VALUES = ConfigValues(
        data_folder_path=Path("/var/lib/timelapse"),
        time_lapse=TimeLapse(
            enabled=True,
            wakeup_time=Time(12, 0, 0)
        ),
        hotspot=Hotspot(
            enabled=True,
            ssid="bamboo",
        ),
        website=Website(
            enabled=True,
            ui_folder_path=Path("/var/lib/timelapse/website"),
        ),
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
        with ( file_path or cls.DEFAULT_FILE_PATH ).open("r") as f:
            obj = json.load(f)
            if isinstance(obj, dict):
                return cls(obj, file_path=file_path)
            else:
                raise Exception("Config file is invalid! ")

    def override_with(self, other: "Config") -> "Config":
        return Config(
            always_merger.merge(
                self.obj, 
                other.obj,
            ), 
            file_path=self.file_path or other.file_path,
        )

    @property
    def values(self) -> ConfigValues:
        return ConfigValues.model_validate(self.obj)
    
    def save_values(self, /, file_path: Path | None = None):
        file_path = file_path or self.file_path or self.DEFAULT_FILE_PATH
        with file_path.open("w") as f:
            f.write(self.values.model_dump_json())