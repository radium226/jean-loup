from pydantic import BaseModel
from pathlib import Path


class PiSugar(BaseModel):

    server_socket_path: Path