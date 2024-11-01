import nunchuk

WII_NUNCHUCK_ADDRESS = 0x52

def configure(i2c0, i2c1):
    global wii_controller
    
    # Locate Wii Nunchuck
    wii_bus			= None
    wii_controller	= None
    try:
        i2c0.readfrom_mem(WII_NUNCHUCK_ADDRESS, 0, 1)
        wii_bus = i2c0
        print("Wii Nunchuck using I2C0")
    except:
        try:
            i2c1.readfrom_mem(WII_NUNCHUCK_ADDRESS, 0, 1)
            wii_bus = i2c1
            print("Wii Nunchuck using I2C1")
        except:
            print("Warning:  Wii Nunchuck not found")
    
    # Unlock Wii Nunchuck
    try:
        wii_controller = nunchuk.Nunchuk(wii_bus)
        print("Wii Nunchuk connected")
    except:
        print("Warning:  Failed to connect to Wii Nunchuk")
    
    return wii_controller

