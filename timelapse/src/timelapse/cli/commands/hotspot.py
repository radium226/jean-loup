from click import (
    Context,
    command, 
    pass_context,
)


@command
@pass_context
def hotspot(context: Context):
    pass