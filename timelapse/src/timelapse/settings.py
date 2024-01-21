from pydantic import BaseModel
from pendulum import Time
from pathlib import Path


class Credentials(BaseModel):

    login: str
    password: str


class Hotspot(BaseModel):

    enabled: bool = True
    ssid: str = "bamboo"
    credentials: Credentials | None = None


class TimeLapse(BaseModel):

    enabled: bool = True
    
    wakeup_time: Time


class Root(BaseModel):

    hotspot: Hotspot

    time_lapse: TimeLapse



class Settings():

    DEFAULT_FOLDER_PATH = Path("/etc/jean-loup")

    file_path: Path

    def __init__(self, folder_path: Path | None = None):
        self.file_path = ( folder_path or self.DEFAULT_FOLDER_PATH ) / "settings.toml"
    
    def dump(self, root: Root) -> None:
        with self.file_path.open("w") as f:
            f.write(root.model_dump_json(indent=2))

    def load(self) -> Root:
        with self.file_path.open("r") as f:
            return Root.model_validate_json(f.read())

    
