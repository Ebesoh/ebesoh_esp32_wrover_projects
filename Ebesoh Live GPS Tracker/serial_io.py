"""
serial_io.py

This module is responsible for opening and configuring the serial connection
between your PC and the ESP32.

It isolates all serial-related details so the rest of your system does not
need to deal with low-level port configuration.

What it does:
- Opens the selected COM port at the correct baud rate.
- Clears any old data in the input buffer.
- Returns a ready-to-use serial object to main.py.
"""

import serial
from settings import SERIAL_PORT, BAUD

def open_serial():
    ser = serial.Serial(
        port=SERIAL_PORT,
        baudrate=BAUD,
        timeout=0.5
    )
    ser.reset_input_buffer()
    return ser
