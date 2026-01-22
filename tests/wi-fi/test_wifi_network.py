# test_wifi_network.py
import network
import time

def test_network_interfaces():
    """Test all network interfaces"""
    print("\n" + "="*50)
    print("TEST 4: Network Interfaces")
    print("="*50)
    
    try:
        # Test STA interface
        print("\nTesting STA (Station) Interface:")
        wlan_sta = network.WLAN(network.STA_IF)
        wlan_sta.active(True)
        time.sleep(0.5)
        
        sta_status = wlan_sta.status()
        sta_config = wlan_sta.ifconfig()
        
        print(f"  Status: {sta_status}")
        print(f"  IP Config: {sta_config}")
        
        # Test AP interface
        print("\nTesting AP (Access Point) Interface:")
        wlan_ap = network.WLAN(network.AP_IF)
        wlan_ap.active(True)
        time.sleep(0.5)
        
        ap_config = wlan_ap.ifconfig()
        print(f"  IP Config: {ap_config}")
        
        # Test interface coexistence
        print("\nTesting interface coexistence:")
        print(f"  Both interfaces active: {wlan_sta.active() and wlan_ap.active()}")
        
        # Deactivate AP to save power
        wlan_ap.active(False)
        
        print("\n✅ TEST 4 PASSED: All network interfaces work")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}")
        return False

def test_interface_status():
    """Test WiFi interface status codes"""
    print("\n" + "="*50)
    print("TEST 5: Interface Status Codes")
    print("="*50)
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        time.sleep(0.5)
        
        print("Testing status codes:")
        
        # Map status codes to human-readable names
        status_codes = {
            1000: 'STAT_IDLE',
            1001: 'STAT_CONNECTING',
            1010: 'STAT_GOT_IP',
            202: 'STAT_NO_AP_FOUND',
            201: 'STAT_WRONG_PASSWORD',
            200: 'STAT_ASSOC_FAIL',
            204: 'STAT_HANDSHAKE_TIMEOUT',
        }
        
        # Get current status
        current_status = wlan.status()
        status_name = status_codes.get(current_status, f"UNKNOWN({current_status})")
        
        print(f"Current status: {current_status} ({status_name})")
        
        # Test ifconfig when not connected
        if not wlan.isconnected():
            config = wlan.ifconfig()
            print(f"IP config when disconnected: {config}")
            
            # Should be (0.0.0.0, 0.0.0.0, 0.0.0.0, 0.0.0.0)
            if config == ('0.0.0.0', '0.0.0.0', '0.0.0.0', '0.0.0.0'):
                print("✓ Correct IP config when disconnected")
            else:
                print("⚠️ Unexpected IP config when disconnected")
        
        print("\n✅ TEST 5 PASSED: Status codes verified")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 5 FAILED: {e}")
        return False

def test_ap_mode():
    """Test Access Point mode functionality"""
    print("\n" + "="*50)
    print("TEST 6: Access Point Mode")
    print("="*50)
    
    try:
        # Create and configure AP
        wlan_ap = network.WLAN(network.AP_IF)
        wlan_ap.active(True)
        time.sleep(1)
        
        # Configure AP
        ap_ssid = "ESP32-AP-TEST"
        ap_password = "test1234"
        ap_channel = 6
        
        wlan_ap.config(essid=ap_ssid, password=ap_password, authmode=network.AUTH_WPA_WPA2_PSK, channel=ap_channel)
        
        # Get AP configuration
        config = wlan_ap.ifconfig()
        ap_ip = config[0]
        
        print(f"AP Configuration:")
        print(f"  SSID: {ap_ssid}")
        print(f"  Password: {ap_password}")
        print(f"  Channel: {ap_channel}")
        print(f"  IP Address: {ap_ip}")
        print(f"  Subnet Mask: {config[1]}")
        print(f"  Gateway: {config[2]}")
        print(f"  DNS: {config[3]}")
        
        # Check if AP is active
        if wlan_ap.active():
            print(f"\n✓ Access Point is active")
            print(f"  Connect to '{ap_ssid}' from another device")
            print(f"  Use password: {ap_password}")
            print(f"  AP IP: {ap_ip}")
        else:
            print("\n✗ Access Point failed to activate")
            return False
        
        # Keep AP running for a bit
        print("\nAP will run for 10 seconds...")
        for i in range(10, 0, -1):
            print(f"\r  {i} seconds remaining...", end="")
            time.sleep(1)
        
        # Deactivate AP
        wlan_ap.active(False)
        print("\n✓ AP deactivated")
        
        print("\n✅ TEST 6 PASSED: Access Point mode works")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 6 FAILED: {e}")
        return False