"""
DS18B20 Fault Injection Test (ESP32 / MicroPython)

Purpose:
    Verify system behavior when the DS18B20 sensor is disconnected
    during operation.

Test Method:
    - Confirm sensor presence at startup
    - Prompt operator to unplug sensor
    - Attempt temperature conversion and read

Pass Criteria:
    - Failure is detected (None, -127, or exception)
    - System does not hang or crash

Fail Criteria:
    - Sensor unplug not detected
    - Invalid data treated as valid reading

Note:
    This is a semi-manual test (requires physical unplug).
"""

from machine import Pin
import onewire, ds18x20
import time, sys

DATA_PIN = 4

def ds18b20_fault_injection_test():
    ow = onewire.OneWire(Pin(DATA_PIN))
    ds = ds18x20.DS18X20(ow)
    roms = ds.scan()

    if not roms:
        return "FAIL", ["No sensor detected at start"]

    sensor = roms[0]

    print("Sensor detected. UNPLUG SENSOR NOW.")
    time.sleep(5)

    try:
        ds.convert_temp()
        time.sleep(1)
        temp = ds.read_temp(sensor)

        if temp is None or temp == -127:
            return "PASS", ["Failure detected correctly"]

        return "FAIL", ["Sensor unplug not detected"]

    except Exception:
        return "PASS", ["Exception handled safely"]


if __name__ == "__main__":
    verdict, reasons = ds18b20_fault_injection_test()
    print("VERDICT:", verdict)
    for r in reasons:
        print("-", r)
    print("CI_RESULT:", verdict)
    sys.exit(0 if verdict == "PASS" else 1)
