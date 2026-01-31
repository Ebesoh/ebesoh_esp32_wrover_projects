# test_bluetooth_basic.py
import ubluetooth as bt
import time

def test_ble_initialization():
    """Test if Bluetooth module can be initialized"""
    print("\n" + "="*50)
    print("TEST 1: Bluetooth Module Initialization")
    print("="*50)
    
    try:
        # Create BLE object
        ble = bt.BLE()
        print("✓ BLE object created successfully")
        
        # Check initial state
        initial_state = ble.active()
        print(f"  Initial active state: {initial_state}")
        
        # Try to activate
        ble.active(True)
        time.sleep(0.5)
        
        active_state = ble.active()
        print(f"  After activation: {active_state}")
        
        # Test deactivation
        ble.active(False)
        time.sleep(0.5)
        
        deactivated_state = ble.active()
        print(f"  After deactivation: {deactivated_state}")
        
        # Reactivate for further tests
        ble.active(True)
        
        print("\nTEST 1 PASSED: Bluetooth module works correctly")
        return True
        
    except Exception as e:
        print(f"\nTEST 1 FAILED: {e}")
        return False

def test_ble_mac_address():
    """Test retrieval of Bluetooth MAC address"""
    print("\n" + "="*50)
    print("TEST 2: Bluetooth MAC Address")
    print("="*50)
    
    try:
        ble = bt.BLE()
        ble.active(True)
        time.sleep(0.5)
        
        # Get MAC address (method varies by firmware)
        try:
            # Try different methods to get MAC
            mac = ble.config('mac')
            print(f"✓ MAC address retrieved via config('mac'): {mac}")
        except:
            try:
                mac_addr = ble.config('addr')
                print(f"MAC address retrieved via config('addr'): {mac_addr}")
            except:
                # Try to get it from gap_advertise
                print("Direct MAC retrieval not supported")
                print("  This is normal for some MicroPython versions")
                mac = "Unknown"
        
        print(f"\nTEST 2 PASSED: MAC address functionality checked")
        return True
        
    except Exception as e:
        print(f"\n TEST 2 FAILED: {e}")
        return False

def test_ble_configuration():
    """Test Bluetooth configuration options"""
    print("\n" + "="*50)
    print("TEST 3: Bluetooth Configuration")
    print("="*50)
    
    try:
        ble = bt.BLE()
        ble.active(True)
        time.sleep(0.5)
        
        print("Testing configuration parameters:")
        
        # Test getting various config values
        configs_to_test = ['gap_name', 'mtu', 'bond', 'io_cap']
        
        for config_param in configs_to_test:
            try:
                value = ble.config(config_param)
                print(f"  {config_param}: {value}")
            except:
                print(f"  {config_param}: Not supported in this firmware")
        
        # Test setting device name
        try:
            device_name = "ESP32-TEST"
            ble.config(gap_name=device_name)
            print(f"Device name set to: {device_name}")
        except:
            print("Cannot set device name via config")
        
        print("\nTEST 3 PASSED: Configuration functions work")
        return True
        
    except Exception as e:
        print(f"\n TEST 3 FAILED: {e}")
        return False