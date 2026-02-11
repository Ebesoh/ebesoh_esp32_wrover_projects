"""
esp32_time_sync.py

Runs on ESP32 WROVER (MicroPython).

- Reads $GPRMC from GPS
- Extracts UTC time
- Sends it to PC over UART
- Receives time offset from PC
- Applies offset so ESP32 time matches GPS time
"""

from machine import UART, Pin
import time

# === YOUR WIRING ===
GPS_TX = 26
GPS_RX = 25

# UART to GPS
gps = UART(2, baudrate=9600, tx=Pin(GPS_TX), rx=Pin(GPS_RX))

# UART to PC (Thonny)
pc = UART(1, baudrate=115200)

time_offset = 0.0  # PC_time - GPS_time

def parse_gprmc_time(fields):
    """
    Extract UTC time from $GPRMC: hhmmss.sss
    Return seconds since midnight.
    """
    if len(fields) < 2 or not fields[1]:
        return None

    t = fields[1]

    try:
        hours = int(t[0:2])
        minutes = int(t[2:4])
        seconds = float(t[4:])
        return hours*3600 + minutes*60 + seconds
    except:
        return None

print("ESP32 time sync running...")

while True:
    line = gps.readline()
    if not line:
        continue

    try:
        line = line.decode().strip()
    except:
        continue

    if "$GPRMC" in line:
        fields = line.split(",")

        gps_seconds = parse_gprmc_time(fields)

        if gps_seconds is None:
            continue

        # Send raw GPS time to PC
        pc.write(f"GPS_TIME,{gps_seconds}\n")

    # Check if PC sent back a time offset
    if pc.any():
        msg = pc.readline().decode().strip()

        if msg.startswith("TIME_OFFSET"):
            try:
                time_offset = float(msg.split(",")[1])
                print("Updated time offset:", time_offset)
            except:
                pass

    # Compute synchronized time on ESP32
    esp32_time = time.time() + time_offset

    # Print synced time occasionally
    if int(time.time()) % 5 == 0:
        print("Synced ESP32 time:", esp32_time)

    time.sleep(0.1)
