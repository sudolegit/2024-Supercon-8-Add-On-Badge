from machine import I2C, Pin
import time

while True:

    if HAS_SCREEN:
        screen.fill(0)

        screen.text("Hello Hackaday!", 10, 0)

        screen.text("Button A: ", 25, 20)
        screen.text(str(buttonA.value()), 100, 20)
        screen.text("Button B: ", 25, 30)
        screen.text(str(buttonB.value()), 100, 30)
        screen.text("Button C: ", 25, 40)
        screen.text(str(buttonC.value()), 100, 40)

        if touchwheel_bus:
            screen.text("Wheel: ", 25, 50)
            screen.text(str(touchwheel_read(touchwheel_bus)), 80, 50)

        screen.show()
    
    ## display button status on RGB
    if petal_bus:
        if not buttonA.value():
            petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x80]))
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 2, bytes([0x00]))

        if not buttonB.value():
            petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x80]))
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 3, bytes([0x00]))

        if not buttonC.value():
            petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x80]))
        else:
            petal_bus.writeto_mem(PETAL_ADDRESS, 4, bytes([0x00]))

    ## see what's going on with the touch wheel
    if touchwheel_bus:
        tw = touchwheel_read(touchwheel_bus)

    ## display touchwheel on petal
    if petal_bus and touchwheel_bus:
        if tw > 0:
            petal = int(tw/32) + 1
        else: 
            petal = 999
        for i in range(1,9):
            if i == petal:
                petal_bus.writeto_mem(0, i, bytes([0x7F]))
            else:
                petal_bus.writeto_mem(0, i, bytes([0x00]))


    
    time.sleep_ms(20)





