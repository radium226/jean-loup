from click import group, pass_context, Context
from click_default_group import DefaultGroup
from types import SimpleNamespace

from .controller import Controller


@group(cls=DefaultGroup, default="get-by", default_if_no_args=True)
@pass_context
def app(context: Context):
    context.obj = SimpleNamespace()


@app.command()
@pass_context
def get_by(context: Context):
    with Controller.create() as controller:
        controller.get_by()


# from click import command, option, argument, echo, Choice, group, pass_context, Context, argument
# from click_default_group import DefaultGroup
# from enum import StrEnum, auto
# from types import SimpleNamespace
# from pathlib import Path

# from .system import System


# class ButtonPressType(StrEnum):

#     SHORT = auto()
#     LONG = auto()
#     DOUBLE = auto()



# @group(cls=DefaultGroup, default="manage", default_if_no_args=True)
# @pass_context
# def app(context: Context):
#     context.obj = SimpleNamespace()


# @app.command()
# @argument("type", type=ButtonPressType)
# @pass_context
# def press_button(context: Context, type: ButtonPressType):
#     with System() as system:
#         match type:
#             case ButtonPressType.SHORT:
#                 # FIXME: In Ad-Hoc folder... 
#                 now = system.now()
#                 file_path = Path("/var/lib/timelapse") / "{date_time}.jpg".format(date_time=now.to_iso8601_string())
#                 system.take_picture(file_path)

#             case ButtonPressType.LONG:
#                 now = system.now()
#                 # system.auto_power_on = False
#                 system.wake_up_at = now.add(minutes=5)
#                 # system.shutdown()

#             case ButtonPressType.DOUBLE:
#                 print("double")


# @app.command()
# @option("--file", "file_path", type=Path, required=False, default=None, help="File path")
# @pass_context
# def take_picture(context: Context, file_path: Path | None):
#     with System() as system:
#         if not file_path:
#             now = system.now()
#             file_path = Path("/var/lib/timelapse") / "{date_time}.jpg".format(date_time=now.to_iso8601_string())
        
#         system.take_picture(file_path)


# @app.command()
# @pass_context
# def start(context: Context):
#     with System() as system:
#         now = system.now()
#         system.auto_power_on = False
#         system.wake_up_at = now.add(minutes=2)
#         # system.shutdown()


# @app.command()
# @option("--threshold", "threshold_in_seconds", type=int, help="Threshold (in seconds)", default=60)
# @option("--force", "force", is_flag=True, show_default=True, default=False, help="Force shutdown")
# @option("--dry-run", "dry_run", is_flag=True, show_default=True, default=False, help="Dry run")
# @option("--delay", "delay_in_minutes", default=2, help="Delay (in minutes)")
# @pass_context
# def manage(context: Context, threshold_in_seconds: int, delay_in_minutes: int, force: bool, dry_run: bool):
#     pass
#     # with System() as system:
#     #     now = system.now()
#     #     if force or now.diff(system.wake_up_at).in_seconds() <= threshold_in_seconds:
#     #         system.auto_power_on = False
#     #         system.wake_up_at = now.add(minutes=delay_in_minutes)
#     #         file_path = Path("/var/lib/timelapse") / "{date_time}.jpg".format(date_time=now.to_iso8601_string())
#     #         system.take_picture(file_path)
#     #         if not dry_run:
#     #             print("Actually shuting down...")
#     #             system.shutdown()
#     #         else:
#     #             print("We should have shut down...")
#     #     else:
#     #         system.wake_up_at = None
#     #         system.auto_power_on = True
