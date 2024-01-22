from click import (
    Context,
    command, 
    pass_context,
)

from ...service import Service


@command
@pass_context
def take_picture(context: Context):
    config = context.obj.config
    with Service(config) as service:
        service.take_picture()