from click import (
    Context,
    command, 
    pass_context,
)

from ...controller import Controller


@command
@pass_context
def take_picture(context: Context):
    config = context.obj.config
    with Controller(config) as controller:
        controller.power_off()