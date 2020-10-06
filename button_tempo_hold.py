import gremlin
import time
import threading

from gremlin.user_plugin import *

# Simple button test plugin
_PLUGIN_NAME = "TempoHold"
_DEBUG = True # extra log messages

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

hold1_enable = BoolVariable("Hold 1: Enable", "Enables hold 1", False)

hold1_tempo_delay = FloatVariable(
    "Hold 1: Tempo Delay",
    "Long press delay to activate hold 1 (s).",
    initial_value=0.5,
    min_value=0,
)

hold1_hold_time = FloatVariable(
    "Hold 1: Hold Time",
    "Time to hold virtual button before releasing for hold 1 (s).",
    initial_value=5,
    min_value=0,
    max_value=1e6,
)

# Process settings

gremlin.util.log(f"{_PLUGIN_NAME}: Activating...")
gremlin.util.log(f"{_PLUGIN_NAME}: Input is {btn_input.value}")

target_vjoy_id = vjoy_btn.vjoy_id
target_input_id = vjoy_btn.input_id

gremlin.util.log(
    f"{_PLUGIN_NAME}: Target vjoy_id: {target_vjoy_id}; input_id {target_input_id}"
)

hold1_is_enabled = bool(hold1_enable.value) # seems to have value '2' if enabled?
hold1_tempo_value = hold1_tempo_delay.value
hold1_hold_value = hold1_hold_time.value

gremlin.util.log(
    f"{_PLUGIN_NAME}: Hold1 (Enabled: {hold1_is_enabled}) Tempo: {hold1_tempo_value} s; Hold {hold1_hold_value} s"
)

# Prepare decorator
if not btn_input.value: gremlin.util.log(f"{_PLUGIN_NAME}: Invalid input, cannot activate plugin")

input_decorator = btn_input.create_decorator(mode.value)

# State variables
input_button_start_time = 0
hold_timer = None

# Implementation

def output_button(pressed_state, vjoy):
    if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: Setting output state to {pressed_state}")
    vjoy[target_vjoy_id].button(target_input_id).is_pressed = pressed_state

# Called by a threading.Timer
def stop_hold(vjoy):
    if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: Ending hold from timer.")
    output_button(False, vjoy)


@input_decorator.button(btn_input.input_id)
def input_button(event, vjoy):
    if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: Input button state: {event.is_pressed}")
    global input_button_start_time, hold_timer
    if event.is_pressed:
        if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: Processing press...")
        # send 'pressed' to target
        output_button(True, vjoy)
        # store start time
        if hold1_is_enabled:
            input_button_start_time = time.time()
            # cancel any current hold timer
            if hold_timer is not None:
                if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: (press) Cancelling previous Hold1 timer.")
                hold_timer.cancel()
                hold_timer = None
        else:
            if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: (press) Hold1 is not enabled.")
    else:
        if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: Processing release...")
        curtime = time.time()
        if hold1_is_enabled:
            if curtime >= input_button_start_time + hold1_tempo_value:
                if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: Hold1 Tempo activated.")
                # tempo activated
                # activate hold: start thread and do not release until
                #   reaching input_button_start_time + hold1_hold_time
                if hold_timer is not None:
                    # expect this not to occur (should be cancelled on press)
                    if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: (release) Cancelling previous Hold1 timer.")
                    hold_timer.cancel()
                    hold_timer = None
                remaining_time = input_button_start_time + hold1_hold_value - curtime
                if _DEBUG: gremlin.util.log(
                    f"{_PLUGIN_NAME}: Timed release for Hold1 is {remaining_time} s from now."
                )
                if remaining_time<0:
                    if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: Hold1 Hold time exceeded, sending release immediately.")
                    output_button(False, vjoy)
                else:
                    hold_timer = threading.Timer(remaining_time, stop_hold, args = [vjoy])
                    hold_timer.start()
            else:
                if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: Hold1 Tempo not activated (delay not exceeded).")
                output_button(False, vjoy)
        else:
            if _DEBUG: gremlin.util.log(f"{_PLUGIN_NAME}: (release) Hold1 is not enabled.")
            output_button(False, vjoy)