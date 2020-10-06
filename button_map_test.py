import gremlin
from gremlin.user_plugin import *

# Simple button test plugin

mode = ModeVariable("Mode", "The mode to use for this mapping")

btn_input = PhysicalInputVariable(
    "Input Button",
    "Button which will be mapped by this plugin.",
    [gremlin.common.InputType.JoystickButton],
)

_PLUGIN_NAME = "ButtonPress"
_DEBUG = True # extra log messages

gremlin.util.log(f"{_PLUGIN_NAME}: Activating...")
gremlin.util.log(f"{_PLUGIN_NAME}: Input is {btn_input.value}")

if not btn_input.value: gremlin.util.log(f"{_PLUGIN_NAME}: Invalid input, cannot load plugin")

input_decorator = btn_input.create_decorator(mode.value)

@input_decorator.button(btn_input.input_id)
def input_button(event, vjoy):
    if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: Input button state: {event.is_pressed}")
    vjoy[1].button(1).is_pressed = event.is_pressed

