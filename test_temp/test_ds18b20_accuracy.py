"""
DS18B20 Accuracy Validation Test (ESP32 / MicroPython)

Purpose:
    Validate DS18B20 temperature accuracy against a known reference value.

Test Method:
    - Perform a single temperature conversion
    - Compare measured value against a reference temperature
    - Calculate absolute error

Pass Criteria:
    - Absolute error within defined tolerance

Fail Criteria:
    - Sensor not detected
    - Invalid temperature reading
    - Error exceeds allowed tolerance

Note:
    Reference temperature must be measured externally
    (calibrated thermometer, climate chamber, etc.).
"""

from machine import Pin
import onewire, ds18x20
import time, sys

DATA_PIN = 4
REFERENCE_TEMP = 21.0  # °C
MAX_ERROR = 2.0        # °C

def ds18b20_accuracy_test():
    ow = onewire.OneWire(Pin(DATA_PIN))
    ds = ds18x20.DS18X20(ow)
    roms = ds.scan()

    if not roms:
        return "FAIL", ["No DS18B20 detected"]

    sensor = roms[0]

    ds.convert_temp()
    time.sleep(1)
    temp = ds.read_temp(sensor)

    if temp is None:
        return "FAIL", ["Invalid temperature read"]

    error = abs(temp - REFERENCE_TEMP)

    if error > MAX_ERROR:
        return "FAIL", ["Temperature error {:.2f} °C exceeds tolerance".format(error)]

    return "PASS", ["Accuracy within tolerance"]


if __name__ == "__main__":
    verdict, reasons = ds18b20_accuracy_test()
    print("VERDICT:", verdict)
    for r in reasons:
        print("-", r)
    print("CI_RESULT:", verdict)
    sys.exit(0 if verdict == "PASS" else 1)
