from click import group, pass_context, Context, argument, option
from click_default_group import DefaultGroup
from types import SimpleNamespace
from pathlib import Path

from .controller import Controller
from .event_type import EventType
from .picture_format import PictureFormat


FILE_EXTENSIONS_BY_PICTURE_FORMAT = {
    PictureFormat.JPEG: "jpg",
    PictureFormat.PNG: "png",
}


@group(cls=DefaultGroup, default="handle-event", default_if_no_args=True)
@pass_context
def app(context: Context):
    context.obj = SimpleNamespace()


@app.command()
@argument("event_type", type=EventType)
@pass_context
def handle_event(context: Context, event_type: EventType):
    with Controller.create() as controller:
        controller.handle_event(event_type)


@app.command()
@option(
    "--picture-format",
    "picture_format",
    required=False,
    default=PictureFormat.PNG,
    type=PictureFormat,
    help="Picture format",
)
@argument(
    "file", "file_path", type=Path, required=False, default=None, help="File path"
)
@pass_context
def take_picture(
    context: Context, file_path: Path | None, picture_format: PictureFormat
):
    with Controller.create() as controller:
        # Generating file path if not provided
        if not file_path:
            date_time = controller.now()
            file_stem = "{date_time}".format(
                date_time=date_time.format("YYYY-MM-DD_HH-mm-ss")
            )
            file_extension = FILE_EXTENSIONS_BY_PICTURE_FORMAT[picture_format]
            file_name = "{stem}.{extension}".format(
                stem=file_stem, extension=file_extension
            )
            file_path = Path.cwd() / file_name

        # Taking picture
        controller.take_picture(file_path, picture_format)
