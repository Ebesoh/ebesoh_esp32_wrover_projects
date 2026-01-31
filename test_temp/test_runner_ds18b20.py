"""
DS18B20 Comprehensive Test Runner (ESP32 / MicroPython)

Purpose:
    Execute all DS18B20 validation tests in a controlled sequence and
    produce a single CI verdict.

CI Rules:
    - Any FAIL => CI_RESULT: FAIL
    - All PASS => CI_RESULT: PASS
    - Exit code reflects CI_RESULT

Intended Use:
    - Jenkins CI via mpremote
    - Manufacturing test
    - Hardware validation
"""

import sys
import time

# -------------------------------------------------
# Import individual DS18B20 tests
# -------------------------------------------------

def fail_import(name, exc):
    print("ERROR: Cannot import", name)
    print("EXCEPTION:", exc)
    print("CI_RESULT: FAIL")
    sys.exit(1)

try:
    from test_ds18b20_accuracy_temp import ds18b20_accuracy_test
except Exception as e:
    fail_import("accuracy test", e)

try:
    from test_ds18b20_fault_injection import ds18b20_fault_injection_test
except Exception as e:
    fail_import("fault injection test", e)

try:
    from test_ds18b20_stability import ds18b20_stability_test
except Exception as e:
    fail_import("stability test", e)

# -------------------------------------------------
# Helper: run one test safely
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

# -------------------------------------------------
# Runner
# -------------------------------------------------

def main():
    print("=" * 60)
    print("ESP32 DS18B20 SENSOR TEST SUITE")
    print("=" * 60)

    results = []

    results.append((
        "Accuracy Validation",
        run_test("DS18B20 Accuracy Test", ds18b20_accuracy_test)
    ))

    results.append((
        "Fault Injection (Unplug Sensor)",
        run_test("DS18B20 Fault Injection Test", ds18b20_fault_injection_test)
    ))

    results.append((
        "Stability / Jitter",
        run_test("DS18B20 Stability Test", ds18b20_stability_test)
    ))

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------

    print("\n" + "=" * 60)
    print("DS18B20 TEST SUMMARY")
    print("=" * 60)

    passed = 0
    for name, ok in results:
        status = "PASS" if ok else "FAIL"
        print("{:<35} {}".format(name, status))
        if ok:
            passed += 1

    total = len(results)
    print("\nTotal:", passed, "/", total)

    # -------------------------------------------------
    # CI Verdict
    # -------------------------------------------------

    if passed == total:
        print("\nALL DS18B20 TESTS PASSED")
        print("CI_RESULT= Pass")
        sys.exit(0)

    print("\nDS18B20 TEST FAILURE")
    print("CI_RESULT= FAIL")
    sys.exit(1)

# -------------------------------------------------
# Entry point
# -------------------------------------------------

if __name__ == "__main__":
    main()

