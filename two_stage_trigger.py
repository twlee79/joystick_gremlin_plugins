import gremlin
import time
import threading
from gremlin.user_plugin import *


mode = ModeVariable("Mode", "The mode to use for this mapping")


from vjoy.vjoy import AxisName
def set_throttle(vjoy, value):
    vjoy[2].axis(AxisName.Z).value = value

@gremlin.input_devices.keyboard("1", mode.value)
def throttle_0(event, vjoy):
    gremlin.util.log(f"{_PLUGIN_NAME}: throttle_0.")
    #gremlin.util.log("throttle_0.")
    if event.is_pressed:
        set_throttle(vjoy, -1.0)

@gremlin.input_devices.keyboard("2", mode.value)
def throttle_33(event, vjoy):
    if event.is_pressed:
        set_throttle(vjoy, -0.33)

@gremlin.input_devices.keyboard("3", mode.value)
def throttle_66(event, vjoy):
    if event.is_pressed:
        set_throttle(vjoy, 0.33)


_PLUGIN_NAME = "TempoHold"

btn_input = PhysicalInputVariable(
    "Input Button",
    "Button which will be mapped to this plugin.",
    [gremlin.common.InputType.JoystickButton],
)


gremlin.util.log(f"{_PLUGIN_NAME}: Input is {btn_input.value}")

if not btn_input.value: gremlin.util.log(f"{_PLUGIN_NAME}: Invalid input, cannot load plugin")

input_decorator = btn_input.create_decorator(mode.value)


@input_decorator.button(btn_input.input_id)
def input_button(event, vjoy):
    gremlin.util.log(f"{_PLUGIN_NAME}:button.")
    vjoy[1].button(1).is_pressed = event.is_pressed



"""

vjoy_btn = VirtualInputVariable(
    "Output Button",
    "vJoy button to use as the output",
    [gremlin.common.InputType.JoystickButton],
)


hold1_enable = BoolVariable("Hold 1: Enable", "Enables hold 1", False)

hold1_tempo_delay = FloatVariable(
    "Hold 1: Tempo Delay",
    "Long press delay to activate hold 1 (s).",
    0.5,
    min_value=0,
)

hold1_hold_time = FloatVariable(
    "Hold 1: Hold Time",
    "Time to hold virtual button before releasing for hold 1 (s).",
    2,
    min_value=0,
)

hold1_use_modifier = BoolVariable(
    "Hold 1: Use Modifier", "Enables modifier button for hold 1.", False
)

hold1_modifier_btn = PhysicalInputVariable(
    "Hold 1: Modifier Button",
    "Button which must be pressed to activate hold 1.",
    [gremlin.common.InputType.JoystickButton],
)


input_button_start_time = 0

hold_timer = None

target_vjoy_id = vjoy_btn.vjoy_id
target_input_id = vjoy_btn.input_id

hold1_modifier_device_guid = hold1_modifier_btn.device_guid
hold1_modifier_button_id = hold1_modifier_btn.input_id

gremlin.util.log(f"{_PLUGIN_NAME}: Activating...")
gremlin.util.log(
    f"{_PLUGIN_NAME}: Target vjoy_id: {target_vjoy_id};  input_id {target_input_id}"
)
gremlin.util.log(
    f"{_PLUGIN_NAME}: Hold1 modifier guid: {hold1_modifier_device_guid};  input_id {hold1_modifier_button_id}"
)



def vjoy_btn_send(pressed_state):
    gremlin.util.log(f"{_PLUGIN_NAME}: Setting output state to {pressed_state}")
    vjoy[target_vjoy_id].button(target_input_id).is_pressed = pressed_state


def stop_hold():
    gremlin.util.log(f"{_PLUGIN_NAME}: Stop hold registered.")
    vjoy_btn_send(False)

@input_decorator.button(btn_input.input_id)
def input_button(event, vjoy):
    global input_button_start_time
    gremlin.util.log(f"{_PLUGIN_NAME}: Entered decorator...")
    if event.is_pressed:
        gremlin.util.log(f"{_PLUGIN_NAME}: Input is pressed...")
        # send 'pressed' to target
        vjoy_btn_send(True)
        # store start time
        if hold1_enable.value:
            input_button_start_time = time.time()
            # cancel any current hold timer
            if hold_timer is not None:
                gremlin.util.log(f"{_PLUGIN_NAME}: (press) Cancelling Hold1 time.")
                hold_timer.cancel()
        else:
            gremlin.util.log(f"{_PLUGIN_NAME}: (press) Hold1 is not enabled.")
    else:
        gremlin.util.log(f"{_PLUGIN_NAME}: Input is released...")
        curtime = time.time()
        if hold1_enable.value:
            if curtime >= input_button_start_time + hold1_tempo_delay.value:
                gremlin.util.log(f"{_PLUGIN_NAME}: Hold1 Tempo activated.")
                # tempo activated
                # activate hold: start thread and do not release until
                #   reaching input_button_start_time + hold1_hold_time
                if hold_timer is not None:
                    gremlin.util.log(f"{_PLUGIN_NAME}: (release) Cancelling Hold1 time.")
                    hold_timer.cancel()
                remaining_time = input_button_start_time + hold1_hold_time.value - curtime
                gremlin.util.log(
                        f"{_PLUGIN_NAME}: Timing release for Hold1 is {remaining_time} s from now."
                )
                hold_timer = threading.Timer(remaining_time, stop_hold)
            else:
                gremlin.util.log(f"{_PLUGIN_NAME}: Hold1 Tempo delay is not exceeded.")
                vjoy_btn_send(False)
        else:
            gremlin.util.log(f"{_PLUGIN_NAME}: (release) Hold1 is not enabled.")
            vjoy_btn_send(False)
"""