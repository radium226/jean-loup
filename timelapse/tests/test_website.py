from typing import Generator, List
from ipaddress import IPv4Address
from pytest import fixture
import requests
from pydantic import TypeAdapter

from timelapse.models import Picture
from timelapse.config import Config
from timelapse.controller import Controller
from timelapse.apps.website import Website

from .mocks import CameraMock


@fixture(autouse=True)
def website(controller: Controller) -> Generator[Website, None, None]:
    config = Config.default().override_with(dict(
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
    print(text)
    picture = Picture.model_validate_json(text)
    print(picture)
    assert len(camera.pictures_taken) == 1