# test_runner_system.py
#
# Runs:
#  - DS18B20 temperature sensor self-test
#  - GPS GT-U7 self-test
#  - Wi-Fi functional self-test
#
# CI rules:
#   - Any FAIL => CI_RESULT: FAIL
#   - Partial PASS allowed only if explicitly configured
#   - All reasons printed clearly

import sys
import time

# -------------------------------------------------
# Import individual self-tests
# -------------------------------------------------

try:
    from test_ds18b20 import ds18b20_self_test
except Exception as e:
    print("ERROR: Cannot import DS18B20 test:", e)
    print("CI_RESULT: FAIL")
    sys.exit(1)

try:
    from test_gps_gtu7 import gps_self_test
except Exception as e:
    print("ERROR: Cannot import GPS test:", e)
    print("CI_RESULT: FAIL")
    sys.exit(1)

try:
    from test_wifi_self import wifi_self_test
except Exception as e:
    print("ERROR: Cannot import Wi-Fi test:", e)
    print("CI_RESULT: FAIL")
    sys.exit(1)


# -------------------------------------------------
# Runner
# -------------------------------------------------

def run_test(name, test_func):
    print("\n" + "=" * 60)
    print("RUNNING:", name)
    print("=" * 60)

    try:
        result = test_func()

        verdict = result[0]
        reasons = result[1]

        print("VERDICT:", verdict)
        for r in reasons:
            print("-", r)

        return verdict == "PASS"

    except Exception as e:
        print("VERDICT: FAIL")
        print("FAIL_REASON: Unhandled exception")
        print("EXCEPTION:", e)
        return False


def main():
    print("=" * 60)
    print("ESP32 SYSTEM SELF-TEST SUITE")
    print("=" * 60)

    results = []

    results.append(("DS18B20 Temperature Sensor", run_test(
        "DS18B20 Temperature Sensor", ds18b20_self_test)))

    results.append(("GPS GT-U7", run_test(
        "GPS GT-U7", gps_self_test)))

    results.append(("Wi-Fi Connectivity", run_test(
        "Wi-Fi Connectivity", wifi_self_test)))

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print("{:<30} {}".format(name, status))
        if ok:
            passed += 1

    total = len(results)
    print("\nTotal:", passed, "/", total)

    # -------------------------------------------------
    # CI Verdict
    # -------------------------------------------------
    if passed == total:
        print("\n🎉 ALL SYSTEM TESTS PASSED")
        print("CI_RESULT: PASS")
        sys.exit(0)

    else:
        print("\n❌ SYSTEM TEST FAILURE")
        print("CI_RESULT: FAIL")
        sys.exit(1)


# -------------------------------------------------
# Entry point
# -------------------------------------------------
if __name__ == "__main__":
    main()
