from typing import Generator, List
from ipaddress import IPv4Address
from pytest import fixture
import requests
from pydantic import TypeAdapter
from pathlib import Path
import json
from pendulum import Time

from timelapse.models import Picture
from timelapse.config import Config
from timelapse.controller import Controller
from timelapse.apps.website import Website

from .mocks import CameraMock
from .mocks import PiSugarMock


@fixture(autouse=True)
def website(controller: Controller, config: Config) -> Generator[Website, None, None]:
    config = config.override_with(dict(
        website=dict(
            host=IPv4Address("127.0.0.1"),
            port=9876,
        ),
    ))
    with Website(config, controller=controller) as website:
        yield website


def test_api_list_pictures():
    response = requests.get("http://127.0.0.1:9876/api/pictures")
    pictures = TypeAdapter(List[Picture]).validate_json(response.text)
    assert len(pictures) == 0


def test_api_take_picture(camera: CameraMock):
    response = requests.post("http://127.0.0.1:9876/api/pictures", headers={
        "Content-Type": "application/json",
    })
    text = response.text
    picture = Picture.model_validate_json(text)
    assert len(camera.pictures_taken) == 1


def test_api_write_config(config_file_path: Path, pi_sugar: PiSugarMock):
    response = requests.put(
        "http://127.0.0.1:9876/api/config", 
        headers={
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "time_lapse": {
                "wakeup_time": "16:12:00",
                "enabled": True
            }
        })
    )
    response.raise_for_status()

    assert pi_sugar.wakeup_time == Time(16, 12, 0)
    json.loads(config_file_path.read_text())["time_lapse"]["wakeup_time"] == "16:12:00"