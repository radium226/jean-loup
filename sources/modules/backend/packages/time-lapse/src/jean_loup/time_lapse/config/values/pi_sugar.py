from pydantic import BaseModel
from ...types_for_pydantic import Path


class PiSugar(BaseModel):

    server_socket_path: Path