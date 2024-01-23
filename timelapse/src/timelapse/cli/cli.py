from pathlib import Path
from types import SimpleNamespace
from click import Context, pass_context, option, group

from ..config import Config
from .commands import (
    power_off,
    handle_event,
    hotspot,
    website,
    take_picture,
)


@group
@option("--config-file", "config_file_path", type=Path, default=None)
@pass_context
def CLI(context: Context, config_file_path: Path | None = None):
    context.obj = SimpleNamespace()
    context.obj.config = (
        Config.default()
            .override_with(
                Config.from_file(config_file_path)
            )
            .override_with(
                Config({
                        #FIXME: This is where we override config using options
                })
            )
    )


CLI.add_command(power_off)
CLI.add_command(handle_event)
CLI.add_command(hotspot)
CLI.add_command(website)
CLI.add_command(take_picture)