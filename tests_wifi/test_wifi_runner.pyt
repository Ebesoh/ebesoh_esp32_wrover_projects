# test_wifi_runner.py
import time
import sys


def run_all_wifi_tests():
    """Run selected WiFi tests sequentially"""
    print("=" * 60)
    print("ESP32-WROVER WiFi LIMITED TEST SUITE")
    print("=" * 60)

    # Import test modules
    try:
        from test_wifi_basic import (
            test_wifi_initialization,
            test_wifi_mac_address,
            test_wifi_configuration
        )

        from test_wifi_network import (
            test_network_interfaces,
            test_interface_status,
            test_ap_mode
        )

        from test_wifi_connection import (
            test_connection_without_credentials,
            test_scan_networks
        )

    except ImportError as e:
        print(f"ERROR: Import failed: {e}")
        print("CI_RESULT: FAIL")
        sys.exit(1)

    test_functions = [
        ("WiFi Initialization", test_wifi_initialization),
        ("MAC Address", test_wifi_mac_address),
        ("Configuration", test_wifi_configuration),

        ("Network Interfaces", test_network_interfaces),
        ("Interface Status", test_interface_status),
        ("AP Mode", test_ap_mode),

        ("Connection without Credentials", test_connection_without_credentials),
        ("Network Scanning", test_scan_networks),
    ]

    results = []

    for test_name, test_func in test_functions:
        print("\n" + "=" * 60)
        print(f"RUNNING: {test_name}")
        print("=" * 60)

        try:
            start = time.time()
            success = bool(test_func())
            elapsed = time.time() - start

            results.append((test_name, success, elapsed))

            if success:
                print(f"{test_name}: PASSED ({elapsed:.1f}s)")
            else:
                print(f"{test_name}: FAILED ({elapsed:.1f}s)")

        except Exception as e:
            print(f"{test_name}: ERROR - {e}")
            results.append((test_name, False, 0.0))

        time.sleep(2)

    # ===== SUMMARY =====
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    for name, success, elapsed in results:
        status = "PASS" if success else "FAIL"
        print(f"{name:<30} {status:<5} {elapsed:.1f}s")
        if success:
            passed += 1

    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)

    # ===== CI VERDICT =====
    if passed == total:
        print("ALL TESTS PASSED")
        print("CI_RESULT: PASS")
        sys.exit(0)

    print("TEST FAILURE — WiFi baseline checks failed")
    print("CI_RESULT: FAIL")
    sys.exit(1)


# ===== MAIN =====
if __name__ == "__main__":
    run_all_wifi_tests()

