from pytest import fixture

from timelapse.config import Config
from timelapse.controller import Controller

from .mocks import (
    PiSugarMock, 
    SystemMock, 
    CameraMock,
    StorageMock,
)


@fixture
def config() -> Config:
    return Config.default()


@fixture
def pi_sugar() -> PiSugarMock:
    return PiSugarMock()


@fixture
def system() -> SystemMock:
    return SystemMock()


@fixture
def camera() -> CameraMock:
    return CameraMock()

@fixture
def storage() -> StorageMock:
    return StorageMock()


@fixture
def controller(config: Config, pi_sugar: PiSugarMock, system: SystemMock, camera: CameraMock, storage: StorageMock) -> Controller:
    return Controller(
        config,
        pi_sugar=pi_sugar, 
        system=system, 
        camera=camera,
        storage=storage,
    )