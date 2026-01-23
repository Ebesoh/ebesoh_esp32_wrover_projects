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
    - Jitter does not exceed the configured threshold

Fail Criteria:
    - Sensor not detected
    - Read returns None or invalid value
    - Excessive temperature jitter (unstable readings)

CI Behavior:
    Prints CI_RESULT: PASS or FAIL and exits accordingly.
"""

from machine import Pin
import onewire, ds18x20
import time, sys

DATA_PIN = 4
SAMPLES = 10
MAX_JITTER = 1.5  # °C

def ds18b20_stability_test():
    reasons = []
    temps = []

    ow = onewire.OneWire(Pin(DATA_PIN))
    ds = ds18x20.DS18X20(ow)
    roms = ds.scan()

    if not roms:
        return "FAIL", ["No DS18B20 detected"]

    sensor = roms[0]

    for i in range(SAMPLES):
        ds.convert_temp()
        time.sleep(1)
        t = ds.read_temp(sensor)

        if t is None:
            return "FAIL", ["Temperature read returned None"]

        temps.append(t)
        print("Sample {}: {:.2f} °C".format(i + 1, t))

    jitter = max(temps) - min(temps)

    if jitter > MAX_JITTER:
        return "FAIL", ["Temperature jitter too high ({:.2f} °C)".format(jitter)]

    return "PASS", ["Temperature stable"], temps


if __name__ == "__main__":
    verdict, reasons, _ = ds18b20_stability_test()
    print("VERDICT:", verdict)
    for r in reasons:
        print("-", r)
    print("CI_RESULT:", verdict)
    sys.exit(0 if verdict == "PASS" else 1)
