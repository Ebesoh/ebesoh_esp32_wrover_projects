from machine import UART, Pin
import time

gps = UART(2, baudrate=9600, tx=Pin(26), rx=Pin(25))
usb = UART(1, baudrate=115200)

print("Streaming...")

while True:
    data = gps.read()
    if data:
        usb.write(data)
        print(data)
    time.sleep(0.05)
