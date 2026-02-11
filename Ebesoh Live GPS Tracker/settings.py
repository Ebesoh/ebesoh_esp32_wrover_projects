"""
settings.py

This file contains all the configuration parameters that control how the
entire system behaves. If you want to tune or change something, it should
happen here instead of buried in other files.

What each setting means:

SERIAL_PORT:
    The COM port where your ESP32 appears on your PC (e.g. "COM5").

BAUD:
    The baud rate used by the ESP32 to stream NMEA data (must match).

dt:
    Time step for the Kalman filter (roughly your GPS update period).

HDOP_MIN / HDOP_MAX:
    Expected practical range of HDOP (signal quality). Used to scale
    raw GPS uncertainty.

RAW_SIGMA_MIN / RAW_SIGMA_MAX:
    Lower and upper bounds on raw GPS uncertainty in meters.
    These are centered around your datasheet accuracy (2.5 m).
"""
SERIAL_PORT = "COM5"
BAUD = 115200

dt = 0.2   # Kalman filter time step (s)

# HDOP range used to scale raw uncertainty
HDOP_MIN = 0.8
HDOP_MAX = 5.0

# Horizontal raw GPS uncertainty bounds (meters)
RAW_SIGMA_MIN = 2.0
RAW_SIGMA_MAX = 6.0

# Vertical (altitude) uncertainty scaling
# Altitude is typically worse than horizontal
ALT_NOISE_SCALE = 1.5


