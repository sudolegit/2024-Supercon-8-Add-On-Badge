from machine import I2C, Pin
import time

while True:

    screen.fill(0)

    screen.text("Hello Hackaday!", 10, 0)

    screen.text("Button A: ", 25, 20)
    screen.text(str(buttonA.value()), 100, 20)
    screen.text("Button B: ", 25, 30)
    screen.text(str(buttonB.value()), 100, 30)
    screen.text("Button C: ", 25, 40)
    screen.text(str(buttonC.value()), 100, 40)

    screen.text("Wheel: ", 25, 50)
    screen.text(str(touchwheel_read(touchwheel_bus)), 80, 50)

    screen.show()

    tw = touchwheel_read(touchwheel_bus)
    print(tw)

    ## display on petal
    if tw > 0:
        petal = int(tw/32) + 1
    else: 
        petal = 999
    for i in range(1,9):
        if i == petal:
            i2c0.writeto_mem(0, i, bytes([0x7F]))
        else:
            i2c0.writeto_mem(0, i, bytes([0x00]))
    
    time.sleep_ms(100)





