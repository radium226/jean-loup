from pathlib import Path
from click import (
    command,
    option,
)
from ipaddress import IPv4Address

from ...config import Config
from .website import Website


@command
@option("--config-file", "config_file_path", type=Path, required=False, default=None)
@option("--ui-folder", "ui_folder_path", type=Path, required=False, default=None)
@option("--host", type=IPv4Address, required=False, default=None)
@option("--port", type=int, required=False, default=None)
@option("--ui-folder", "ui_folder_path", type=Path, required=False, default=None)
@option("--dry-run", is_flag=True, required=False, default=False)
def app(config_file_path: Path | None, ui_folder_path: Path | None, dry_run: bool, host: IPv4Address | None, port: int | None):
    config = (
        Config.default()
            .override_with(
                Config.from_file(config_file_path)
            )
            .override_with(
                Config(dict(
                    website=dict(
                        ui_folder_path=ui_folder_path,
                        host=host,
                        port=port
                    ),
                ))
            )
    )

    with Website(config, dry_run=dry_run) as website:
        website.serve_forever()
     