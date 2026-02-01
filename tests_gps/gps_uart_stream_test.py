# gps_uart_stream_test.py
#Goal: Confirm continuous GPS output, not just one line.
#Only checks that GPS is alive and streaming
from machine import UART, Pin
import time

UART_ID = 2
TX_PIN = 26
RX_PIN = 25
BAUDRATE = 9600


def test_uart_stream(duration=15, min_sentences=10):
    print("TEST: UART NMEA stream stability")

    uart = UART(
        UART_ID,
        baudrate=BAUDRATE,
        tx=Pin(TX_PIN),
        rx=Pin(RX_PIN),
        timeout=1000
    )

    count = 0
    start = time.time()

    while time.time() - start < duration:
        if uart.any():
            line = uart.readline()
            if not line:
                continue
            try:
                line = line.decode()
            except Exception:
                continue

            if line.startswith("$GP"):
                count += 1

        time.sleep(0.1)

    print("NMEA sentences received:", count)
    return count >= min_sentences

