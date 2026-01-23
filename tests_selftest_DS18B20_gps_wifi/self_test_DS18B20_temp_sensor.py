#What this DS18B20 self-test verifies

#   This test automatically checks:

#   ✅ 1-Wire bus is alive

#   ✅ At least one DS18B20 is detected

#   ✅ Temperature conversion succeeds

#   ✅ Read value is valid (not −127 / 85 / None)

#   ✅ Temperature is within a sane range

#    Verdict: If any step fails, the verdict is FAIL with a reason.

from machine import Pin
import onewire
import ds18x20
import time

DATA_PIN = 4           # GPIO used for DS18B20
TEMP_MIN = -40.0       # sanity limits
TEMP_MAX = 125.0
CONVERT_TIMEOUT = 1.0  # seconds


def ds18b20_self_test():
    verdict = "PASS"
    reasons = []

    print("Starting DS18B20 self-test...")

    try:
        ow = onewire.OneWire(Pin(DATA_PIN))
        ds = ds18x20.DS18X20(ow)
    except Exception as e:
        return "FAIL", ["1-Wire init failed"]

    # -------- Step 1: Detect sensor --------
    roms = ds.scan()
    if not roms:
        return "FAIL", ["No DS18B20 detected"]

    print("Found {} DS18B20 device(s)".format(len(roms)))
    sensor = roms[0]

    # -------- Step 2: Temperature conversion --------
    try:
        ds.convert_temp()
    except Exception:
        return "FAIL", ["Temperature conversion start failed"]

    t0 = time.time()
    while time.time() - t0 < CONVERT_TIMEOUT:
        time.sleep(0.1)

    # -------- Step 3: Read temperature --------
    try:
        temp = ds.read_temp(sensor)
    except Exception:
        return "FAIL", ["Temperature read failed"]

    print("Raw temperature:", temp)

    # -------- Step 4: Validate reading --------
    if temp is None:
        verdict = "FAIL"
        reasons.append("Temperature is None")

    elif temp == -127.0:
        verdict = "FAIL"
        reasons.append("Sensor not responding (-127)")

    elif temp == 85.0:
        verdict = "FAIL"
        reasons.append("Power-up default value (85°C)")

    elif temp < TEMP_MIN or temp > TEMP_MAX:
        verdict = "FAIL"
        reasons.append("Temperature out of range")

    if verdict == "PASS":
        reasons.append("All checks passed")

    return verdict, reasons, temp


# -----------------------------
# RUN SELF TEST
# -----------------------------

result = ds18b20_self_test()

print("==============================")
print("DS18B20 SELF-TEST VERDICT:", result[0])

for r in result[1]:
    print("-", r)

if result[0] == "PASS":
    print("Measured temperature: {:.2f} °C".format(result[2]))

print("==============================")
