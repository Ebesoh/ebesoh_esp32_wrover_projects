#Board: ESP32-WROVER
#GPIOs used: GPIO 16, 17, 18
#(Safe, commonly available. Adjust if needed.)
#Each test:
#  Sets GPIO HIGH
#  Reads it back
#  Decides PASS / FAIL

#  Sets GPIO LOW
#  Reads it back
#  Decides PASS / FAIL

# Hardware wiring
#   Output GPIO         Input GPIO
#     GPIO 14             GPIO 19
#     GPIO 12             GPIO 18
from machine import Pin
import time


from machine import Pin
import time

def loopback_test(out_pin_num, in_pin_num):
    out_pin = Pin(out_pin_num, Pin.OUT)
    in_pin = Pin(in_pin_num, Pin.IN, Pin.PULL_DOWN)

    out_pin.value(1)
    time.sleep(0.05)
    if in_pin.value() != 1:
        return False

    out_pin.value(0)
    time.sleep(0.05)
    if in_pin.value() != 0:
        return False

    return True

