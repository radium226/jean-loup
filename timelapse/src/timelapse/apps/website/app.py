from pathlib import Path
from click import (
    Choice,
    command,
    option,
)
from ipaddress import IPv4Address

from ...config import Config
from .website import Website
from .endpoint_type import EndpointType


@command
@option("--config-file", "config_file_path", type=Path, required=False, default=None)
@option("--ui-folder", "ui_folder_path", type=Path, required=False, default=None)
@option("--host", type=IPv4Address, required=False, default=None)
@option("--port", type=int, required=False, default=None)
@option("--ui-folder", "ui_folder_path", type=Path, required=False, default=None)
@option("--dry-run", "dry_run", is_flag=True, required=False, default=False)
@option("--exclude-endpoint", "excluded_endpoint_types", multiple=True, type=Choice([endpoint_type for endpoint_type in EndpointType]), required=False, default=[])
def app(
    config_file_path: Path | None, 
    ui_folder_path: Path | None, 
    excluded_endpoint_types: list[EndpointType],
    dry_run: bool, 
    host: IPv4Address | None, 
    port: int | None
):
    website_dict: dict = {}
    if ui_folder_path:
        website_dict["ui_folder_path"] = ui_folder_path
    if host:
        website_dict["host"] = host
    if port:
        website_dict["port"] = port
    config = (
        Config.default()
            .override_with(
                Config.from_file(config_file_path)
            )
            .override_with(dict(website=website_dict))
    )

    endpoint_types = [endpoint_type for endpoint_type in EndpointType if endpoint_type not in excluded_endpoint_types]
    with Website(
        config, 
        dry_run=dry_run,
        endpoint_types=endpoint_types
    ) as website:
        website.serve_forever()
     