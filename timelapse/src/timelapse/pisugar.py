class PiSugar:

    def __init__(self):
        pass

    def __enter__(self):
        self._write_config()
        return self
    
    def __exit__(self, type, value, traceback):
        pass

    @property
    def auto_power_on(self) -> bool:
        return self._auto_power_on
    
    @auto_power_on.setter
    def auto_power_on(self, value: bool) -> None:
        self._auto_power_on = value
        self._write_config()