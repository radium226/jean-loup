from pydantic import BaseModel


class Hotspot(BaseModel):

    enabled: bool

    ssid: str