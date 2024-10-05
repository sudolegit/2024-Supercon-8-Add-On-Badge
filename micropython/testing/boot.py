## HAL / devices here

from machine import I2C, Pin
import time
import ssd1306

PETAL_ADDRESS      = 0x00
TOUCHWHEEL_ADDRESS = 0x54
SCREEN_ADDRESS     = 0x3C
## wrap this all up in a badge class eventually

# Testing options

## buttons
buttonA = Pin(8, Pin.IN, Pin.PULL_UP)
buttonB = Pin(9, Pin.IN, Pin.PULL_UP)
buttonC = Pin(28, Pin.IN, Pin.PULL_UP)

## debug pin!
# p = Pin(7, Pin.OUT)
# p.value(1)

## GPIOs

## Initialize I2C peripherals
i2c0 = I2C(0, sda=Pin(0), scl=Pin(1), freq=400_000)
i2c1 = I2C(1, sda=Pin(26), scl=Pin(27), freq=400_000)

def which_bus_has_device_id(i2c_id, debug=False):
    '''Returns a list of i2c bus objects that have the requested id on them.
    Note this can be of length 0, 1, or 2 depending on which I2C bus the id is found'''

    i2c0_bus = i2c0.scan() 
    if debug:
        print("Bus 0: ")
        print(str([hex(x) for x in i2c0_bus]))

    i2c1_bus = i2c1.scan()
    if debug:
        print("Bus 1: ")
        print(str([hex(x) for x in i2c1_bus]))

    busses = []
    if i2c_id in i2c0_bus:
        busses.append(i2c0)
    if i2c_id in i2c1_bus:
        busses.append(i2c1)

    return(busses)

## Look for an SSD1306 screen on the bus
HAS_SCREEN = False
busses = which_bus_has_device_id(SCREEN_ADDRESS)
if len(busses) == 1:
    screen = ssd1306.SSD1306_I2C(128, 64, busses[0])
    HAS_SCREEN = True
else: 
    print(f"Warning: {len(busses)} busses found that match SSD1306 address.")

def petal_init(bus):
    """configure the petal SAO"""
    bus.writeto_mem(PETAL_ADDRESS, 0x09, bytes([0x00]))  ## raw pixel mode (not 7-seg) 
    bus.writeto_mem(PETAL_ADDRESS, 0x0A, bytes([0x09]))  ## intensity (of 16) 
    bus.writeto_mem(PETAL_ADDRESS, 0x0B, bytes([0x07]))  ## enable all segments
    bus.writeto_mem(PETAL_ADDRESS, 0x0C, bytes([0x81]))  ## undo shutdown bits 
    bus.writeto_mem(PETAL_ADDRESS, 0x0D, bytes([0x00]))  ##  
    bus.writeto_mem(PETAL_ADDRESS, 0x0E, bytes([0x00]))  ## no crazy features (default?) 
    bus.writeto_mem(PETAL_ADDRESS, 0x0F, bytes([0x00]))  ## turn off display test mode 

## can't use scan logic for petal b/c it's at address 0
## so wrapping the init routine it try: blocks should also work
## later on can test if petal_bus is None
petal_bus = None
try:
    petal_init(i2c0)
    petal_bus = i2c0
except: 
    pass
try:
    petal_init(i2c1)
    petal_bus = i2c1
except:
    pass
if not petal_bus:
    print(f"Warning: Petal not found.")


## waiting for wheel with a yellow light
petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x80]))
petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))

## touchwheel last, with a wait loop,  b/c it doesn't init until animation is over
## probably need to implement a timeout here?
touchwheel_bus = None
touchwheel_counter = 0
while not touchwheel_bus:
    try:
        touchwheel_bus =  which_bus_has_device_id(0x54)[0]
    except:
        pass
    time.sleep_ms(100)
    touchwheel_counter = touchwheel_counter + 1
    if touchwheel_counter > 50:
        break
if not touchwheel_bus:
    print(f"Warning: Touchwheel not found.")


def touchwheel_read(bus):
    """Returns 0 for no touch, 1-255 clockwise around the circle from the south"""
    return(touchwheel_bus.readfrom_mem(84, 0, 1)[0])

def touchwheel_rgb(bus, r, g, b):
    """RGB color on the central display.  Each 0-255"""
    touchwheel_bus.writeto_mem(84, 15, bytes([r]))
    touchwheel_bus.writeto_mem(84, 16, bytes([g]))
    touchwheel_bus.writeto_mem(84, 17, bytes([b]))


## goes green if wheel configured
if touchwheel_bus:
    petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))
petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
time.sleep_ms(200)
petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))


