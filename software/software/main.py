from machine import I2C, Pin
import time
import wii
import macintosh


## Global constants
MAIN_LOOP_ITERATION_DELAY_MS	= 20										# Amount of time (in milliseconds) to delay between iterations of the main loop
CONTROL_MODES					= ('petal', 'macintosh')					# Tuple of all potential modes
MIN_MODE_SWITCH_HOLD_COUNT		= round(750 / MAIN_LOOP_ITERATION_DELAY_MS)	# Number of main loop iterations to detecta mode switch request before accepting it (~3/4 second)

## Global variables
controller 						= None										# Instance of Wii Nunchuk controller for querying nunchuk state
prev_accel_x_ref_point 			= 0											# Tracking variable - Wii Nunchuk - Acceleration X reference point
control_mode					= -1										# Tracks which CONTROL_MODES entry is active (what the Wii Nunchuk controls). Defautls to -1 so that when auto detection on the first loop iteration occurs it selects the first entry (zero-indexed tuple).
mode_switch						= (MIN_MODE_SWITCH_HOLD_COUNT - 1)			# Tracks how long the mode switch has been held. Defaults to max to trigger auto-detection of default mode on the first loop iteration.
mode_switch_delay				= 0											# Tracks if there should be a delay before you can switch modes back (min time in a mode state).

## do a quick spiral to test
if petal_bus:
    for j in range(8):
        which_leds = (1 << (j+1)) - 1 
        for i in range(1,9):
            print(which_leds)
            petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))
            time.sleep_ms(30)
            petal_bus.writeto_mem(PETAL_ADDRESS, i, bytes([which_leds]))

## Main loop
while True:
    ## Maintain I2C connections
    controller			= wii.configure(i2c0, i2c1)
    macintosh_connected	= macintosh.connect(i2c0, i2c1)
    
    ## Handle mode selection
    mode_switch = (mode_switch + 1) if (controller.buttons.C and controller.buttons.Z or control_mode == -1) else 0
    
    if mode_switch == MIN_MODE_SWITCH_HOLD_COUNT:
        control_mode = (control_mode + 1) % len(CONTROL_MODES)
        if control_mode == 0:
            petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
            petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x80]))
            petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x80]))
            time.sleep_ms(100)
            petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))
            petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))
            petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x00]))
        
        print(f"New control mode:  {CONTROL_MODES[control_mode]}")
        
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
        elif (	controller and 
                (CONTROL_MODES[control_mode] == 'petal' and not controller.buttons.C) and 
                (	controller.joystick.x not in range(wii.JOYSTICK_MIDPOINT_X - 15, wii.JOYSTICK_MIDPOINT_X + 15) or
                    controller.joystick.y not in range(wii.JOYSTICK_MIDPOINT_Y - 15, wii.JOYSTICK_MIDPOINT_Y + 15)
                )
            ):
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
        elif (	controller and
                (CONTROL_MODES[control_mode] == 'petal' and not controller.buttons.C) and 
                controller.buttons.Z and prev_accel_x_ref_point != 0
            ):
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
    
    time.sleep_ms(MAIN_LOOP_ITERATION_DELAY_MS)
    bootLED.off()


