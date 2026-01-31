"""
DS18B20 Stability Test (ESP32 / MicroPython)

Purpose:
    Verify that the DS18B20 temperature sensor provides stable readings
    over time under constant conditions.

Test Method:
    - Detect at least one DS18B20 on the 1-Wire bus
    - Take multiple temperature samples sequentially
    - Measure jitter as (max - min) across samples

Pass Criteria:
    - All reads succeed
    - Jitter <= MAX_JITTER

Fail Criteria:
    - Sensor not detected
    - Read returns None or out-of-range value
    - Excessive temperature jitter (unstable readings)

CI Behavior:
    Prints CI_RESULT: PASS or FAIL and exits accordingly.
"""

from machine import Pin
import onewire
import ds18x20
import time
import sys

# ---------------- CONFIG ----------------

DATA_PIN = 4

SAMPLES = 10
CONVERT_DELAY_S = 0.75

TEMP_MIN_C = -40.0
TEMP_MAX_C = 125.0
MAX_JITTER_C = 1.5

# ----------------------------------------


def ds18b20_stability_test():
    temps = []

    try:
        ow = onewire.OneWire(Pin(DATA_PIN))
        ds = ds18x20.DS18X20(ow)
    except Exception as e:
        return "FAIL", [f"1-Wire initialization failed: {e}"]

    roms = ds.scan()
    if not roms:
        return "FAIL", ["No DS18B20 detected on 1-Wire bus"]

    sensor = roms[0]
    print("✓ Sensor detected")

    for i in range(SAMPLES):
        try:
            ds.convert_temp()
            time.sleep(CONVERT_DELAY_S)
            temp_c = ds.read_temp(sensor)
        except Exception as e:
            return "FAIL", [f"Exception during read at sample {i + 1}: {e}"]

        if temp_c is None:
            return "FAIL", [f"Temperature read returned None at sample {i + 1}"]

        if temp_c < TEMP_MIN_C or temp_c > TEMP_MAX_C:
            return (
                "FAIL",
                [f"Out-of-range temperature at sample {i + 1}: {temp_c:.2f} °C"],
            )

        temps.append(temp_c)
        print(f"Sample {i + 1}/{SAMPLES}: {temp_c:.2f} °C")

    jitter_c = max(temps) - min(temps)

    if jitter_c > MAX_JITTER_C:
        return (
            "FAIL",
            [
                f"Temperature jitter too high: {jitter_c:.2f} °C",
                f"Allowed maximum: {MAX_JITTER_C:.2f} °C",
            ],
        )

    return (
        "PASS",
        [
            f"Temperature stable across {SAMPLES} samples",
            f"Jitter: {jitter_c:.2f} °C",
        ],
    )


# ---------------- ENTRY ----------------

if __name__ == "__main__":
    verdict, reasons = ds18b20_stability_test()

    print("=" * 60)
    print("DS18B20 STABILITY VERDICT:", verdict)
    for r in reasons:
        print("-", r)
    print("CI_RESULT:", verdict)
    print("=" * 60)

    sys.exit(0 if verdict == "PASS" else 1)

