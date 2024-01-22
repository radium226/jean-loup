from click import (
    Context,
    command, 
    pass_context,
)


@command
@pass_context
def website(context: Context):
    pass