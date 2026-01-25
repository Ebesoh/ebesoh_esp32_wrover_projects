# test_wifi_runner.py
import time
import sys


def run_all_wifi_tests():
    """Run all WiFi tests sequentially"""
    print("=" * 60)
    print("ESP32-WROVER WiFi COMPLETE TEST SUITE")
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
            test_scan_networks,
            test_connect_disconnect
        )

        from test_wifi_ipconfig import (
            test_static_ip_configuration,
            test_dhcp_renewal,
            test_multiple_reconnections
        )

        from test_wifi_signal import (
            test_signal_strength,
            test_power_management,
            test_connection_stability
        )

        from test_wifi_internet import (
            test_dns_resolution,
            test_http_connectivity,
            test_socket_operations
        )

        from test_wifi_advanced import (
            test_concurrent_mode,
            test_wifi_events,
            test_reconnect_after_sleep
        )

    except ImportError as e:
        print(f"ERROR: Import failed: {e}")
        print("CI_RESULT=1")
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
        ("Connect/Disconnect Cycle", test_connect_disconnect),

        ("Static IP", test_static_ip_configuration),
        ("DHCP Renewal", test_dhcp_renewal),
        ("Multiple Reconnections", test_multiple_reconnections),

        ("Signal Strength", test_signal_strength),
        ("Power Management", test_power_management),
        ("Connection Stability", test_connection_stability),

        ("DNS Resolution", test_dns_resolution),
        ("HTTP Connectivity", test_http_connectivity),
        ("Socket Operations", test_socket_operations),

        ("Concurrent Mode", test_concurrent_mode),
        ("WiFi Events", test_wifi_events),
        ("Reconnect After Sleep", test_reconnect_after_sleep),
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
                print(f"✓ {test_name}: PASSED ({elapsed:.1f}s)")
            else:
                print(f"✗ {test_name}: FAILED ({elapsed:.1f}s)")

        except Exception as e:
            print(f"✗ {test_name}: ERROR - {e}")
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
        print("🎉 ALL TESTS PASSED")
        print("CI_RESULT=0")
        sys.exit(0)

    elif passed >= int(total * 0.7):
        print("⚠️ PARTIAL PASS — WiFi functional but issues detected")
        print("CI_RESULT=1")
        sys.exit(1)

    else:
        print("❌ TEST FAILURE — WiFi not reliable")
        print("CI_RESULT=1")
        sys.exit(1)


def run_quick_connectivity_test(ssid, password):
    """Run a quick connectivity test"""
    import network
    import socket
    import urequests

    print("=" * 50)
    print("QUICK WiFi CONNECTIVITY TEST")
    print("=" * 50)

    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)

        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(1)
            timeout -= 1

        if not wlan.isconnected():
            print("\n✗ WiFi connection failed")
            return False

        print("\n✓ Connected")

        socket.getaddrinfo("google.com", 80)
        r = urequests.get("http://httpbin.org/ip", timeout=5)
        r.close()

        print("✓ Internet OK")
        return True

    except Exception as e:
        print(f"✗ Connectivity test failed: {e}")
        return False


# ===== MAIN =====
if __name__ == "__main__":
    run_all_wifi_tests()


