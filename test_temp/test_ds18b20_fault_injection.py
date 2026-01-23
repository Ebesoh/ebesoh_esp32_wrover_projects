"""
DS18B20 Fault Injection Test (ESP32 / MicroPython)

Purpose:
    Verify system behavior when the DS18B20 sensor loses power
    during operation.

What this test verifies:
    - Sensor is detected at startup
    - Normal temperature conversion works
    - Power is removed programmatically
    - Sensor disappearance OR read failure is detected
    - Cached values are NOT treated as valid readings

Important:
    This test automatically detects parasitic power situations
    and fails explicitly if power removal is not observable.

CI Rules:
    - PASS  → Sensor fault detected correctly
    - FAIL  → Fault not detected OR parasitic power masking failure
"""

from machine import Pin
import onewire
import ds18x20
import time
import sys

# ---------------- CONFIG ----------------

DATA_PIN  = 4           # 1-Wire data
POWER_PIN = 27          # Controls sensor VDD (via MOSFET or GPIO)
TEMP_MIN  = -40.0
TEMP_MAX  = 125.0

POWER_OFF_DELAY = 2.0
CONVERT_DELAY   = 1.0

# ----------------------------------------

def ds18b20_fault_injection_test():
    reasons = []

    print("Starting DS18B20 Fault Injection Test")

    # Power ON sensor
    power = Pin(POWER_PIN, Pin.OUT)
    power.on()
    time.sleep(1)

    try:
        ow = onewire.OneWire(Pin(DATA_PIN))
        ds = ds18x20.DS18X20(ow)
    except Exception as e:
        return "FAIL", ["1-Wire init failed: {}".format(e)]

    # ---------- Step 1: Detect sensor ----------
    roms = ds.scan()
    if not roms:
        return "FAIL", ["No DS18B20 detected at startup"]

    sensor = roms[0]
    print("✓ Sensor detected")

    # ---------- Step 2: Normal read ----------
    try:
        ds.convert_temp()
        time.sleep(CONVERT_DELAY)
        temp_normal = ds.read_temp(sensor)
    except Exception as e:
        return "FAIL", ["Initial temperature read failed: {}".format(e)]

    if temp_normal is None or temp_normal < TEMP_MIN or temp_normal > TEMP_MAX:
        return "FAIL", ["Invalid initial temperature reading"]

    print("✓ Normal temperature read:", temp_normal)

    # ---------- Step 3: Inject power loss ----------
    print("Injecting sensor power loss")
    power.off()
    time.sleep(POWER_OFF_DELAY)

    # ---------- Step 4: Detect disappearance ----------
    try:
        roms_after = ds.scan()
        if roms_after:
            return (
                "FAIL",
                [
                    "Sensor still detected after power cut",
                    "Parasitic power likely present",
                    "Fault injection not observable"
                ]
            )
    except Exception:
        pass

    # ---------- Step 5: Attempt read ----------
    try:
        ds.convert_temp()
        time.sleep(CONVERT_DELAY)
        temp_after = ds.read_temp(sensor)

        if temp_after is None:
            return "PASS", ["Sensor failure detected (None read)"]

        if temp_after == -127.0:
            return "PASS", ["Sensor failure detected (-127)"]

        if temp_after == temp_normal:
            return (
                "FAIL",
                [
                    "Cached temperature returned after power cut",
                    "Invalid value treated as valid",
                    "Parasitic power or hardware limitation"
                ]
            )

        return (
            "FAIL",
            [
                "Unexpected temperature after power cut: {}".format(temp_after),
                "Fault not detected correctly"
            ]
        )

    except Exception:
        return "PASS", ["Exception raised safely after power loss"]

# ---------------- ENTRY ----------------

if __name__ == "__main__":
    verdict, reasons = ds18b20_fault_injection_test()

    print("=" * 60)
    print("DS18B20 FAULT INJECTION VERDICT:", verdict)
    for r in reasons:
        print("-", r)
    print("CI_RESULT:", verdict)
    print("=" * 60)

    sys.exit(0 if verdict == "PASS" else 1)


