from click import group, pass_context, Context, argument, option, Choice
from click_default_group import DefaultGroup
from types import SimpleNamespace
from pathlib import Path
from ipaddress import IPv4Network

from .controller import Controller
from .event_type import EventType
from .picture_format import PictureFormat
from .hotspot import HotSpot
from .website import Website


FILE_EXTENSIONS_BY_PICTURE_FORMAT = {
    PictureFormat.JPEG: "jpg",
    PictureFormat.PNG: "png",
}


@group(cls=DefaultGroup, default="handle-event", default_if_no_args=True)
@pass_context
def app(context: Context):
    context.obj = SimpleNamespace()


@app.command()
@argument("event_type", type=Choice([event_type for event_type in EventType]))
@pass_context
def handle_event(context: Context, event_type: EventType):
    with Controller.create() as controller:
        controller.handle_event(event_type)


@app.command()
@option(
    "--format",
    "picture_format",
    required=False,
    default=None,
    type=Choice([picture_format for picture_format in PictureFormat]),
    help="Picture format",
)
@argument(
    "file_path", type=Path, required=False, default=None
)
@pass_context
def take_picture(
    context: Context, file_path: Path | None, picture_format: PictureFormat | None
):  
    with Controller.create() as controller:
        if file_path and picture_format:
            controller.take_picture(file_path, picture_format)
        elif not file_path and not picture_format:
            controller.take_picture()
        elif file_path and not picture_format:
            controller.take_picture(file_path)
        elif picture_format and not file_path:
            controller.take_picture(picture_format)
        else:
            raise Exception("Invalid arguments! ")


@app.command()
@pass_context
def hotspot(context: Context):
    with HotSpot(IPv4Network("192.168.50.1/24", strict=False), "bamboo") as hotspot:
        hotspot.wait_for()


@app.command()
@pass_context
def website(context: Context):
    with Website() as website:
        website.wait_for()