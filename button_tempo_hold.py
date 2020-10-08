import gremlin
import time
import threading

from gremlin.user_plugin import *

# Simple button test plugin
_PLUGIN_NAME = "TempoHold"
_DEBUG = True  # extra log messages

# Settings
description = StringVariable(
    "Description", "Description of this plugin action", "", is_optional=True
)

mode = ModeVariable("Mode", "The mode to use for this mapping")

btn_input = PhysicalInputVariable(
    "Input Button",
    "Button which will be mapped by this plugin.",
    [gremlin.common.InputType.JoystickButton],
)

vjoy_btn = VirtualInputVariable(
    "Output Button",
    "vJoy button to use as the output.",
    [gremlin.common.InputType.JoystickButton],
)

cancel_enable = BoolVariable("Cancel button enabled", "Enables cancel button.", False)

tempo_cancel_btn = PhysicalInputVariable(
    "Tempo cancel button (physical)",
    "Button which will suppress tempo if pressed.",
    [gremlin.common.InputType.JoystickButton],
    is_optional=True,
)

hold1_enable = BoolVariable("Hold 1: Enable", "Enables Hold 1.", False)

hold1_description = StringVariable(
    "Hold 1: Description", "Description of hold 1 plugin action", "", is_optional=True
)

hold1_tempo_delay = FloatVariable(
    "Hold 1: Tempo Delay",
    "Long press delay to activate Hold 1 (s).",
    initial_value=0.5,
    min_value=0,
)

hold1_hold_time = FloatVariable(
    "Hold 1: Hold Time",
    "Time to hold virtual button before releasing for Hold 1 (s).",
    initial_value=5,
    min_value=0,
    max_value=1e6,
)

hold1_use_modifier = BoolVariable(
    "Hold 1: Use Modifier", "Enables modifier button for hold 1.", False
)

hold1_modifier_btn = PhysicalInputVariable(
    "Hold 1: Modifier Button (physical)",
    "Button which must be pressed to activate hold 1.",
    [gremlin.common.InputType.JoystickButton],
    is_optional=True,
)

# add both a physical button and vjoy modifier, to allow users to use either
hold1_use_vjoy_modifier = BoolVariable(
    "Hold 1: Use vJoy Modifier", "Enables vJoy modifier button for hold 1.", False
)

hold1_vjoy_modifier_btn = VirtualInputVariable(
    "Hold 1: Modifier Button (vJoy)",
    "vJoy button which must be pressed to activate hold 1.",
    [gremlin.common.InputType.JoystickButton],
    is_optional=True,
)


# DONE Optional modifier
# TODO Add extra hold (Hold 2)
# DONE Add Description generic, and one for all Holds
# TODO Add Tempo Cancel button (set time to 0, and do a time != 0 check)

# Process settings

gremlin.util.log(f"{_PLUGIN_NAME}: Activating...")
gremlin.util.log(f"{_PLUGIN_NAME}: Input is {btn_input.value}")
gremlin.util.log(f"{_PLUGIN_NAME}: Mode is {mode.value}")

target_vjoy_id = vjoy_btn.vjoy_id
target_input_id = vjoy_btn.input_id

gremlin.util.log(
    f"{_PLUGIN_NAME}: Target vjoy_id: {target_vjoy_id}; input_id {target_input_id}"
)

# Cancel button
# If pressed, will cancel any ongoing Tempo
cancel_is_enabled = bool(cancel_enable.value)

# Prepare cancel decorator
if cancel_is_enabled:
    if not tempo_cancel_btn.value:
        gremlin.util.log(f"{_PLUGIN_NAME}: Invalid cancel button, cancel disabled")
        cancel_is_enabled = False
    else:
        gremlin.util.log(f"{_PLUGIN_NAME}: Cancel button is {tempo_cancel_btn.value}")
        tempo_cancel_btn.value
        cancel_decorator = tempo_cancel_btn.create_decorator(mode.value)

        @cancel_decorator.button(tempo_cancel_btn.input_id)
        def cancel_button(event):
            global input_button_start_time
            if _DEBUG:
                gremlin.util.log(
                    f"{_PLUGIN_NAME}: Cancel button state change: {event.is_pressed}"
                )
            if event.is_pressed:
                input_button_start_time = 0


if not cancel_is_enabled:
    gremlin.util.log(f"{_PLUGIN_NAME}: Cancel button disabled")

# Options for hold1
hold1_is_enabled = bool(hold1_enable.value)  # seems to have value '2' if enabled?
hold1_tempo_value = hold1_tempo_delay.value
hold1_hold_value = hold1_hold_time.value

hold1_modifier_is_enabled = bool(hold1_use_modifier.value)
hold1_vjoy_modifier_is_enabled = bool(hold1_use_vjoy_modifier.value)

gremlin.util.log(
    f"{_PLUGIN_NAME}: Hold1 (Enabled: {hold1_is_enabled}) Tempo: {hold1_tempo_value} s; Hold {hold1_hold_value} s"
)

if hold1_modifier_is_enabled:
    hold1_modifier_guid = hold1_modifier_btn.device_guid
    hold1_modifier_input_id = hold1_modifier_btn.input_id
    gremlin.util.log(
        f"{_PLUGIN_NAME}: Hold1 modifier guid: {hold1_modifier_guid}; input_id {hold1_modifier_input_id}"
    )
    if hold1_modifier_guid is None or hold1_modifier_input_id is None:
        hold1_modifier_is_enabled = False
        gremlin.util.log(f"{_PLUGIN_NAME}: Hold1 modifier is invalid so is disabled")
