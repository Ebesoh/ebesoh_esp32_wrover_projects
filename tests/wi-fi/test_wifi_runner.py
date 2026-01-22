# test_wifi_runner.py
import time

def run_all_wifi_tests():
    """Run all WiFi tests sequentially"""
    print("="*60)
    print("ESP32-WROVER WiFi COMPLETE TEST SUITE")
    print("="*60)
    
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
        print(f"Error importing test modules: {e}")
        print("Make sure all test files are in the same directory")
        return
    
    # Test execution order
    test_functions = [
        # Basic tests (no network needed)
        ("WiFi Initialization", test_wifi_initialization),
        ("MAC Address", test_wifi_mac_address),
        ("Configuration", test_wifi_configuration),
        
        # Network interface tests
        ("Network Interfaces", test_network_interfaces),
        ("Interface Status", test_interface_status),
        ("AP Mode", test_ap_mode),
        
        # Connection tests (need network)
        ("Connection without Credentials", test_connection_without_credentials),
        ("Network Scanning", test_scan_networks),
        ("Connect/Disconnect Cycle", test_connect_disconnect),
        
        # IP configuration tests
        ("Static IP", test_static_ip_configuration),
        ("DHCP Renewal", test_dhcp_renewal),
        ("Multiple Reconnections", test_multiple_reconnections),
        
        # Signal and performance tests
        ("Signal Strength", test_signal_strength),
        ("Power Management", test_power_management),
        ("Connection Stability", test_connection_stability),
        
        # Internet connectivity tests (need internet)
        ("DNS Resolution", test_dns_resolution),
        ("HTTP Connectivity", test_http_connectivity),
        ("Socket Operations", test_socket_operations),
        
        # Advanced features tests
        ("Concurrent Mode", test_concurrent_mode),
        ("WiFi Events", test_wifi_events),
        ("Reconnect After Sleep", test_reconnect_after_sleep),
    ]
    
    results = []
    
    for test_name, test_func in test_functions:
        print(f"\n{'='*60}")
        print(f"RUNNING: {test_name}")
        print(f"{'='*60}")
        
        try:
            start_time = time.time()
            success = test_func()
            elapsed = time.time() - start_time
            
            results.append((test_name, success, elapsed))
            
            if success:
                print(f"\n✓ {test_name}: PASSED ({elapsed:.1f}s)")
            else:
                print(f"\n✗ {test_name}: FAILED ({elapsed:.1f}s)")
                
        except Exception as e:
            print(f"\n✗ {test_name}: ERROR - {e}")
            results.append((test_name, False, 0))
        
        # Small delay between tests
        time.sleep(2)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    for test_name, success, elapsed in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test_name:<30} {status:<10} {elapsed:.1f}s")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    print("="*60)
    
    if passed == len(results):
        print("🎉 ALL TESTS PASSED! WiFi is working perfectly.")
    elif passed >= len(results) * 0.7:
        print("⚠️  Most tests passed. WiFi is functional.")
    else:
        print("❌ Many tests failed. Check WiFi hardware/firmware.")

def run_quick_connectivity_test(ssid, password):
    """Run a quick connectivity test"""
    print("\n" + "="*50)
    print("QUICK WiFi CONNECTIVITY TEST")
    print("="*50)
    
    import network
    import socket
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        print(f"Connecting to: {ssid}")
        wlan.connect(ssid, password)
        
        # Wait for connection
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(1)
            timeout -= 1
        
        if wlan.isconnected():
            config = wlan.ifconfig()
            print(f"\n✓ Connected!")
            print(f"  IP Address: {config[0]}")
            print(f"  Gateway: {config[2]}")
            print(f"  DNS: {config[3]}")
            
            # Test DNS
            try:
                socket.getaddrinfo("google.com", 80)
                print("✓ DNS: Working")
                
                # Test internet
                import urequests
                try:
                    r = urequests.get("http://httpbin.org/ip", timeout=5)
                    print(f"✓ Internet: Working (IP: {r.text})")
                    r.close()
                    return True
                except:
                    print("✗ Internet: No connectivity")
                    return False
                    
            except:
                print("✗ DNS: Failed")
                return False
        else:
            print("\n✗ Failed to connect to WiFi")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False
    if passed == len(results):
        print("CI_RESULT: PASS")
    else:
        print("CI_RESULT: FAIL")


def run_specific_test_category(category):
    """Run tests from a specific category"""
    categories = {
        'basic': [0, 1, 2],        # Tests 1-3
        'network': [3, 4, 5],      # Tests 4-6
        'connection': [6, 7, 8],   # Tests 7-9
        'ip': [9, 10, 11],         # Tests 10-12
        'signal': [12, 13, 14],    # Tests 13-15
        'internet': [15, 16, 17],  # Tests 16-18
        'advanced': [18, 19, 20],  # Tests 19-21
    }
    
    print(f"Running {category} tests...")
    # Implementation would map to specific test functions

# Main execution
if __name__ == "__main__":
    print("ESP32-WROVER WiFi Test Suite")
    print("="*50)
    print("Options:")
    print("1. Run all tests (comprehensive)")
    print("2. Run quick connectivity test")
    print("3. Run basic tests only")
    print("4. Run internet tests only")
    print()
    
    # For Thonny, uncomment what you want to run:
    
    # Option 1: Complete test suite
    run_all_wifi_tests()
    
    # Option 2: Quick test (set your SSID/password)
    # run_quick_connectivity_test("YOUR_SSID", "YOUR_PASSWORD")
    
    # Option 3: Individual test
    # from test_wifi_basic import test_wifi_initialization
    # test_wifi_initialization()
    
    print("\nTo run tests, uncomment the desired function above")
    print("and run the script in Thonny.")
