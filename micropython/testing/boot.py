## HAL / devices here

from machine import I2C, Pin
import time

time.sleep(2.2)
## wrap this all up in a badge class eventually

# Testing options
HAS_SCREEN = True

if HAS_SCREEN:
    import ssd1306

## buttons
buttonA = Pin(8, Pin.IN, Pin.PULL_UP)
buttonB = Pin(9, Pin.IN, Pin.PULL_UP)
buttonC = Pin(28, Pin.IN, Pin.PULL_UP)

## GPIOs

## Initialize I2C peripherals
i2c0 = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
i2c1 = I2C(1, sda=Pin(26), scl=Pin(27), freq=400_000)

def which_bus_has_device_id(i2c_id_string, debug=True):
    '''Returns a list of i2c bus objects that have the requested id on them.
    Note this can be of length 0, 1, or 2 depending on which I2C bus the id is found'''

    i2c0_bus = [hex(x) for x in i2c0.scan()] 
    if debug:
        print("Bus 0: ")
        print(str(i2c0_bus))

    i2c1_bus = [hex(x) for x in i2c1.scan()] 
    if debug:
        print("Bus 1: ")
        print(str(i2c1_bus))

    busses = []
    if str(i2c_id_string) in i2c0_bus:
        busses.append(i2c0)
    if str(i2c_id_string) in i2c1_bus:
        busses.append(i2c1)

    return(busses)

## find first touchwheel
touchwheel_bus =  which_bus_has_device_id("0x54")[0]
def touchwheel_read(bus):
    """Returns 0 for no touch, 1-255 clockwise around the circle from the south"""
    return(touchwheel_bus.readfrom_mem(84, 0, 1)[0])

def touchwheel_rgb(bus, r, g, b):
    """RGB color on the central display.  Each 0-255"""
    touchwheel_bus.writeto_mem(84, 15, bytes([r]))
    touchwheel_bus.writeto_mem(84, 16, bytes([g]))
    touchwheel_bus.writeto_mem(84, 17, bytes([b]))


def flower_init(bus):
    """configure the petal SAO"""
    bus.writeto_mem(0, 0x09, bytes([0x00]))  ## raw pixel mode (not 7-seg) 
    bus.writeto_mem(0, 0x0A, bytes([0x09]))  ## intensity (of 16) 
    bus.writeto_mem(0, 0x0B, bytes([0x07]))  ## enable all segments
    bus.writeto_mem(0, 0x0C, bytes([0x81]))  ## undo shutdown bits 
    bus.writeto_mem(0, 0x0D, bytes([0x00]))  ##  
    bus.writeto_mem(0, 0x0E, bytes([0x00]))  ## no crazy features (default?) 
    bus.writeto_mem(0, 0x0F, bytes([0x00]))  ## turn off display test mode 

## one of these will fail out...
try:
    flower_init(i2c0)
except: 
    pass
try:
    flower_init(i2c1)
except:
    pass

if HAS_SCREEN:
    ## config screen
    busses = which_bus_has_device_id("0x3c")
    if len(busses) == 1:
        screen = ssd1306.SSD1306_I2C(128, 64, busses[0])


