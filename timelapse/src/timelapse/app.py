from click import group, pass_context, Context, argument, option, Choice
from click_default_group import DefaultGroup
from types import SimpleNamespace
from pathlib import Path
from ipaddress import IPv4Network

from .controller import Controller
from .event_type import EventType
from .picture_format import PictureFormat
from .hotspot import HotSpot
from .website2 import Website
from .config import Config



FILE_EXTENSIONS_BY_PICTURE_FORMAT = {
    PictureFormat.JPEG: "jpg",
    PictureFormat.PNG: "png",
}


@group(cls=DefaultGroup, default="handle-event", default_if_no_args=True)
@option("--config-folder", "config_folder_path", type=Path, default=None)
@pass_context
def app(context: Context, config_folder_path: Path | None = None):
    context.obj = SimpleNamespace()
    context.obj.config = Config(folder_path=config_folder_path)


@app.command()
@argument("event_type", type=Choice([event_type for event_type in EventType]))
@pass_context
def handle_event(context: Context, event_type: EventType):
    config = context.obj.config
    with Controller.create(config) as controller:
        controller.handle_event(event_type)


@app.command()
@pass_context
def hotspot(context: Context):
    with HotSpot(IPv4Network("192.168.50.1/24", strict=False), "bamboo") as hotspot:
        hotspot.wait_for()


@app.command()
@option("--fake", is_flag=True, default=False)
@option("--ui-folder", "ui_folder_path", type=Path, default=None)
@pass_context
def website(context: Context, fake: bool, ui_folder_path: Path | None):
    with Website(ui_folder_path, config=context.obj.config) as website:
        website.serve_forever()


@app.command()
@pass_context
def generate_picture_thumbnails(context: Context):
    config = context.obj.config
    with Controller.create(config) as controller:
        for picture_file_path in controller.list_pictures():
            print(f"Dealing with {picture_file_path}... ")
            thumbail_file_path = picture_file_path.parent / "thumbnails" / picture_file_path.name
            if not thumbail_file_path.exists():
                thumbail_file_path.parent.mkdir(parents=True, exist_ok=True)
                with thumbail_file_path.open("wb") as f:
                    f.write(controller.generate_tumbnail(picture_file_path).read())


@app.command()
@pass_context
def take_picture(context: Context):
    config = context.obj.config
    with Controller.create(config) as controller:
        picture_content = controller.take_picture()
        controller.save_picture(picture_content)



@app.command()
@option("--is", "bool_to_exit_code", is_flag=True, default=False)
@argument("value_path", type=str)
@pass_context
def config(context: Context, bool_to_exit_code: bool, value_path: str):
    value = eval(f"context.obj.config.values.{value_path}")
    if bool_to_exit_code:
        exit(0 if value else 1)
    else:
        print(value)


@app.command()
@pass_context
def power_off(context: Context):
    config = context.obj.config
    with Controller.create(config) as controller:
        controller.power_off()