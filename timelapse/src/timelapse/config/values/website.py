from pydantic import BaseModel
from pathlib import Path
from ipaddress import IPv4Address


class Website(BaseModel):

    enabled: bool

    ui_folder_path: Path

    host: IPv4Address

    port: int