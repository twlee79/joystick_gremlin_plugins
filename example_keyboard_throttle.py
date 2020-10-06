import gremlin
from vjoy.vjoy import AxisName

# this adapted is the Keyboard Controlled Throttle example 
# from https://whitemagic.github.io/JoystickGremlin/user_plugins/
# with added log messages for testing

gremlin.util.log("Keyboard throttle plugin activated")

def set_throttle(vjoy, value):
    vjoy[2].axis(AxisName.Z).value = value # changed here to vjoy 2

@gremlin.input_devices.keyboard("1", "Default")
def throttle_0(event, vjoy):
    gremlin.util.log("in throttle0")
    if event.is_pressed:
        set_throttle(vjoy, -1.0)

@gremlin.input_devices.keyboard("2", "Default")
def throttle_33(event, vjoy):
    gremlin.util.log("in throttle33")
    if event.is_pressed:
        set_throttle(vjoy, -0.33)

@gremlin.input_devices.keyboard("3", "Default")
def throttle_66(event, vjoy):
    gremlin.util.log("in throttle66")
    if event.is_pressed:
        set_throttle(vjoy, 0.33)

@gremlin.input_devices.keyboard("4", "Default")
def throttle_100(event, vjoy):
    gremlin.util.log("in throttle100")
    if event.is_pressed:
        set_throttle(vjoy, 1.0)