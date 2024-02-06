from click import (
    Context,
    command, 
    pass_context,
    argument,
    Choice,
)

from ....models import EventType
from ....controller import Controller


@command
@argument("event_type", type=Choice([event_type for event_type in EventType]))
@pass_context
def handle_event(context: Context, event_type: EventType):
    config = context.obj.config
    dry_run = context.obj.dry_run
    with Controller(config, dry_run=dry_run) as controller:
        controller.handle_event(event_type)