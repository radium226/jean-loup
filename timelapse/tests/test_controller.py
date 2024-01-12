from pytest import fixture
from pytest import mark
from tempfile import TemporaryDirectory
from pathlib import Path
import pendulum
from pendulum import Time
from typing import Generator

from timelapse.controller import Controller
from timelapse.event_type import EventType

from .fakes import FakePiSugar, FakeSystem, FakeCamera


@fixture
def camera() -> FakeCamera:
    return FakeCamera()


@fixture
def pisugar() -> FakePiSugar:
    return FakePiSugar()


@fixture
def system() -> FakeSystem:
    return FakeSystem()


@fixture
def data_folder_path() -> Generator[Path, None, None]:
    with TemporaryDirectory() as temp_folder_path:
        yield Path(temp_folder_path)


@fixture
def controller(
    camera: FakeCamera, pisugar: FakePiSugar, system: FakeSystem, data_folder_path: Path
) -> Controller:
    return Controller(
        pisugar=pisugar, system=system, camera=camera, data_folder_path=data_folder_path
    )


@mark.parametrize(
    "wakeup_time, number_of_services, number_of_pictures_taken",
    [
        (
            pendulum.now().subtract(minutes=42).time(),
            2,
            0,
        ),
        (
            None,
            2,
            0,
        ),
        (
            pendulum.now().subtract(seconds=15).time(),
            0,
            1,
        ),
    ],
)
def test_handle_powered_on_event(
    wakeup_time: Time,
    number_of_services: int,
    number_of_pictures_taken: int,
    controller: Controller,
    pisugar: FakePiSugar,
    system: FakeSystem,
    camera: FakeCamera,
):
    pisugar.wakeup_time = wakeup_time
    controller.handle_event(EventType.POWERED_ON)
    assert len(system.services) == number_of_services
    assert len(camera.pictures_taken) == number_of_pictures_taken


@mark.parametrize(
    "event_type",
    [event_type for event_type in EventType if event_type != EventType.POWERED_ON],
)
def test_handle_other_events(
    event_type: EventType,
    controller: Controller,
    pisugar: FakePiSugar,
    system: FakeSystem,
    camera: FakeCamera,
) -> None:
    controller.handle_event(event_type)
    match event_type:
        case EventType.POWER_BUTTON_TAPPED:
            assert not pisugar.is_powered_on
            assert not system.is_powered_on

        case EventType.CUSTOM_BUTTON_SINGLE_TAPPED:
            assert len(camera.pictures_taken) == 1

        case EventType.CUSTOM_BUTTON_LONG_TAPPED:
            assert pisugar.wakeup_time is not None

        case EventType.CUSTOM_BUTTON_DOUBLE_TAPPED:
            pass
