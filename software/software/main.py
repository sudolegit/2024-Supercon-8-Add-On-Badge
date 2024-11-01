from machine import I2C, Pin
import time
import wii

counter = 0

## do a quick spiral to test
if petal_bus:
    for j in range(8):
        which_leds = (1 << (j+1)) - 1 
        for i in range(1,9):
            print(which_leds)
            petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))
            time.sleep_ms(30)
            petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))

controller 				= None
prev_accel_x_ref_point 	= 0
rotation 				= 0
while True:
    controller = wii.configure(i2c0, i2c1)

    ## see what's going on with the touch wheel
    if touchwheel_bus:
        tw = touchwheel_read(touchwheel_bus)

    ## display touchwheel on petal
    if petal_bus and touchwheel_bus:
        
        check_for_rollover = False
        
        # Drive petal using touchwheel
        if tw > 0:
            tw = (128 - tw) % 256
            petal = int(tw/32) + 1
            petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x80]))
        
        # Drive petal using joystick
        elif controller and (controller.joystick.x not in range(wii.JOYSTICK_MIDPOINT_X - 15, wii.JOYSTICK_MIDPOINT_X + 15) or controller.joystick.y not in range(wii.JOYSTICK_MIDPOINT_Y - 15, wii.JOYSTICK_MIDPOINT_Y + 15)):
            check_for_rollover = True
            petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
            
            # Check for rotation
            # - Static (no change)
            if controller.joystick.x in range(prev_joystick_x - 15, prev_joystick_x + 15) and controller.joystick.y in range(prev_joystick_y - 15, prev_joystick_y + 15):
                pass
            # - Counter clockwise
            elif ((controller.joystick.x > prev_joystick_x) and (controller.joystick.y > wii.JOYSTICK_MIDPOINT_Y)) or ((controller.joystick.x < prev_joystick_x) and (controller.joystick.y < wii.JOYSTICK_MIDPOINT_Y)):
                petal = petal - 1
            # - Clockwise
            else:
                petal = petal + 1
        
        # Drive petal using accelerometer (X axis)
        elif controller and controller.buttons.Z and prev_accel_x_ref_point != 0:
            check_for_rollover = True
            petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x80]))
            
            if controller.acceleration.x in range(prev_accel_x_ref_point - 25, prev_accel_x_ref_point + 25):
                rotation = 0
            elif controller.acceleration.x > prev_accel_x_ref_point:
                rotation = -1
            else:
                rotation = 1
            
            petal += rotation
            
            if rotation != 0:
                time.sleep_ms( min(200 - abs(controller.acceleration.x - prev_accel_x_ref_point), 200) )
        
        # Turn off petal and reset tracking vars
        else:
            # Reset accelerometer tracking
            rotation				= 0
            prev_accel_x_ref_point 	= 0
            
            # Clear LED state on petal
            petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))
            petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))
            petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x00]))
            
            # Clear petal LEDs (turn off)
            petal = 0
        
        # Handle rollover
        if check_for_rollover:
            if petal > 8:
                petal = 1
            elif petal < 1:
                petal = 8
        
        # Push petal values to target PCB
        for i in range(1,9):
            if i == petal:
                petal_bus.writeto_mem(0, i, bytes([0x7F]))
            else:
                petal_bus.writeto_mem(0, i, bytes([0x00]))

    # Track pertinent values
    if controller:
        prev_joystick_x = controller.joystick.x
        prev_joystick_y = controller.joystick.y
        if controller.buttons.Z and prev_accel_x_ref_point == 0:
            prev_accel_x_ref_point	= controller.acceleration.x
    else:
        prev_joystick_x = wii.JOYSTICK_MIDPOINT_X
        prev_joystick_y = wii.JOYSTICK_MIDPOINT_Y
        prev_accel_x_ref_point	= 0
    
    time.sleep_ms(20)
    bootLED.off()


