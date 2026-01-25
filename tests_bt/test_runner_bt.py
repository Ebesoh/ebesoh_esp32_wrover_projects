# test_runner_bt.py
# Comprehensive ESP32 Bluetooth (BLE) CI Test Suite

import time
import sys

PASS = True
FAIL = False


def run_all_tests():
    print("\n" + "=" * 70)
    print("ESP32-WROVER BLUETOOTH CI TEST SUITE")
    print("=" * 70)

    # -------------------------------------------------
    # Import test modules (FAIL HARD if missing)
    # -------------------------------------------------
    try:
        from test_bluetooth_basic import (
            test_ble_initialization,
            test_ble_mac_address,
            test_ble_configuration
        )

        from test_bluetooth_advertising import (
            test_simple_advertising,
            test_advertising_parameters,
            test_advertising_without_scan_response
        )

        from test_bluetooth_scanning import (
            test_device_scanning,
            test_scan_parameters
        )

        from test_bluetooth_gatt import (
            test_gatt_service_setup,
            test_gatt_characteristic_properties,
            test_gatt_advertising_with_service
        )

        from test_bluetooth_connections import (
            test_connection_callbacks,
            test_mtu_negotiation
        )

        from test_bluetooth_performance import (
            test_advertising_performance,
            test_memory_usage,
            test_stress_multiple_services
        )

    except Exception as e:
        print("\n❌ FATAL: Bluetooth test module import failed")
        print("EXCEPTION:", e)
        print("CI_EXIT_CODE=1")
        sys.exit(1)

    # -------------------------------------------------
    # Test list (ordered, deterministic)
    # -------------------------------------------------
    test_functions = [
        ("Bluetooth Initialization", test_ble_initialization),
        ("MAC Address", test_ble_mac_address),
        ("Configuration", test_ble_configuration),

        ("Simple Advertising", test_simple_advertising),
        ("Advertising Parameters", test_advertising_parameters),
        ("Minimal Advertising", test_advertising_without_scan_response),

        ("Device Scanning", test_device_scanning),
        ("Scan Parameters", test_scan_parameters),

        ("GATT Service Setup", test_gatt_service_setup),
        ("Characteristic Properties", test_gatt_characteristic_properties),
        ("Advertising with Service", test_gatt_advertising_with_service),

        ("Connection Callbacks", test_connection_callbacks),
        ("MTU Negotiation", test_mtu_negotiation),

        ("Advertising Performance", test_advertising_performance),
        ("Memory Usage", test_memory_usage),
        ("Multiple Services Stress", test_stress_multiple_services),
    ]

    results = []
    failed_tests = []

    # -------------------------------------------------
    # Execute tests
    # -------------------------------------------------
    for test_name, test_func in test_functions:
        print("\n" + "-" * 60)
        print(f"RUNNING TEST: {test_name}")
        print("-" * 60)

        start = time.time()

        try:
            success = bool(test_func())
            duration = time.time() - start

            if success:
                print(f"✓ RESULT: PASS  | {test_name} ({duration:.2f}s)")
                results.append((test_name, PASS, duration))
            else:
                print(f"✗ RESULT: FAIL  | {test_name} ({duration:.2f}s)")
                results.append((test_name, FAIL, duration))
                failed_tests.append(test_name)

        except Exception as e:
            print(f"✗ RESULT: EXCEPTION | {test_name}")
            print("EXCEPTION:", e)
            results.append((test_name, FAIL, 0.0))
            failed_tests.append(test_name)

        time.sleep(1)

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------
    print("\n" + "=" * 70)
    print("BLUETOOTH TEST SUMMARY")
    print("=" * 70)

    passed_count = 0
    for name, success, elapsed in results:
        status = "PASS" if success else "FAIL"
        symbol = "✓" if success else "✗"
        print(f"{symbol} {name:<35} {status:<5} {elapsed:.2f}s")
        if success:
            passed_count += 1

    total = len(results)
    print("\n" + "-" * 70)
    print(f"TOTAL RESULT: {passed_count}/{total} TESTS PASSED")
    print("-" * 70)

    # -------------------------------------------------
    # CI VERDICT (AUTHORITATIVE, SINGLE SOURCE OF TRUTH)
    # -------------------------------------------------
    if failed_tests:
        print("\n❌ CI VERDICT: BLUETOOTH TEST SUITE FAILED")
        print("FAILED TESTS:")
        for name in failed_tests:
            print(f" - {name}")
        print("CI_RESULT=1")
        sys.exit(1)

    print("\n✅ CI VERDICT: BLUETOOTH TEST SUITE PASSED")
    print("CI_RESULT=0")
    sys.exit(0)


# -------------------------------------------------
# Entry point
# -------------------------------------------------
if __name__ == "__main__":
    run_all_tests()

