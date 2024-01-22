from ..config import Config

class Service:

    def __init__(self, config: Config):
        pass

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        pass

    def power_off(self):
        pass