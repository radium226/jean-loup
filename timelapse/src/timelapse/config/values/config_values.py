from pydantic import BaseModel
from pathlib import Path

from .hotspot import Hotspot
from .time_lapse import TimeLapse
from .website import Website


class ConfigValues(BaseModel):

    data_folder_path: Path

    hotspot: Hotspot

    time_lapse: TimeLapse

    website: Website