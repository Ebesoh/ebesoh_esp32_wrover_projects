# test_wifi_connection.py
import network
import time

def test_connection_without_credentials():
    """Test connection attempt without credentials"""
    print("\n" + "="*50)
    print("TEST 7: Connection without Credentials")
    print("="*50)
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        # Ensure we're disconnected
        if wlan.isconnected():
            wlan.disconnect()
            time.sleep(2)
        
        print("Testing connection without credentials...")
        print("This should fail as expected")
        
        # Try to connect without SSID/password
        try:
            wlan.connect('', '')
            print("Unexpected: connect() accepted empty credentials")
            return False
        except:
            print("Correctly rejected empty credentials")
        
        # Check status
        status = wlan.status()
        print(f"Connection status: {status}")
        
        if not wlan.isconnected():
            print(" Correctly not connected")
        
        print("\nTEST 7 PASSED: Empty credentials handled properly")
        return True
        
    except Exception as e:
        print(f"\n TEST 7 FAILED: {e}")
        return False

def test_scan_networks():
    """Test scanning for available WiFi networks"""
    print("\n" + "="*50)
    print("TEST 8: Network Scanning")
    print("="*50)
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        time.sleep(1)
        
        print("Scanning for WiFi networks...")
        print("This may take 5-10 seconds...")
        
        # Scan for networks
        networks = wlan.scan()
        
        if networks:
            print(f"\nFound {len(networks)} networks:")
            print("-" * 60)
            print(f"{'SSID':<25} {'Channel':<8} {'RSSI':<6} {'Security':<10}")
            print("-" * 60)
            
            # Security mode mapping
            authmodes = {
                0: "Open",
                1: "WEP",
                2: "WPA-PSK",
                3: "WPA2-PSK",
                4: "WPA/WPA2-PSK"
            }
            
            for net in networks:
                ssid = net[0].decode('utf-8') if net[0] else "Hidden"
                channel = net[2]
                rssi = net[3]
                auth = authmodes.get(net[4], f"Unknown({net[4]})")
                
                # Truncate long SSIDs
                if len(ssid) > 24:
                    ssid = ssid[:21] + "..."
                
                print(f"{ssid:<25} {channel:<8} {rssi:<6} {auth:<10}")
            
            # Count visible networks
            visible_ssids = [net[0].decode('utf-8') for net in networks if net[0]]
            print(f"\nVisible networks: {len(visible_ssids)}")
            print(f"Hidden networks: {len(networks) - len(visible_ssids)}")
            
            print("\n TEST 8 PASSED: Network scanning works")
            return True
        else:
            print(" No networks found")
            print("Make sure there are WiFi networks in range")
            return False
            
    except Exception as e:
        print(f"\n TEST 8 FAILED: {e}")
        return False

def test_connect_disconnect():
    """Test basic connect and disconnect cycle"""
    print("\n" + "="*50)
    print("TEST 9: Connect/Disconnect Cycle")
    print("="*50)
    
    # You need to set these for actual testing
    TEST_SSID = "Familj_Ebesoh_2.4"
    TEST_PASSWORD = "AmandaAlicia1991"
    
    if TEST_SSID == "YOUR_TEST_SSID":
        print("  Please set TEST_SSID and TEST_PASSWORD in the code")
        print("Skipping actual connection test")
        return False
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        # Ensure disconnected first
        if wlan.isconnected():
            print("Disconnecting from current network...")
            wlan.disconnect()
            time.sleep(2)
        
        print(f"Attempting to connect to: {TEST_SSID}")
        print("This may take 10-20 seconds...")
        
        # Connect
        wlan.connect(TEST_SSID, TEST_PASSWORD)
        
        # Wait for connection with timeout
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(1)
            timeout -= 1
        
        if wlan.isconnected():
            config = wlan.ifconfig()
            print(f"\n✓ Connected successfully!")
            print(f"  IP Address: {config[0]}")
            print(f"  Gateway: {config[2]}")
            
            # Test disconnect
            print("\nTesting disconnect...")
            wlan.disconnect()
            time.sleep(2)
            
            if not wlan.isconnected():
                print(" Disconnected successfully")
                
                # Verify IP config resets
                config = wlan.ifconfig()
                if config[0] == '0.0.0.0':
                    print(" IP config reset to zeros")
                else:
                    print(f" IP config not reset: {config}")
                
                print("\n TEST 9 PASSED: Connect/disconnect cycle works")
                return True
            else:
                print(" Failed to disconnect")
                return False
        else:
            print(f"\n Failed to connect (timeout)")
            print(f"  Check SSID/password and network availability")
            return False
            
    except Exception as e:
        print(f"\n TEST 9 FAILED: {e}")
        return False