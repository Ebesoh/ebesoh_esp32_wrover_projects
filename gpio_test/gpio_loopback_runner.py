import sys
import gpio_loopback_tests as tests


def run_all_tests():
    failures = []

    if not tests.loopback_test(14, 19):
        failures.append("GPIO 14 - 19")

    if not tests.loopback_test(12, 18):
        failures.append("GPIO 12 - 18")

    if failures:
        for f in failures:
            print(f"GPIO loopback failed: {f}")
        raise RuntimeError("GPIO loopback test failed")

    print("GPIO loopback tests passed")


if __name__ == "__main__":
    run_all_tests()
