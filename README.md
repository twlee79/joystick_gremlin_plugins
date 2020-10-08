# Button Hold Joystick Gremlin Plugin

The `button_hold.py` in this repository is a [Joystick Gremlin](https://github.com/WhiteMagic/JoystickGremlin)
plugin that implements a 'Button hold' mapping. The overall purpose of this 
plugin is to map a physical button to an output vJoy button with a programmed 
timed release of the virtual button, rather than immediate release. However,
a number of options are available that allow:

1) Immediate release normally, but programmed timed release if a tempo hold is
performed with the physical button.

2) Immediate release normally, but programmed timed release if a modifier 
button is also held down.

3) Combination of 1 and 2.

4) Two different programmed release times ('hold's), activated by different
tempos and/or holds.

5) A tempo 'cancel' button, that will cancel any tempo hold. The original 
intention of this is feature was customise a two-stage trigger. The first-stage
can be used as a tempo button to activate a programmed release, while activating
the second stage inactivates the tempo. This results in the second stage being
a 'normal' trigger, but the first stage being a 'tempo' trigger with timed
release. Note that this will *always* cancel processing of a hold, even if
the tempo delay is set to 0 s.

6) Any press of the physical button will cancel an existing programmed hold, 
and be processed as a new press.

7) If is possible to use no modifier and no tempo delay on a hold, in which
case the hold will always be activated. In this case, it is useful to either use
a 'cancel' button (see 5), or activate 'Alternating Mode' in which a new press
during an existing hold will cancel the existing hold and not activate a new 
hold, thereby triggering a normal virtual button release when the physical
button is released.

8) Although an indefinite hold is not possible, using a very long hold time will
be equivalent to this.

Available settings are:

`Description`: (Optional) Arbitrary string, does nothing but functions as a user
comment.

`Mode`: Mode in which this plugin is activated.

`Input Button`: Physical button that is to be mapped, monitored for press/release
events.

`Output Button`: Virtual vJoy button that will receive press/release events.

`Enable Alternating Mode`: Enables Alternating Mode. In Alternating Mode a
press of the physical button while a hold is activated, will cancel the hold
and not process a new hold. This allows a single press to always cancel the
current hold, and is useful if a hold is set to have a 0 s tempo delay and
no modifier, in which case the hold will always activate and otherwise interfere
with cancelling the hold with a quick press.

`Enable Cancel Button`: Enables the `Tempo Cancel Button`.

`Tempo Cancel Button`: (Optional) Physical button that, when pressed, will cancel 
any existing tempo hold. Useful if set as the second stage of a two-stage trigger,
as noted above.

`Hold 1: Enable`: Enables programmed timed release (hold) 1. Must be enabled to 
process this hold.

`Hold 1: Description`: (Optional) Arbitrary string, does nothing but functions as 
a user comment.

`Hold 1: Tempo Delay`: Tempo delay time (seconds) to activate hold 1. If physical 
button is held down for > this time, the programmed timed release will activate
(provided any modifier options also pass).

`Hold 1: Hold Time`: Once hold is activated, time (seconds) to wait until the 
virtual button is sent a button release. No button release is sent until this
time elapses. The programmed release time is relative to the time the physical
button was first pressed, not when it is released.

`Hold 2: Hold Time Multiplier`: Multiplier for the hold time. This exists because
there appears to be a hard limit of 99.99 on a `FloatVariable` enforced by
Joystick Gremlin, so a multiplier allows hold times 100 s or longer.

`Hold 1: Use Modifier`: Enables `Hold 1: Modifier Button (vJoy)`.

`Hold 1: Modifier Button (vJoy)`: vJoy button that must be pressed when a
release of physical button is processed in order to activate hold 1. This is
tested in addition to any tempo delay.

`Enable Debug Mode`: Enabling this will produce more log messages in the output.

Note that the modifier must be a vJoy button. Therefore, a user must map a
physical button to a vJoy button for use as a modifier.

All the `Hold 1` options are repeated for a second optional `Hold 2`. Note that
if only different tempo times differentiate `Hold 1` and `Hold 2`, then the longer
tempo delay should be used for `Hold 2`. This is because `Hold 2` is processed
first. Setting a longer tempo delay to `Hold 2` will therefore ensure it is only
activated if this longer time is exceeded, otherwise `Hold 1` is processed. If
a shorter tempo delay is used for `Hold 2`, it will always activate and `Hold 1`
will never be processed.

To use: Simply install using "Add Plugin" in Joystick Gremling (v13.3 tested), 
and set up the plugin options.

Note: This repository also houses some test/example Joystick Gremlin plugins that
are not described here.

```
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
```