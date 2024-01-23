from pytest import fixture
from pytest import mark
import pendulum
from pendulum import Time, DateTime

from timelapse.controller import Controller
from timelapse.models import EventType
from timelapse.config import Config

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


@mark.parametrize(
    "wakeup_time, number_of_services, number_of_pictures_taken, number_of_scheduled_services",
    [
        (
            pendulum.now().subtract(minutes=42).time(),
            2,
            0,
            1,
        ),
        (
            None,
            2,
            0,
            0,
        ),
        (
            pendulum.now().subtract(seconds=15).time(),
            0,
            1,
            1,
        ),
    ],
)
def test_handle_powered_on_event(
    wakeup_time: Time,
    number_of_services: int,
    number_of_pictures_taken: int,
    number_of_scheduled_services: int,
    controller: Controller,
    pi_sugar: PiSugarMock,
    system: SystemMock,
    camera: CameraMock,
):
    pi_sugar.wakeup_time = wakeup_time
    controller.handle_event(EventType.POWERED_ON)
    assert len(system.services) == number_of_services
    assert len(system.scheduled_services) == number_of_scheduled_services
    assert len(camera.pictures_taken) == number_of_pictures_taken


def test_handle_powered_on_event_without_wakeup_time(
    controller: Controller, pi_sugar: PiSugarMock, system: SystemMock, camera: CameraMock
):
    controller.handle_event(EventType.POWERED_ON)
    assert len(system.services) == 2
    assert len(camera.pictures_taken) == 0
    assert pi_sugar.wakeup_time is None


@mark.parametrize(
    "event_type",
    [event_type for event_type in EventType if event_type not in [EventType.POWERED_ON, EventType.TIMER_TRIGGERED]],
)
def test_handle_other_events(
    event_type: EventType,
    controller: Controller,
    pi_sugar: PiSugarMock,
    system: SystemMock,
    camera: CameraMock,
) -> None:
    controller.handle_event(event_type)
    match event_type:
        case EventType.POWER_BUTTON_TAPPED:
            assert not pi_sugar.is_powered_on
            assert not system.is_powered_on

        case EventType.CUSTOM_BUTTON_SINGLE_TAPPED:
            assert len(camera.pictures_taken) == 1

        case EventType.CUSTOM_BUTTON_LONG_TAPPED:
            assert pi_sugar.wakeup_time is not None

        case EventType.CUSTOM_BUTTON_DOUBLE_TAPPED:
            pass

@mark.parametrize(
    "wakeup_time, current_date_time, next_wakeup_date_time", 
    [
        (
            Time(23, 50, 0),
            DateTime(2024, 1, 15, 23, 50, 0),
            DateTime(2024, 1, 16, 0, 20, 0),
        ),
        (
            Time(12, 50, 0),
            DateTime(2024, 1, 15, 23, 50, 0),
            DateTime(2024, 1, 15, 13, 20, 0),
        ),
    ],
)
def test_handle_timer_triggered_event(
    wakeup_time: Time, current_date_time: DateTime, next_wakeup_date_time: DateTime,
    controller: Controller, pi_sugar: PiSugarMock, system: SystemMock, camera: CameraMock
) -> None:
    pi_sugar.wakeup_time = wakeup_time
    pi_sugar.override_now = current_date_time
    controller.handle_event(EventType.TIMER_TRIGGERED)
    assert system.scheduled_services[0][1] == next_wakeup_date_time
    assert pi_sugar.wakeup_time == next_wakeup_date_time.time()