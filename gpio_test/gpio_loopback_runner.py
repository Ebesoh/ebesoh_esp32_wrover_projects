import sys
import gpio_loopback_tests as tests


def run_all_tests():
    failures = []

    if not tests.loopback_test(14, 19):
        failures.append("FAIL (GPIO 14 -> 19)")
        

    if not tests.loopback_test(12, 18):
      failures.append("FAIL (GPIO 12 -> 18)")

    if failures:
        print("CI_RESULT: FAILED")
        print("FAULTS:")
        for f in failures:
            print(f"-{f}")
        return 1
    
    print("CI_RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(run_all_tests())
    #run_all_tests()
