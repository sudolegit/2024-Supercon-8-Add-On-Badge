import nunchuk

WII_NUNCHUCK_ADDRESS 	= 0x52

JOYSTICK_MIDPOINT_X		= 135
JOYSTICK_MIDPOINT_Y		= 125


wii_controller			= None

def configure(i2c0, i2c1):
    global wii_controller
    
    # Locate Wii Nunchuck
    wii_bus = None
    try:
        i2c0.readfrom_mem(WII_NUNCHUCK_ADDRESS, 0, 1)
        wii_bus = i2c0
    except:
        try:
            i2c1.readfrom_mem(WII_NUNCHUCK_ADDRESS, 0, 1)
            wii_bus = i2c1
        except:
            pass
    
    # Connect to Wii Nunchuck
    try:
        if wii_bus != None and wii_controller == None:
            wii_controller = nunchuk.Nunchuk(wii_bus)
            print("Wii Nunchuk connected")
        elif wii_bus == None:
            raise
    except:
        if wii_controller:
            print("Wii Nunchuk disconnected")
        wii_controller = None
    
    # Return handle if connected; else 'None'
    return wii_controller


