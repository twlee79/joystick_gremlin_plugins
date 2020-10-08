import gremlin
import time
import threading

from gremlin.user_plugin import *

"""
Joystick Gremlin Button Hold Plugin

Implements a 'button hold' mapping for a physical button to an output vJoy 
button with a programmed timed release of the virtual button under various
customisable circumstances.
"""


_PLUGIN_NAME = "ButtonHold"
_VERSION = '1.0'
# -------------------------------------------------------------------------------
# Author:       Tet Woo Lee
#
# Created:      2020-10-09
# Copyright:    © 2020 Tet Woo Lee
# Licence:      GPLv3
#
# Dependencies: Joystick Gremlin, tested on v13.3
# -------------------------------------------------------------------------------

# -------------------------------------------------------------------------------
# ### Change log
#
# version 1.0 2020-10-09
# : First release version.
#
# version 0.9dev3 2020-10-09
# : Add hold multiplier to allow >100 s holds.
# : Add DEBUG option.
#
# version 0.9dev2 2020-10-09
# : Removed physical modifier; user can map a physical button to a vjoy button
# for use as a modifier.
#
# version 0.9dev1 2020-10-09
# : Initial working version, with two holds, tempo delay, physical/virtual 
# modifiers and a cancel button.
# -------------------------------------------------------------------------------


_DEBUG = False  # extra log messages

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

alternating_mode_enable = BoolVariable(
    "Enable Alternating Mode", 
    "Enables alternating hold/cancel mode.", 
    False)

cancel_enable = BoolVariable("Enable Cancel Button", "Enables cancel button.", False)

tempo_cancel_btn = PhysicalInputVariable(
    "Tempo cancel button",
    "Button which will suppress tempo if pressed.",
    [gremlin.common.InputType.JoystickButton],
    is_optional=True,
)

# Two set of hold options are enabled, which can be set with different tempos
# or different modifiers
# If using only different tempo times, note that longer tempo time should be
# set as hold2: hold2 is tested first, so needs to be a longer time so that it
# is only activated if this time is actually exceeded, otherwise hold1 is tested;
# if hold2 is the shorter time, it will always be activated and hold1 is never 
# # tested

# Hold 1 options
hold1_enable = BoolVariable("Hold 1: Enable", "Enables Hold 1.", False)

hold1_description = StringVariable(
    "Hold 1: Description", "Description of hold 1 plugin action", "", is_optional=True
)

hold1_tempo_delay = FloatVariable(
    "Hold 1: Tempo Delay",
    "Long press delay to activate Hold 1 (s).",
    initial_value=0.5,
    min_value=0,
    max_value=600,
)

hold1_hold_time = FloatVariable(
    "Hold 1: Hold Time",
    "Time to hold virtual button before releasing for Hold 1 (s).",
    initial_value=5,
    min_value=0,
    max_value=1e6,
)

# Multiplier is needed as there appears to be hard limit of 99.99 s on a FloatVariable
hold1_hold_time_multiplier = FloatVariable(
    "Hold 1: Hold Time Multiplier",
    "Multiplier for hold time.",
    initial_value=1,
    min_value=0,
    max_value=1e6,
)

# add only vjoy modifer, user can map a physical button to a vjoy button if needed
hold1_use_vjoy_modifier = BoolVariable(
    "Hold 1: Use Modifier", "Enables vJoy modifier button for hold 1.", False
)

hold1_vjoy_modifier_btn = VirtualInputVariable(
    "Hold 1: Modifier Button (vJoy)",
    "vJoy button which must be pressed to activate hold 1.",
    [gremlin.common.InputType.JoystickButton],
    is_optional=True,
)

# Hold 2 options
hold2_enable = BoolVariable("Hold 2: Enable", "Enables Hold 2.", False)

hold2_description = StringVariable(
    "Hold 2: Description", "Description of hold 2 plugin action", "", is_optional=True
)

hold2_tempo_delay = FloatVariable(
    "Hold 2: Tempo Delay",
    "Long press delay to activate Hold 2 (s).",
    initial_value=0.5,
    min_value=0,
    max_value=600,
)

hold2_hold_time = FloatVariable(
    "Hold 2: Hold Time",
    "Time to hold virtual button before releasing for Hold 2 (s).",
    initial_value=5,
    min_value=0,
    max_value=1e6,
)

# Multiplier is needed as there appears to be hard limit of 99.99 s on a FloatVariable
hold2_hold_time_multiplier = FloatVariable(
    "Hold 2: Hold Time Multiplier",
    "Multiplier for hold time.",
    initial_value=1,
    min_value=0,
    max_value=1e6,
)

# add only vjoy modifer, user can map a physical button to a vjoy button if needed
hold2_use_vjoy_modifier = BoolVariable(
    "Hold 2: Use Modifier", "Enables vJoy modifier button for hold 2.", False
)

hold2_vjoy_modifier_btn = VirtualInputVariable(
    "Hold 2: Modifier Button (vJoy)",
    "vJoy button which must be pressed to activate hold 2.",
    [gremlin.common.InputType.JoystickButton],
    is_optional=True,
)

enable_debug = BoolVariable(
    "Enable Debug Mode", "Produces additional log messages.", False
)

_DEBUG = enable_debug.value

# Process settings

gremlin.util.log(f"{_PLUGIN_NAME}: Activating...")
gremlin.util.log(f"{_PLUGIN_NAME}: Input is {btn_input.value}")
gremlin.util.log(f"{_PLUGIN_NAME}: Mode is {mode.value}")

target_vjoy_id = vjoy_btn.vjoy_id
target_input_id = vjoy_btn.input_id

gremlin.util.log(
    f"{_PLUGIN_NAME}: Target vjoy_id: {target_vjoy_id}; input_id {target_input_id}"
)

