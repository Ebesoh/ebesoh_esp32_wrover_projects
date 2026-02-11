from machine import UART, Pin
import time

# === YOUR WIRING ===
GPS_TX = 26   # ESP32 pin connected to GPS RX
GPS_RX = 25   # ESP32 pin connected to GPS TX

print("Starting ESP32 GPS stream...")

gps = UART(2, baudrate=9600, tx=Pin(GPS_TX), rx=Pin(GPS_RX))

print("UART initialized. Streaming NMEA via print() ...")

buffer = b""

while True:
    if gps.any():
        chunk = gps.read(32)
        if chunk:
            buffer += chunk

            if b"\n" in buffer:
                lines = buffer.split(b"\n")
                buffer = lines[-1]

                for line in lines[:-1]:
                    s = line.strip()
                    if b"$GPRMC" in s or b"$GPGGA" in s:
                        try:
                            print(s.decode())
                        except:
                            pass
    time.sleep(0.01)

  