from pydantic import BaseModel
from ...types_for_pydantic import Path, IPv4Address


class Website(BaseModel):

    enabled: bool

    ui_folder_path: Path

    host: IPv4Address

    port: int