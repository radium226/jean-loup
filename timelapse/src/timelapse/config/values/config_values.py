from pydantic import BaseModel
from pathlib import Path

from .hotspot import Hotspot
from .time_lapse import TimeLapse
from .website import Website
from .pi_sugar import PiSugar


class ConfigValues(BaseModel):

    storage_folder_path: Path

    hotspot: Hotspot

    time_lapse: TimeLapse

    website: Website

    pi_sugar: PiSugar