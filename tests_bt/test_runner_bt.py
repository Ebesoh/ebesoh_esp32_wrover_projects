# test_runner.py
#This test suite performs a comprehensive validation of the ESP32 Bluetooth (BLE) functionality running under MicroPython. It verifies that the Bluetooth stack initializes #correctly, operates reliably, and remains stable under real-world usage conditions.

#The tests cover core BLE features including initialization, configuration, advertising, scanning, GATT services, connections, performance, and memory usage. Both basic #functionality and advanced scenarios such as long-running advertising, MTU negotiation, and multi-service stress testing are included.

#The suite is designed for automated execution in CI environments (e.g. Jenkins using mpremote). Each test produces explicit pass/fail results, and the overall CI verdict is #determined strictly: any failed test results in a CI failure, while all passing tests produce a CI success.

#This ensures reliable Bluetooth operation during hardware bring-up, regression testing, and manufacturing or lab validation of ESP32-based systems

import time
import sys

def run_all_tests():
    """Run all Bluetooth tests sequentially with CI verdict"""
    print("=" * 60)
    print("ESP32-WROVER BLUETOOTH COMPLETE TEST SUITE")
    print("=" * 60)

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

    except ImportError as e:
        print("❌ ERROR: Failed to import Bluetooth test modules")
        print("EXCEPTION:", e)
        print("CI_RESULT=1")
        sys.exit(1)

    # -------------------------------------------------
    # Test execution order
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
    failed_tests = 0

    # -------------------------------------------------
    # Run tests
    # -------------------------------------------------
    for test_name, test_func in test_functions:
        print("\n" + "=" * 60)
        print("RUNNING:", test_name)
        print("=" * 60)

        try:
            start_time = time.time()
            success = bool(test_func())
            elapsed = time.time() - start_time

            results.append((test_name, success, elapsed))

            if success:
                print(f"\n✓ {test_name}: PASSED ({elapsed:.1f}s)")
            else:
                print(f"\n✗ {test_name}: FAILED ({elapsed:.1f}s)")
                failed_tests += 1

        except Exception as e:
            print(f"\n✗ {test_name}: EXCEPTION")
            print("EXCEPTION:", e)
            results.append((test_name, False, 0.0))
            failed_tests += 1

        time.sleep(1)

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    for test_name, success, elapsed in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test_name:<30} {status:<10} {elapsed:.1f}s")
        if success:
            passed += 1

    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)

    # -------------------------------------------------
    # CI VERDICT (AUTHORITATIVE)
    # -------------------------------------------------
    if failed_tests > 0:
        print("\n❌ BLUETOOTH TEST SUITE FAILED")
        print(f"Failed tests: {failed_tests}")
        print("CI_RESULT=1")
        sys.exit(1)

    print("\n✅ BLUETOOTH TEST SUITE PASSED")
    print("CI_RESULT=0")
    sys.exit(0)


# -------------------------------------------------
# Optional helpers (non-CI)
# -------------------------------------------------

def quick_smoke_test():
    """Run a quick smoke test (not CI-critical)"""
    print("Running Quick Bluetooth Smoke Test...")

    try:
        import ubluetooth as bt

        ble = bt.BLE()
        ble.active(True)
        print("✓ Bluetooth initialized")

        ble.gap_advertise(100, b'\x02\x01\x06\x08\x09ESP32-SMOKE')
        print("✓ Advertising started")
        time.sleep(2)
        ble.gap_advertise(None)
        print("✓ Advertising stopped")

        ble.active(False)
        print("\n✅ Smoke test passed!")
        return True

    except Exception as e:
        print("\n❌ Smoke test failed:", e)
        return False


# -------------------------------------------------
# Entry point
# -------------------------------------------------
if __name__ == "__main__":
    run_all_tests()
