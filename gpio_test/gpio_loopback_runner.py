import sys
import gpio_loopback_tests as tests


def run_all_tests():
    if not tests.loopback_test(14, 19):
        print("CI_RESULT: FAIL (GPIO 14 -> 19)")
        sys.exit(1)
        return 1

    if not tests.loopback_test(12, 18):
        print("CI_RESULT: FAIL (GPIO 12 -> 18)")
        sys.exit(1)
        return 2

    print("CI_RESULT: PASS")
    sys.exit(0)
    return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
