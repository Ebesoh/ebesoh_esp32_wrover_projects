"""
DS18B20 Accuracy Validation Test (ESP32 / MicroPython)

Purpose:
    Validate DS18B20 temperature accuracy against a known reference value.

Test Method:
    - Detect DS18B20 sensor on 1-Wire bus
    - Perform a single temperature conversion
    - Compare measured value against an external reference temperature
    - Calculate absolute error

Pass Criteria:
    - Absolute error <= MAX_ERROR

Fail Criteria:
    - Sensor not detected
    - Invalid temperature reading
    - Absolute error exceeds MAX_ERROR

Note:
    Reference temperature must be measured externally using
    a calibrated thermometer, climate chamber, or equivalent.
"""

from machine import Pin
import onewire
import ds18x20
import time
import sys

# Configuration
DATA_PIN = 4
REFERENCE_TEMP_C = 21.0   # °C (external reference)
MAX_ERROR_C = 2.5        # °C allowed deviation
CONVERSION_DELAY_S = 0.75


def ds18b20_accuracy_test():
    ow = onewire.OneWire(Pin(DATA_PIN))
    ds = ds18x20.DS18X20(ow)

    roms = ds.scan()
    if not roms:
        return "FAIL", ["No DS18B20 detected on 1-Wire bus"]

    sensor = roms[0]

    try:
        ds.convert_temp()
        time.sleep(CONVERSION_DELAY_S)
        temp_c = ds.read_temp(sensor)
    except Exception as e:
        return "FAIL", [f"Exception during temperature read: {e}"]

    if temp_c is None:
        return "FAIL", ["Invalid temperature reading (None)"]

    error_c = abs(temp_c - REFERENCE_TEMP_C)

    if error_c > MAX_ERROR_C:
        return (
            "FAIL",
            [
                f"Measured: {temp_c:.2f} °C",
                f"Reference: {REFERENCE_TEMP_C:.2f} °C",
                f"Error: {error_c:.2f} °C exceeds tolerance ({MAX_ERROR_C:.2f} °C)",
            ],
        )

    return (
        "PASS",
        [
            f"Measured: {temp_c:.2f} °C",
            f"Reference: {REFERENCE_TEMP_C:.2f} °C",
            f"Error: {error_c:.2f} °C within tolerance",
        ],
    )


if __name__ == "__main__":
    verdict, details = ds18b20_accuracy_test()

    print("VERDICT:", verdict)
    for line in details:
        print("-", line)

    # CI-friendly result flag
    print("CI_RESULT:", verdict)
    sys.exit(0 if verdict == "PASS" else 1)