alternating_mode_is_enabled = bool(alternating_mode_enable.value)

gremlin.util.log(
    f"{_PLUGIN_NAME}: Alternating mode enabled: {alternating_mode_is_enabled}"
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

# Load options for hold1
hold1_is_enabled = bool(hold1_enable.value)  # seems to have value '2' if enabled?
hold1_tempo_value = hold1_tempo_delay.value
hold1_hold_value = hold1_hold_time.value * hold1_hold_time_multiplier.value

hold1_vjoy_modifier_is_enabled = bool(hold1_use_vjoy_modifier.value)

gremlin.util.log(
    f"{_PLUGIN_NAME}: Hold1 (Enabled: {hold1_is_enabled}) Tempo: {hold1_tempo_value} s; Hold {hold1_hold_value} s"
)

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

# Load options for hold2
hold2_is_enabled = bool(hold2_enable.value)  # seems to have value '2' if enabled?
hold2_tempo_value = hold2_tempo_delay.value
hold2_hold_value = hold2_hold_time.value * hold2_hold_time_multiplier.value

hold2_vjoy_modifier_is_enabled = bool(hold2_use_vjoy_modifier.value)

gremlin.util.log(
    f"{_PLUGIN_NAME}: Hold2 (Enabled: {hold2_is_enabled}) Tempo: {hold2_tempo_value} s; Hold {hold2_hold_value} s"
)

if hold2_vjoy_modifier_is_enabled:
    hold2_vjoy_modifier_id = hold2_vjoy_modifier_btn.vjoy_id
    hold2_vjoy_modifier_input_id = hold2_vjoy_modifier_btn.input_id
    gremlin.util.log(
        f"{_PLUGIN_NAME}: Hold2 vJoy modifier guid: {hold2_vjoy_modifier_id}; input_id {hold2_vjoy_modifier_input_id}"
    )
else:
    hold2_vjoy_modifier_id = None
    hold2_vjoy_modifier_input_id = None

if not hold2_vjoy_modifier_is_enabled:
    gremlin.util.log(f"{_PLUGIN_NAME}: Hold2 vJoy modifier disabled")


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
    global hold_timer
    output_button(False, vjoy)
    hold_timer = None


def check_hold1_modifier(joy, vjoy):
    # if a modifier is enabled, return state of modifier
    if hold1_vjoy_modifier_is_enabled:
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


def check_hold2_modifier(joy, vjoy):
    # if a modifier is enabled, return state of modifier
    if hold2_vjoy_modifier_is_enabled:
        modifier_state = (
            vjoy[hold2_vjoy_modifier_id].button(hold2_vjoy_modifier_input_id).is_pressed
        )
        if _DEBUG:
            gremlin.util.log(
                f"{_PLUGIN_NAME}: Hold2 vjoy modifier enabled; pressed: {modifier_state}"
            )
        return modifier_state
    else:
        # no modifiers enabled, default to true
        if _DEBUG:
            gremlin.util.log(f"{_PLUGIN_NAME}: Hold2 no modifier enabled")
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
        if alternating_mode_is_enabled and hold_timer:
            # in alternating mode, any existing timer is cancel and no new
            # timer is started
            # this is to allow a user to cancel a time and trigger a release
            # by pressing the button and releasing it
            if _DEBUG:
                gremlin.util.log(f"{_PLUGIN_NAME}: Alternating mode, cancelling timer.")
            hold_timer.cancel()
            hold_timer = None
            input_button_start_time = 0
        # store start time
        elif hold1_is_enabled or hold2_is_enabled:
            input_button_start_time = time.time()
            # cancel any current hold timer
            if hold_timer is not None:
                if _DEBUG:
                    gremlin.util.log(
                        f"{_PLUGIN_NAME}: (press) Cancelling previous Hold1/2 timer."
                    )
                hold_timer.cancel()
                hold_timer = None
        else:
            if _DEBUG:
                gremlin.util.log(f"{_PLUGIN_NAME}: (press) Hold1/2 is not enabled.")
    else:
        if _DEBUG:
            gremlin.util.log(f"{_PLUGIN_NAME}: Processing release...")
        curtime = time.time()
        if hold2_is_enabled and ( # test hold2 first
            input_button_start_time > 0
            and curtime >= input_button_start_time + hold2_tempo_value
            and check_hold2_modifier(joy, vjoy)
        ):
            if _DEBUG:
                gremlin.util.log(f"{_PLUGIN_NAME}: Hold2 Tempo activated.")
            # tempo activated
            # activate hold: start thread and do not release until
            #   reaching input_button_start_time + hold2_hold_time
            remaining_time = input_button_start_time + hold2_hold_value - curtime
            if _DEBUG:
                gremlin.util.log(
                    f"{_PLUGIN_NAME}: Timed release for Hold2 is {remaining_time} s from now."
                )
            if remaining_time < 0:
                if _DEBUG:
                    gremlin.util.log(
                        f"{_PLUGIN_NAME}: Hold2 Hold time exceeded, sending release immediately."
                    )
                output_button(False, vjoy)
            else:
                hold_timer = threading.Timer(remaining_time, stop_hold, args=[vjoy])
                hold_timer.start()
        elif hold1_is_enabled and (
            input_button_start_time > 0
            and curtime >= input_button_start_time + hold1_tempo_value
            and check_hold1_modifier(joy, vjoy)
        ):
            if _DEBUG:
                gremlin.util.log(f"{_PLUGIN_NAME}: Hold1 Tempo activated.")
            # tempo activated
            # activate hold: start thread and do not release until
            #   reaching input_button_start_time + hold1_hold_time
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
                    f"{_PLUGIN_NAME}: (release) Hold1 and Hold2 not enabled/activated."
                )
            output_button(False, vjoy)