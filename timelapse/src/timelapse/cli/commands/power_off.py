from click import (
    Context,
    command, 
    pass_context,
)

from ...service import Service


@command
@pass_context
def power_off(context: Context):
    config = context.obj.config
    with Service(config) as service:
        service.power_off()
