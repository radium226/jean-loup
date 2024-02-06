from click import (
    Context,
    command, 
    pass_context,
)

from ....controller import Controller


@command
@pass_context
def power_off(context: Context):
    config = context.obj.config
    dry_run = context.obj.dry_run
    with Controller(config, dry_run=dry_run) as controller:
        controller.power_off()
