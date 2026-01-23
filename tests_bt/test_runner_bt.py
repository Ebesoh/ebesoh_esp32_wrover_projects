# test_runner.py
import time
import sys

def run_all_tests():
    """Run all Bluetooth tests sequentially"""
    print("="*60)
    print("ESP32-WROVER BLUETOOTH COMPLETE TEST SUITE")
    print("="*60)
    
    # Import test modules
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
        print(f"Error importing test modules: {e}")
        print("Make sure all test files are in the same directory")
        return
    
    # Test execution order
    test_functions = [
        # Basic tests
        ("Bluetooth Initialization", test_ble_initialization),
        ("MAC Address", test_ble_mac_address),
        ("Configuration", test_ble_configuration),
        
        # Advertising tests
        ("Simple Advertising", test_simple_advertising),
        ("Advertising Parameters", test_advertising_parameters),
        ("Minimal Advertising", test_advertising_without_scan_response),
        
        # Scanning tests
        ("Device Scanning", test_device_scanning),
        ("Scan Parameters", test_scan_parameters),
        
        # GATT tests
        ("GATT Service Setup", test_gatt_service_setup),
        ("Characteristic Properties", test_gatt_characteristic_properties),
        ("Advertising with Service", test_gatt_advertising_with_service),
        
        # Connection tests
        ("Connection Callbacks", test_connection_callbacks),
        ("MTU Negotiation", test_mtu_negotiation),
        
        # Performance tests
        ("Advertising Performance", test_advertising_performance),
        ("Memory Usage", test_memory_usage),
        ("Multiple Services Stress", test_stress_multiple_services),
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
        time.sleep(1)
    
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
        print("🎉 ALL TESTS PASSED! Bluetooth is working perfectly.")
    elif passed >= len(results) * 0.7:
        print("⚠️  Most tests passed. Bluetooth is functional.")
    else:
        print("❌ Many tests failed. Check Bluetooth hardware/firmware.")

def run_specific_tests(test_numbers):
    """Run specific tests by number"""
    # This function would allow running individual tests
    # Implementation would map test numbers to functions
    pass

def quick_smoke_test():
    """Run a quick smoke test"""
    print("Running Quick Bluetooth Smoke Test...")
    
    try:
        import ubluetooth as bt
        
        # Test 1: Initialize
        ble = bt.BLE()
        ble.active(True)
        print("✓ Bluetooth initialized")
        
        # Test 2: Simple advertise
        ble.gap_advertise(100, b'\x02\x01\x06\x08\x09ESP32-SMOKE')
        print("✓ Advertising started")
        time.sleep(2)
        ble.gap_advertise(None)
        print("✓ Advertising stopped")
        
        ble.active(False)
        print("\n✅ Smoke test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Smoke test failed: {e}")
        return False

# Main execution
if __name__ == "__main__":
    print("ESP32-WROVER Bluetooth Test Suite")
    print("1. Run all tests")
    print("2. Run quick smoke test")
    print("3. Exit")
    
    # For Thonny, you can uncomment what you want to run:
    
    # Option 1: Run complete test suite
    run_all_tests()
    
    # Option 2: Quick test only
    # quick_smoke_test()
    
    # Option 3: Run specific tests (example)
    print("\nTo run tests, uncomment the desired function above")
    print("and run the script in Thonny.")