else:
    hold1_modifier_guid = None
    hold1_modifier_input_id = None

if not hold1_modifier_is_enabled:
    gremlin.util.log(f"{_PLUGIN_NAME}: Hold1 modifier disabled")


if hold1_vjoy_modifier_is_enabled:
    hold1_vjoy_modifier_id = hold1_vjoy_modifier_btn.vjoy_id
    hold1_vjoy_modifier_input_id = hold1_vjoy_modifier_btn.input_id
    gremlin.util.log(
        f"{_PLUGIN_NAME}: Hold1 vJoy modifier guid: {hold1_vjoy_modifier_id}; input_id {hold1_vjoy_modifier_input_id}"
    )
else:
    hold1_vjoy_modifier_id = None
    hold1_vjoy_modifier_input_id = None

if not hold1_vjoy_modifier_is_enabled:
    gremlin.util.log(f"{_PLUGIN_NAME}: Hold1 vJoy modifier disabled")


# Prepare decorator
if not btn_input.value:
    gremlin.util.log(f"{_PLUGIN_NAME}: Invalid input, cannot activate plugin")

input_decorator = btn_input.create_decorator(mode.value)

# State variables
input_button_start_time = 0
hold_timer = None

# Implementation


def output_button(pressed_state, vjoy):
    if _DEBUG:
        gremlin.util.log(f"{_PLUGIN_NAME}: Setting output state to {pressed_state}")
    vjoy[target_vjoy_id].button(target_input_id).is_pressed = pressed_state


# Called by a threading.Timer
def stop_hold(vjoy):
    if _DEBUG:
        gremlin.util.log(f"{_PLUGIN_NAME}: Ending hold from timer.")
    output_button(False, vjoy)


def check_hold1_modifier(joy, vjoy):
    # if a modifier is enabled, return state of modifier
    if hold1_modifier_is_enabled:
        modifier_state = (
            joy[hold1_modifier_guid].button(hold1_modifier_input_id).is_pressed
        )
        if _DEBUG:
            gremlin.util.log(
                f"{_PLUGIN_NAME}: Hold1 modifier enabled; pressed: {modifier_state}"
            )
        return modifier_state
    elif hold1_vjoy_modifier_is_enabled:
        modifier_state = (
            vjoy[hold1_vjoy_modifier_id].button(hold1_vjoy_modifier_input_id).is_pressed
        )
        if _DEBUG:
            gremlin.util.log(
                f"{_PLUGIN_NAME}: Hold1 vjoy modifier enabled; pressed: {modifier_state}"
            )
        return modifier_state
    else:
        # no modifiers enabled, default to true
        if _DEBUG:
            gremlin.util.log(f"{_PLUGIN_NAME}: Hold1 no modifier enabled")
        return True


@input_decorator.button(btn_input.input_id)
def input_button(event, joy, vjoy):
    if _DEBUG:
        gremlin.util.log(f"{_PLUGIN_NAME}: Input button state: {event.is_pressed}")
    global input_button_start_time, hold_timer
    if event.is_pressed:
        if _DEBUG:
            gremlin.util.log(f"{_PLUGIN_NAME}: Processing press...")
        # send 'pressed' to target
        output_button(True, vjoy)
        # store start time
        if hold1_is_enabled:
            input_button_start_time = time.time()
            # cancel any current hold timer
            if hold_timer is not None:
                if _DEBUG:
                    gremlin.util.log(
                        f"{_PLUGIN_NAME}: (press) Cancelling previous Hold1 timer."
                    )
                hold_timer.cancel()
                hold_timer = None
        else:
            if _DEBUG:
                gremlin.util.log(f"{_PLUGIN_NAME}: (press) Hold1 is not enabled.")
    else:
        if _DEBUG:
            gremlin.util.log(f"{_PLUGIN_NAME}: Processing release...")
        curtime = time.time()
        if hold1_is_enabled:
            if (
                input_button_start_time > 0
                and curtime >= input_button_start_time + hold1_tempo_value
                and check_hold1_modifier(joy, vjoy)
            ):
                if _DEBUG:
                    gremlin.util.log(f"{_PLUGIN_NAME}: Hold1 Tempo activated.")
                # tempo activated
                # activate hold: start thread and do not release until
                #   reaching input_button_start_time + hold1_hold_time
                if hold_timer is not None:
                    # expect this not to occur (should be cancelled on press)
                    if _DEBUG:
                        gremlin.util.log(
                            f"{_PLUGIN_NAME}: (release) Cancelling previous Hold1 timer."
                        )
                    hold_timer.cancel()
                    hold_timer = None
                remaining_time = input_button_start_time + hold1_hold_value - curtime
                if _DEBUG:
                    gremlin.util.log(
                        f"{_PLUGIN_NAME}: Timed release for Hold1 is {remaining_time} s from now."
                    )
                if remaining_time < 0:
                    if _DEBUG:
                        gremlin.util.log(
                            f"{_PLUGIN_NAME}: Hold1 Hold time exceeded, sending release immediately."
                        )
                    output_button(False, vjoy)
                else:
                    hold_timer = threading.Timer(remaining_time, stop_hold, args=[vjoy])
                    hold_timer.start()
            else:
                if _DEBUG:
                    gremlin.util.log(
                        f"{_PLUGIN_NAME}: Hold1 Tempo not activated (delay not exceeded/modifier not pressed)."
                    )
                output_button(False, vjoy)
        else:
            if _DEBUG:
                gremlin.util.log(f"{_PLUGIN_NAME}: (release) Hold1 is not enabled.")
            output_button(False, vjoy)