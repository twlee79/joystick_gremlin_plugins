import gremlin
from gremlin.user_plugin import *

# Simple button test plugin

# Settings
mode = ModeVariable("Mode", "The mode to use for this mapping")

btn_input = PhysicalInputVariable(
    "Input Button",
    "Button which will be mapped by this plugin.",
    [gremlin.common.InputType.JoystickButton],
)

vjoy_btn = VirtualInputVariable(
    "Output Button",
    "vJoy button to use as the output",
    [gremlin.common.InputType.JoystickButton],
)

# Process settings
_PLUGIN_NAME = "ButtonPress"
_DEBUG = True # extra log messages

gremlin.util.log(f"{_PLUGIN_NAME}: Activating...")
gremlin.util.log(f"{_PLUGIN_NAME}: Input is {btn_input.value}")

target_vjoy_id = vjoy_btn.vjoy_id
target_input_id = vjoy_btn.input_id

gremlin.util.log(
    f"{_PLUGIN_NAME}: Target vjoy_id: {target_vjoy_id};  input_id {target_input_id}"
)

# Prepare decorator
if not btn_input.value: gremlin.util.log(f"{_PLUGIN_NAME}: Invalid input, cannot activate plugin")

input_decorator = btn_input.create_decorator(mode.value)

def output_button(pressed_state, vjoy):
    if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: Setting output state to {pressed_state}")
    vjoy[target_vjoy_id].button(target_input_id).is_pressed = pressed_state


@input_decorator.button(btn_input.input_id)
def input_button(event, vjoy):
    if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: Input button state: {event.is_pressed}")
    output_button(event.is_pressed, vjoy)

