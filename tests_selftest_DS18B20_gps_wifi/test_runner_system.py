# test_runner_system.py
#
# System-level hardware self-test runner.
#
# Executes the following checks:
#   - DS18B20 temperature sensor self-test
#   - Wi-Fi end-to-end connectivity self-test
#
# CI behavior:
#   - Any individual test returning FAIL results in CI_RESULT: FAIL
#   - Partial PASS is not permitted unless explicitly enabled
#   - All failure reasons are printed verbosely for diagnosis
#
# If this runner reports PASS, the system hardware and connectivity
# are considered operational at a functional level.

import sys
import time

# -------------------------------------------------
# Import individual self-tests
# -------------------------------------------------

def import_test(name, module, symbol):
    try:
        mod = __import__(module, None, None, [symbol])
        return getattr(mod, symbol)
    except Exception as e:
        print("=" * 60)
        print(f"ERROR: Cannot import {name} test")
        print("EXCEPTION:", e)
        print("CI_RESULT: FAIL")
        sys.exit(1)


ds18b20_self_test = import_test(
    "DS18B20 Temperature Sensor",
    "self_test_DS18B20_temp_sensor",
    "ds18b20_self_test",
)

wifi_self_test = import_test(
    "Wi-Fi Connectivity",
    "self_test_wifi",
    "wifi_self_test",
)

# -------------------------------------------------
# Test Runner
# -------------------------------------------------

def run_test(name, test_func):
    print("\n" + "=" * 60)
    print("RUNNING TEST:", name)
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
        print("FAIL_REASON: Unhandled exception during test execution")
        print("EXCEPTION:", e)
        return False


def main():
    print("=" * 60)
    print("ESP32 SYSTEM SELF-TEST SUITE")
    print("=" * 60)

    tests = [
        ("DS18B20 Temperature Sensor", ds18b20_self_test),
        ("Wi-Fi Connectivity", wifi_self_test),
    ]

    results = []

    for name, func in tests:
        ok = run_test(name, func)
        results.append((name, ok))
        time.sleep(0.5)

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"{name:<30} {status}")
        if ok:
            passed += 1

    total = len(results)
    print(f"\nTotal: {passed} / {total}")

    # -------------------------------------------------
    # CI Verdict
    # -------------------------------------------------

    if passed == total:
        print("\nALL SYSTEM TESTS PASSED")
        print("CI_RESULT: PASS")
        sys.exit(0)

    print("\nSYSTEM TEST FAILURE")
    print("CI_RESULT: FAIL")
    sys.exit(1)


# -------------------------------------------------
# Entry point
# -------------------------------------------------

if __name__ == "__main__":
    main()
