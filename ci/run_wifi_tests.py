import serial
import time
import sys

PORT = "COM5"          # CHANGE to your ESP32 port
BAUD = 115200
TIMEOUT = 600          # WiFi tests take time

print("Connecting to ESP32 on", PORT)
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)

# Stop anything running
ser.write(b'\x03')
time.sleep(1)

# Run the WiFi test runner
ser.write(b'import test_wifi_runner\n')

start = time.time()
output = ""

while time.time() - start < TIMEOUT:
    if ser.in_waiting:
        line = ser.readline().decode(errors="ignore").strip()
        print(line)
        output += line + "\n"

        if "CI_RESULT:" in line:
            break

ser.close()

if "CI_RESULT: PASS" in output:
    print("FINAL RESULT: PASS")
    sys.exit(0)

print("FINAL RESULT: FAIL")
sys.exit(1)
