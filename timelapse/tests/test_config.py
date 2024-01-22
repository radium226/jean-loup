from pytest import fixture
from tempfile import TemporaryDirectory
from typing import Generator
from pathlib import Path
from textwrap import dedent

from timelapse.config import Config

@fixture
def config_file_path() -> Generator[Path, None, None]:
    with TemporaryDirectory() as temp_folder_path:
        file_path = Path(temp_folder_path) / "config.json"
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
        yield file_path

def test_config(
    config_file_path: Path,    
) -> None:
    config = Config.default()
    assert config.values.hotspot.enabled

    config = config.override_with(Config.from_file(config_file_path))
    assert not config.values.hotspot.enabled

    config = config.override_with(Config(dict(hotspot=dict(enabled=True))))
    assert config.values.hotspot.enabled