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
release.

6) Any press of the physical button will cancel an existing programmed hold, 
and be processed as a new press.

Available settings are:

`Description`: (Optional) Arbitrary string, does nothing but functions as a user
comment.

`Mode`: Mode in which this plugin is activated.

`Input Button`: Physical button that is to be mapped, monitored for press/release
events.

`Output Button`: Virtual vJoy button that will receive press/release events.

`Cancel Button Enabled`: Enables the `Tempo Cancel Button`.

`Tempo Cancel Button`: (Optional) Physical button that, when pressed, will cancel 
any existing tempo hold. Useful if set as the second stage of a two-stage trigger,
as noted above.

`Hold 1: Enable`: Enables programmed timed release (hold) 1.

`Hold 1: Description`: (Optional) Arbitrary string, does nothing but functions as 
a user comment.

`Hold 1: Tempo Delay`: Tempo delay time (seconds) to activate hold 1. If physical 
button is held down for > this time, the programmed timed release will activate
(provided any modifier options also pass).

`Hold 1: Use Modifier`: Enables `Hold 1: Modifier Button (vJoy)`.

`Hold 1: Modifier Button (vJoy)`: vJoy button that must be pressed when a
release of physical button is processed in order to activate hold 1. This is
tested in addition to any tempo delay.

Note that the modifier must be a vJoy button. Therefore, a user must map a
physical button to a vJoy button for use as a modifier.

All the `Hold 1` options are repeated for a second optional `Hold 2`. Note that
if only different tempo times differentiate `Hold 1` and `Hold 2`, then the longer
tempo delay should be used for `Hold 2`. This is because `Hold 2` is processed
first. Setting a longer tempo delay to `Hold 2` will therefore ensure it is only
activated if this longer time is exceeded, otherwise `Hold 1` is processed. If
a shorter tempo delay is used for `Hold 2`, it will always activate and `Hold 1`
will never be processed.

Note: This repository also has some test/example Joystick Gremlin plugins that
are not described here.