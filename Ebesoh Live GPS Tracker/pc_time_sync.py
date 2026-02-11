"""
pc_time_sync.py

Runs on your PC in Thonny (normal Python).

- Listens for GPS UTC time from ESP32
- Computes offset between PC time and GPS time
- Sends offset back to ESP32
"""

import serial
import time

SERIAL_PORT = "COM5"   # change to your port
BAUD = 115200

ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)

def pc_seconds_since_midnight():
    now = time.gmtime()  # UTC time on PC
    return now.tm_hour*3600 + now.tm_min*60 + now.tm_sec

print("PC time sync running...")

while True:
    line = ser.readline().decode(errors="ignore").strip()

    if not line:
        continue

    if line.startswith("GPS_TIME"):
        try:
            gps_seconds = float(line.split(",")[1])
        except:
            continue

        pc_seconds = pc_seconds_since_midnight()

        # Compute offset: PC_time - GPS_time
        offset = pc_seconds - gps_seconds

        print(f"GPS: {gps_seconds:.1f} s | PC: {pc_seconds:.1f} s | Offset: {offset:.2f}")

        # Send offset back to ESP32
        ser.write(f"TIME_OFFSET,{offset}\n".encode())

    time.sleep(0.1)
