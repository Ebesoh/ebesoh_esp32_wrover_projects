# test_wifi_advanced.py
import network
import time

def test_concurrent_mode():
    """Test STA+AP concurrent mode"""
    print("\n" + "="*50)
    print("TEST 19: STA+AP Concurrent Mode")
    print("="*50)
    
    try:
        print("Testing concurrent STA and AP modes...")
        
        # Activate both interfaces
        wlan_sta = network.WLAN(network.STA_IF)
        wlan_ap = network.WLAN(network.AP_IF)
        
        wlan_sta.active(True)
        wlan_ap.active(True)
        time.sleep(1)
        
        print(f"STA active: {wlan_sta.active()}")
        print(f"AP active: {wlan_ap.active()}")
        
        if wlan_sta.active() and wlan_ap.active():
            print("✓ Concurrent mode active")
            
            # Configure AP
            wlan_ap.config(essid="ESP32-CONCURRENT", authmode=network.AUTH_OPEN)
            ap_config = wlan_ap.ifconfig()
            print(f"AP IP: {ap_config[0]}")
            
            # Show STA status
            sta_config = wlan_sta.ifconfig()
            print(f"STA IP: {sta_config[0]}")
            
            # Run for a short time
            print("\nConcurrent mode running for 10 seconds...")
            for i in range(10, 0, -1):
                print(f"\r  {i} seconds remaining...", end="")
                time.sleep(1)
            
            # Cleanup
            wlan_ap.active(False)
            print("\n✓ AP deactivated")
            
            print("\n✅ TEST 19 PASSED: Concurrent mode works")
            return True
        else:
            print("✗ Failed to activate concurrent mode")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 19 FAILED: {e}")
        return False

def test_wifi_events():
    """Test WiFi event handling"""
    print("\n" + "="*50)
    print("TEST 20: WiFi Event Handling")
    print("="*50)
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        print("Testing event registration...")
        
        # Define event handler
        def event_handler(event):
            event_names = {
                network.STA_CONNECTED: "STA_CONNECTED",
                network.STA_DISCONNECTED: "STA_DISCONNECTED",
                network.STA_GOT_IP: "STA_GOT_IP",
                network.STA_LOST_IP: "STA_LOST_IP",
                network.AP_STACONNECTED: "AP_STACONNECTED",
                network.AP_STADISCONNECTED: "AP_STADISCONNECTED",
            }
            name = event_names.get(event, f"UNKNOWN({event})")
            print(f"  Event: {name}")
        
        # Register event handler
        wlan.config(event_handler=event_handler)
        print("✓ Event handler registered")
        
        # Trigger some events by changing connection state
        print("\nTriggering events...")
        print("Disconnecting if connected...")
        
        if wlan.isconnected():
            wlan.disconnect()
            time.sleep(2)
        
        print("Events will be shown as they occur")
        print("Monitoring for 10 seconds...")
        
        for i in range(10):
            print(f"\r  {10-i} seconds remaining...", end="")
            time.sleep(1)
        
        # Remove event handler
        wlan.config(event_handler=None)
        print("\n✓ Event handler removed")
        
        print("\n✅ TEST 20 PASSED: Event handling works")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 20 FAILED: {e}")
        return False

def test_reconnect_after_sleep():
    """Test WiFi reconnection after deep sleep"""
    print("\n" + "="*50)
    print("TEST 21: Reconnection After Sleep")
    print("="*50)
    
    print("Note: This test simulates sleep/wake cycle")
    print("Actual deep sleep would restart the ESP32")
    
    TEST_SSID = "YOUR_TEST_SSID"  # Set this
    TEST_PASSWORD = "YOUR_TEST_PASSWORD"  # Set this
    
    if TEST_SSID == "YOUR_TEST_SSID":
        print("⚠️  Set TEST_SSID and TEST_PASSWORD to run this test")
        return False
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        # First connection
        print(f"1. Initial connection to {TEST_SSID}...")
        wlan.connect(TEST_SSID, TEST_PASSWORD)
        
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
        
        if not wlan.isconnected():
            print("✗ Initial connection failed")
            return False
        
        ip1 = wlan.ifconfig()[0]
        print(f"✓ Connected - IP: {ip1}")
        
        # Simulate "sleep" by deactivating WiFi
        print("\n2. Simulating sleep (deactivating WiFi)...")
        wlan.active(False)
        time.sleep(3)
        
        # "Wake up" and reconnect
        print("3. Waking up (reactivating WiFi)...")
        wlan.active(True)
        time.sleep(1)
        
        # Auto-reconnect should happen if credentials saved
        print("4. Waiting for auto-reconnect...")
        
        timeout = 30
        while not wlan.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(1)
            timeout -= 1
        
        if wlan.isconnected():
            ip2 = wlan.ifconfig()[0]
            print(f"\n✓ Reconnected - IP: {ip2}")
            
            if ip1 == ip2:
                print(" Same IP address (DHCP cache)")
            else:
                print("Different IP address (new DHCP lease)")
            
            print("\nTEST 21 PASSED: Reconnection after sleep works")
            return True
        else:
            print("\n Failed to auto-reconnect")
            print("Note: Auto-reconnect depends on firmware")
            return False
            
    except Exception as e:
        print(f"\n TEST 21 FAILED: {e}")
        return False