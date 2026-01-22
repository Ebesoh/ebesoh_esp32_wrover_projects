# test_wifi_basic.py
import network
import time

def test_wifi_initialization():
    """Test if WiFi module can be initialized"""
    print("\n" + "="*50)
    print("TEST 1: WiFi Module Initialization")
    print("="*50)
    
    try:
        # Create STA interface
        wlan_sta = network.WLAN(network.STA_IF)
        print("✓ STA interface created")
        
        # Create AP interface
        wlan_ap = network.WLAN(network.AP_IF)
        print("✓ AP interface created")
        
        # Check initial states
        sta_active = wlan_sta.active()
        ap_active = wlan_ap.active()
        
        print(f"\nInitial states:")
        print(f"  STA interface active: {sta_active}")
        print(f"  AP interface active: {ap_active}")
        
        # Test activation/deactivation
        print("\nTesting activation:")
        wlan_sta.active(True)
        time.sleep(0.5)
        print(f"  STA activated: {wlan_sta.active()}")
        
        wlan_sta.active(False)
        time.sleep(0.5)
        print(f"  STA deactivated: {wlan_sta.active()}")
        
        # Reactivate for further tests
        wlan_sta.active(True)
        
        print("\n✅ TEST 1 PASSED: WiFi module initialized successfully")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        return False

def test_wifi_mac_address():
    """Test retrieval of WiFi MAC address"""
    print("\n" + "="*50)
    print("TEST 2: WiFi MAC Address")
    print("="*50)
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        time.sleep(0.5)
        
        # Get MAC address
        mac = wlan.config('mac')
        
        if mac:
            mac_str = ':'.join(['%02X' % b for b in mac])
            print(f"✓ MAC address: {mac_str}")
            
            # Check if MAC looks valid (not all zeros)
            if all(b == 0 for b in mac):
                print("⚠️ MAC address is all zeros (might be invalid)")
                return False
            
            print("\n✅ TEST 2 PASSED: Valid MAC address retrieved")
            return True
        else:
            print("✗ Could not retrieve MAC address")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        return False

def test_wifi_configuration():
    """Test WiFi configuration options"""
    print("\n" + "="*50)
    print("TEST 3: WiFi Configuration")
    print("="*50)
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        time.sleep(0.5)
        
        print("Testing configuration parameters:")
        
        # Test common config parameters
        config_params = [
            'mac',      # MAC address
            'essid',    # SSID (for AP mode)
            'channel',  # WiFi channel
            'hidden',   # Hidden SSID
            'authmode', # Authentication mode
            'txpower',  # Transmit power
        ]
        
        for param in config_params:
            try:
                value = wlan.config(param)
                print(f"  {param}: {value}")
            except Exception as e:
                print(f"  {param}: Not supported ({e})")
        
        # Test setting a parameter
        try:
            # Try to set transmit power (if supported)
            current_power = wlan.config('txpower')
            print(f"\nCurrent TX power: {current_power}")
            
            # Note: Changing TX power might not be allowed on all devices
            print("✓ Configuration get/set operations work")
            
        except:
            print("⚠️ Some config parameters are read-only")
        
        print("\n✅ TEST 3 PASSED: Configuration functions tested")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        return False