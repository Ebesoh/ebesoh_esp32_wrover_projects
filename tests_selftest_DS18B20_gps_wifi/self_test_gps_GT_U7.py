from machine import UART, Pin
import time

gps = UART(
    2,
    baudrate=9600,
    tx=Pin(26),
    rx=Pin(25)
)

print("GT-U7 self-test running...")

# -------------------------
# Helpers
# -------------------------
def nmea_to_decimal(coord, direction, is_lon=False):
    try:
        deg_len = 3 if is_lon else 2
        degrees = float(coord[:deg_len])
        minutes = float(coord[deg_len:])
        value = degrees + minutes / 60.0
        if direction in ("S", "W"):
            value *= -1
        return value
    except:
        return None


# -------------------------
# Phase 1: UART check
# -------------------------
rx_bytes = 0
start = time.ticks_ms()

while time.ticks_diff(time.ticks_ms(), start) < 5000:
    n = gps.any()
    if n:
        data = gps.read(n)
        rx_bytes += len(data)
    time.sleep(0.05)

print("UART bytes received:", rx_bytes)

if rx_bytes == 0:
    print("SELF TEST FAIL: No UART data")
    raise SystemExit

print("UART OK")

# -------------------------
# Phase 2: Fix + sats + position
# -------------------------
print("Waiting for GPS fix, satellites, and position...")

fix_found = False
sats_in_view = None
sats_used = None
latitude = None
longitude = None

start = time.ticks_ms()
FIX_TIMEOUT_MS = 120000   # 120 seconds

while time.ticks_diff(time.ticks_ms(), start) < FIX_TIMEOUT_MS:
    if gps.any():
        try:
            line = gps.readline().decode().strip()
        except:
            continue

        # Fix + position (GPRMC)
        if line.startswith("$GPRMC"):
            p = line.split(",")

            if len(p) > 6 and p[2] == "A":
                fix_found = True
                latitude = nmea_to_decimal(p[3], p[4], is_lon=False)
                longitude = nmea_to_decimal(p[5], p[6], is_lon=True)

        # Satellites used (GPGGA)
        elif line.startswith("$GPGGA"):
            p = line.split(",")
            if len(p) > 7 and p[7]:
                try:
                    sats_used = int(p[7])
                except:
                    pass

        # Satellites in view (GPGSV)
        elif line.startswith("$GPGSV"):
            p = line.split(",")
            if len(p) > 3 and p[3]:
                try:
                    sats_in_view = int(p[3])
                except:
                    pass

        if (
            fix_found
            and latitude is not None
            and longitude is not None
            and sats_in_view is not None
            and sats_used is not None
        ):
            break

    time.sleep(0.1)

# -------------------------
# Report
# -------------------------
if not fix_found:
    print("SELF TEST FAIL: No GPS fix")

elif latitude is None or longitude is None:
    print("SELF TEST FAIL: Fix but no valid position")

else:
    print("SELF TEST PASS")
    print("Latitude  :", latitude)
    print("Longitude :", longitude)
    print("L1 satellites in view :", sats_in_view)
    print("Satellites used       :", sats_used)
