from pytest import fixture

from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

from timelapse.config import Config
from timelapse.controller import Controller

from .mocks import (
    PiSugarMock, 
    SystemMock, 
    CameraMock,
    StorageMock,
)


@fixture
def config_file_path() -> Generator[Path, None, None]:
    with TemporaryDirectory() as temp_folder_path:
        file_path = Path(temp_folder_path) / "config.json"
        yield file_path

@fixture
def config(config_file_path: Path) -> Config:
    return Config.default(config_file_path)


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