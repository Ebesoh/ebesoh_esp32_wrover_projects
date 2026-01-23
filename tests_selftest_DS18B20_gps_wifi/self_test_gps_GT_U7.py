# The GPS self-test verifies correct operation of the GT-U7 GPS module and its UART interface.
# The test confirms that serial communication is active by detecting incoming NMEA data, then waits for a valid GPS fix.
# Once a fix is obtained, the test decodes latitude and longitude values and verifies that satellite information is available.
# The test passes only if UART communication, GPS fix acquisition, position data, and satellite information are all successfully obtained.
# Failure at any stage results in a FAIL verdict, indicating a communication, reception, or positioning issue with the GPS module.

def gps_self_test():
    from machine import UART, Pin
    import time

    # -------------------------
    # Configuration
    # -------------------------
    UART_ID = 2
    BAUDRATE = 9600
    TX_PIN = 26
    RX_PIN = 25

    UART_TIMEOUT_MS = 5000
    FIX_TIMEOUT_MS = 120000  # 120 seconds

    verdict = "PASS"
    reasons = []

    print("=" * 60)
    print("GT-U7 GPS SELF-TEST")
    print("=" * 60)

    # -------------------------
    # Helper
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
    # UART Init
    # -------------------------
    try:
        gps = UART(
            UART_ID,
            baudrate=BAUDRATE,
            tx=Pin(TX_PIN),
            rx=Pin(RX_PIN)
        )
    except Exception:
        print("UART initialization failed")
        print("CI_RESULT: FAIL")
        return "FAIL", ["UART initialization failed"]

    # -------------------------
    # Phase 1: UART activity
    # -------------------------
    rx_bytes = 0
    start = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start) < UART_TIMEOUT_MS:
        n = gps.any()
        if n:
            data = gps.read(n)
            rx_bytes += len(data)
        time.sleep(0.05)

    print("UART bytes received:", rx_bytes)

    if rx_bytes == 0:
        verdict = "FAIL"
        reasons.append("No UART data received from GPS")
        print("CI_RESULT: FAIL")
        return verdict, reasons

    print("✓ UART communication OK")

    # -------------------------
    # Phase 2: Fix + position
    # -------------------------
    print("Waiting for GPS fix...")

    fix_found = False
    latitude = None
    longitude = None
    sats_used = None
    sats_in_view = None

    start = time.ticks_ms()

    while time.ticks_diff(time.ticks_ms(), start) < FIX_TIMEOUT_MS:
        if gps.any():
            try:
                line = gps.readline().decode().strip()
            except:
                continue

            if line.startswith("$GPRMC"):
                p = line.split(",")
                if len(p) > 6 and p[2] == "A":
                    fix_found = True
                    latitude = nmea_to_decimal(p[3], p[4], is_lon=False)
                    longitude = nmea_to_decimal(p[5], p[6], is_lon=True)

            elif line.startswith("$GPGGA"):
                p = line.split(",")
                if len(p) > 7 and p[7]:
                    try:
                        sats_used = int(p[7])
                    except:
                        pass

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
                and sats_used is not None
                and sats_in_view is not None
            ):
                break

        time.sleep(0.1)

    # -------------------------
    # Verdict
    # -------------------------
    if not fix_found:
        verdict = "FAIL"
        reasons.append("No GPS fix acquired")

    if latitude is None or longitude is None:
        verdict = "FAIL"
        reasons.append("Invalid latitude/longitude")

    if sats_used is None:
        verdict = "FAIL"
        reasons.append("Satellites used not reported")

    if sats_in_view is None:
        verdict = "FAIL"
        reasons.append("Satellites in view not reported")

    # -------------------------
    # Report
    # -------------------------
    print("\n" + "=" * 60)
    print("GPS SELF-TEST VERDICT:", verdict)

    if verdict == "PASS":
        print("Latitude :", latitude)
        print("Longitude:", longitude)
        print("Satellites in view:", sats_in_view)
        print("Satellites used   :", sats_used)
        print("CI_RESULT: PASS")
        return "PASS", ["All GPS checks passed"]

    else:
        for r in reasons:
            print("-", r)
        print("CI_RESULT: FAIL")
        return "FAIL", reasons
