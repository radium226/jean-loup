from pytest import fixture
from tempfile import TemporaryDirectory
from typing import Generator
from pathlib import Path
from textwrap import dedent
from types import SimpleNamespace

from timelapse.config import Config

@fixture
def config_folder_path() -> Generator[Path, None, None]:
    with TemporaryDirectory() as temp_folder_path:
        yield Path(temp_folder_path)


@fixture(autouse=True)
def config_file_path(config_folder_path: Path) -> Path:
    file_path = config_folder_path / "config.json"
    with file_path.open("w") as f:
        f.write(
            dedent(
                """\
                    {
                        "hotspot": {
                            "enabled": true,
                            "ssid": "bamboo"
                        }
                    }
                """
            )
        )
    return file_path


@fixture
def config(settings_folder_path: Path) -> Config:
    return Config(folder_path=settings_folder_path)

def test_config(
    config_folder_path: Path,    
) -> None:

    obj = SimpleNamespace()
    obj.hotspot = SimpleNamespace()
    obj.hotspot.enabled = True

    old_config = Config(folder_path=config_folder_path)
    assert old_config.values.hotspot.ssid == "bamboo"

    new_config = Config({
        "hotspot": {
            "ssid": "flower",
            "enabled": False,
        },
    })

    config = old_config.override_with(new_config).override_with(Config(obj))
    assert config.values.hotspot.ssid == "flower"
    assert config.values.hotspot.enabled
    config.save_values(folder_path=config_folder_path)

    config = Config(folder_path=config_folder_path)
    assert config.values.hotspot.ssid == "flower"
