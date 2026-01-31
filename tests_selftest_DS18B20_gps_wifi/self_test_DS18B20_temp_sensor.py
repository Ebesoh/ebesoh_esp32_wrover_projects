# What this DS18B20 self-test verifies
#
# This self-test validates the full sensor read path:
#
#   ✓ 1-Wire bus is responsive
#   ✓ At least one DS18B20 is detected on the bus
#   ✓ Temperature conversion completes successfully
#   ✓ Read value is valid (not None, -127 °C, or 85 °C)
#   ✓ Reported temperature is within a physically sane range
#
# Verdict:
#   Any failed check results in a FAIL verdict with an explicit reason.
from machine import Pin
import onewire
import ds18x20
import time

# ---------------- CONFIG ----------------

DATA_PIN = 4            # GPIO used for DS18B20
TEMP_MIN_C = -40.0      # Sanity limits
TEMP_MAX_C = 125.0
CONVERT_DELAY_S = 0.75  # DS18B20 max conversion time (12-bit)

# --------------------------------------


def ds18b20_self_test():
    print("Starting DS18B20 self-test")

    # ---------- Step 0: Init 1-Wire ----------
    try:
        ow = onewire.OneWire(Pin(DATA_PIN))
        ds = ds18x20.DS18X20(ow)
    except Exception as e:
        return "FAIL", [f"1-Wire initialization failed: {e}"], None

    # ---------- Step 1: Detect sensor ----------
    roms = ds.scan()
    if not roms:
        return "FAIL", ["No DS18B20 detected on 1-Wire bus"], None

    print(f"Found {len(roms)} DS18B20 device(s)")
    sensor = roms[0]

    # ---------- Step 2: Temperature conversion ----------
    try:
        ds.convert_temp()
        time.sleep(CONVERT_DELAY_S)
    except Exception as e:
        return "FAIL", [f"Temperature conversion failed: {e}"], None

    # ---------- Step 3: Read temperature ----------
    try:
        temp_c = ds.read_temp(sensor)
    except Exception as e:
        return "FAIL", [f"Temperature read failed: {e}"], None

    print("Raw temperature:", temp_c)

    # ---------- Step 4: Validate reading ----------
    reasons = []

    if temp_c is None:
        reasons.append("Temperature read returned None")

    elif temp_c == -127.0:
        reasons.append("Sensor not responding (-127 °C)")

    elif temp_c == 85.0:
        reasons.append("Power-up default value detected (85 °C)")

    elif temp_c < TEMP_MIN_C or temp_c > TEMP_MAX_C:
        reasons.append(
            f"Temperature out of sane range ({temp_c:.2f} °C)"
        )

    if reasons:
        return "FAIL", reasons, temp_c

    return "PASS", ["All self-test checks passed"], temp_c


# ---------------- ENTRY ----------------

if __name__ == "__main__":
    verdict, reasons, temp = ds18b20_self_test()

    print("=" * 60)
    print("DS18B20 SELF-TEST VERDICT:", verdict)
    for r in reasons:
        print("-", r)

    if verdict == "PASS":
        print(f"Measured temperature: {temp:.2f} °C")

    print("CI_RESULT:", verdict)
    print("=" * 60)

