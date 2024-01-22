from contextlib import ExitStack

from ..config import Config
from ..tools.camera import Camera, RaspberryPiCamera
from ..tools.storage import Storage, DataFolderStorage
from ..tools.system import System, SystemdSystem
from ..tools.battery import Battery, PiSugarBattery
from ..tools.clock import Clock, PiSugarClock

class Service:

    config: Config
    exit_stack: ExitStack
    camera: Camera
    system: System
    clock: Clock
    battery: Battery

    def __init__(self, config: Config, /, camera: Camera | None = None):
        self.config = config
        self.camera = camera or RaspberryPiCamera()
        self.system  = system or SystemdSystem()
        self.clock = clock or PiSugarClock()
        self.battery = battery or PiSugarBattery()
        self.storage = storage or DataFolderStorage()
        self.exit_stack = ExitStack()

    def __enter__(self):
        self.exit_stack.enter_context(self.camera)
        return self
    
    def __exit__(self, type, value, traceback):
        self.exit_stack.close()

    def power_off(self):
        pass

    def take_picture(self) -> None:
        self.camera.take_picture()