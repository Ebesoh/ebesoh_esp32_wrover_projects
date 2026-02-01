import sys
import time
from machine import UART, Pin

from gps_uart_stream_test import test_uart_stream
from gps_sentence_diversity_test import test_sentence_diversity
from gps_fix_consistency_test import test_fix_consistency
from gps_coordinate_sanity_test import test_coordinate_sanity

UART_ID = 2
TX_PIN = 26
RX_PIN = 25
BAUDRATE = 9600


def collect_nmea(duration=20):
    uart = UART(
        UART_ID,
        baudrate=BAUDRATE,
        tx=Pin(TX_PIN),
        rx=Pin(RX_PIN),
        timeout=1000
    )

    lines = []
    start = time.time()

    while time.time() - start < duration:
        if uart.any():
            line = uart.readline()
            if not line:
                continue
            try:
                line = line.decode().strip()
            except Exception:
                continue

            if line.startswith("$GP"):
                lines.append(line)

        time.sleep(0.1)

    return lines


def run_all_tests():
    print("\n" + "=" * 60)
    print("ESP32-WROVER GPS GT-U7 STABLE TEST SUITE")
    print("=" * 60)

    results = []

    # UART-level sanity check
    results.append(("UART stream", test_uart_stream()))

    # Collect NMEA data once and reuse
    nmea_lines = collect_nmea()
    if len(nmea_lines) < 10:
        print("Insufficient NMEA data collected")
        print("CI_RESULT: FAIL")
        sys.exit(1)

    results.append(("Sentence diversity", test_sentence_diversity(nmea_lines)))
    results.append(("Fix consistency", test_fix_consistency(nmea_lines)))
    results.append(("Coordinate sanity", test_coordinate_sanity(nmea_lines)))

    passed = sum(1 for _, ok in results if ok)

    print("\nSUMMARY")
    for name, ok in results:
        print(f"{name:<25} {'PASS' if ok else 'FAIL'}")

    if passed == len(results):
        print("CI_RESULT: PASS")
        sys.exit(0)

    print("CI_RESULT: FAIL")
    sys.exit(1)


# Backward-compatible entry point
def main():
    run_all_tests()


if __name__ == "__main__":
    main()

