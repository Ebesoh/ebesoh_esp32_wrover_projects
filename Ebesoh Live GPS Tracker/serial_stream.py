import serial

ser = serial.Serial("COM5", 115200, timeout=2)

print("Waiting for ESP32 stream...")

while True:
    data = ser.read(200)
    if data:
        print("RAW BYTES:", data)
        try:
            print("AS TEXT:", data.decode())
        except:
            pass

