from pathlib import Path
from click import (
    command,
    option,
)

# from ...config import Config


@command
@option("--config-file", "config_file_path", type=Path, default=None)
@option("--ui-folder", "ui_folder_path", type=Path, default=None)
def app(config_file_path: Path | None, ui_folder_path: Path | None):
    pass