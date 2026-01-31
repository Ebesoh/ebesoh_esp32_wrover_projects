# test_bluetooth_advertising.py
import ubluetooth as bt
import struct
import time

def test_simple_advertising():
    """Test basic advertising functionality"""
    print("\n" + "="*50)
    print("TEST 4: Simple Advertising")
    print("="*50)
    
    try:
        ble = bt.BLE()
        ble.active(True)
        time.sleep(0.5)
        
        # Build simple advertisement data
        adv_data = bytearray()
        
        # Add flags
        adv_data += struct.pack("BB", 0x02, 0x01)  # Length, Type (Flags)
        adv_data += struct.pack("B", 0x06)         # Flags (LE General Discoverable)
        
        # Add device name
        device_name = "ESP32-TEST"
        name_bytes = device_name.encode()
        adv_data += struct.pack("BB", len(name_bytes) + 1, 0x09)  # Type: Complete Local Name
        adv_data += name_bytes
        
        print("Starting advertisement...")
        print(f"Device will appear as: {device_name}")
        print("Use a Bluetooth scanner app to verify")
        
        # Start advertising with 100ms interval
        ble.gap_advertise(100, adv_data=adv_data)
        print("✓ Advertising started")
        print("  Advertising for 5 seconds...")
        
        # Advertise for 5 seconds
        start_time = time.time()
        while time.time() - start_time < 5:
            print(".", end="")
            time.sleep(1)
        
        # Stop advertising
        ble.gap_advertise(None)
        print("\n✓ Advertising stopped")
        
        print("\nTEST 4 PASSED: Advertising works correctly")
        return True
        
    except Exception as e:
        print(f"\nTEST 4 FAILED: {e}")
        return False

def test_advertising_parameters():
    """Test different advertising parameters"""
    print("\n" + "="*50)
    print("TEST 5: Advertising Parameters")
    print("="*50)
    
    try:
        ble = bt.BLE()
        ble.active(True)
        time.sleep(0.5)
        
        print("Testing different advertising intervals:")
        
        intervals = [
            (20, "20ms - Fast advertising"),
            (100, "100ms - Normal advertising"),
            (500, "500ms - Slow advertising"),
            (1000, "1000ms - Very slow advertising"),
        ]
        
        for interval_ms, description in intervals:
            print(f"\nTesting: {description}")
            
            # Simple advertisement
            adv_data = b'\x02\x01\x06\x08\x09ESP32-TEST'
            
            ble.gap_advertise(interval_ms, adv_data=adv_data)
            print(f"  Started advertising at {interval_ms}ms interval")
            
            time.sleep(2)  # Advertise for 2 seconds
            
            ble.gap_advertise(None)
            print(f"  Stopped advertising")
        
        print("\nTEST 5 PASSED: All advertising intervals work")
        return True
        
    except Exception as e:
        print(f"\nTEST 5 FAILED: {e}")
        return False

def test_advertising_without_scan_response():
    """Test advertising without scan response data"""
    print("\n" + "="*50)
    print("TEST 6: Advertising Without Scan Response")
    print("="*50)
    
    try:
        ble = bt.BLE()
        ble.active(True)
        time.sleep(0.5)
        
        print("Testing advertisement with minimal data...")
        
        # Minimal advertisement data (flags only)
        minimal_adv = b'\x02\x01\x06'  # Flags: LE General Discoverable
        
        ble.gap_advertise(100, adv_data=minimal_adv)
        print("✓ Started advertising with minimal data")
        print("  Device may appear as 'Unknown' in scanners")
        print("  Advertising for 3 seconds...")
        
        time.sleep(3)
        
        ble.gap_advertise(None)
        print("✓ Advertising stopped")
        
        print("\nTEST 6 PASSED: Minimal advertising works")
        return True
        
    except Exception as e:
        print(f"\n TEST 6 FAILED: {e}")
        return False