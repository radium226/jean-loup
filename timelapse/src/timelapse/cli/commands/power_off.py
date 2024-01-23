from click import (
    Context,
    command, 
    pass_context,
)

from ...controller import Controller


@command
@pass_context
def power_off(context: Context):
    config = context.obj.config
    with Controller(config) as controller:
        controller.power_off()
