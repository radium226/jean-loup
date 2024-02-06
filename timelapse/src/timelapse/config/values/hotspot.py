from pydantic import BaseModel

from ...types_for_pydantic import IPv4Network

class Hotspot(BaseModel):

    enabled: bool

    ssid: str

    ip_network: IPv4Network

    wireless_hardware_device: str

    domain: str