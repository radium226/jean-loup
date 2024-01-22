from click import (
    Context,
    command, 
    pass_context,
)


@command
@pass_context
def handle_event(context: Context):
    pass