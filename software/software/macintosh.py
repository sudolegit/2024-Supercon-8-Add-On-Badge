# I2C related constants
MACINTOSH_ADDRESS		= 0x0A

MACINTOSH_COMMAND_WRITE	= 10
MACINTOSH_COMMAND_READ	= 11

# Global variables
macintosh_bus			= None

def connect(i2c0, i2c1):
    
    global macintosh_bus
    
    # Locate Macintosh SAO
    macintosh_bus = None
    try:
        i2c0.readfrom_mem(MACINTOSH_ADDRESS, 0, 1)
        macintosh_bus = i2c0
    except:
        try:
            i2c1.readfrom_mem(MACINTOSH_ADDRESS, 0, 1)
            macintosh_bus = i2c1
        except:
            pass
    
    return 1 if macintosh_bus else 0


