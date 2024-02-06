from pathlib import Path
from click import (
    command,
    option,
)

from .hotspot import Hotspot

from ...config import Config


@command
@option("--config-file", "config_file_path", type=Path, default=None)
def app(config_file_path: Path | None):
    config = (
        Config.default()
            .override_with(
                Config.from_file(config_file_path)
            )
    )
    with Hotspot(config) as hostpot:
        hostpot.serve_forever()