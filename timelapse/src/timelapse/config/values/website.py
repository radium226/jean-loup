from pydantic import BaseModel
from pathlib import Path


class Website(BaseModel):

    enabled: bool

    ui_folder_path: Path