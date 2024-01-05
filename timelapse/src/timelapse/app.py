from click import command, option, argument, echo, Choice, group, pass_context, Context, argument
from click_default_group import DefaultGroup
from enum import StrEnum, auto
from types import SimpleNamespace
from pathlib import Path

from .system import System

@group(cls=DefaultGroup, default="manage", default_if_no_args=True)
@pass_context
def app(context: Context):
    context.obj = SimpleNamespace()


@app.command()
@argument("file_path", type=Path)
@pass_context
def take_picture(context: Context, file_path: Path):
    with System() as system:
        system.take_picture(file_path)


@app.command()
@option("--threshold", "threshold_in_seconds", type=int, help="Threshold in seconds", default=60)
@pass_context
def manage(context: Context, threshold_in_seconds: int):
    with System() as system:
        if system.now().diff(system.wake_up_at).in_seconds() <= threshold_in_seconds:
            system.take_picture()
            system.schedule_wakeup(at=system.now().add(minutes=5))
            system.shutdown()
