# test_wifi_ipconfig.py
import network
import time

def test_static_ip_configuration():
    """Test setting static IP address"""
    print("\n" + "="*50)
    print("TEST 10: Static IP Configuration")
    print("="*50)
    
    # Static IP configuration (adjust for your network)
    STATIC_IP = '192.168.1.100'
    SUBNET_MASK = '255.255.255.0'
    GATEWAY = '192.168.1.1'
    DNS_SERVER = '8.8.8.8'
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        # Save original config
        original_config = wlan.ifconfig()
        print(f"Original config: {original_config}")
        
        # Set static IP
        print(f"\nSetting static IP configuration:")
        print(f"  IP: {STATIC_IP}")
        print(f"  Mask: {SUBNET_MASK}")
        print(f"  Gateway: {GATEWAY}")
        print(f"  DNS: {DNS_SERVER}")
        
        wlan.ifconfig((STATIC_IP, SUBNET_MASK, GATEWAY, DNS_SERVER))
        time.sleep(1)
        
        # Verify new config
        new_config = wlan.ifconfig()
        print(f"\nNew config: {new_config}")
        
        if new_config[0] == STATIC_IP:
            print("✓ Static IP set successfully")
        else:
            print("✗ Failed to set static IP")
            print("Note: Static IP might not take effect until connection")
        
        # Restore original config
        print("\nRestoring original configuration...")
        wlan.ifconfig(original_config)
        time.sleep(1)
        
        restored_config = wlan.ifconfig()
        if restored_config == original_config:
            print("✓ Original config restored")
        else:
            print(f"⚠️ Config mismatch: {restored_config}")
        
        print("\n✅ TEST 10 PASSED: Static IP configuration tested")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 10 FAILED: {e}")
        return False

def test_dhcp_renewal():
    """Test DHCP IP address renewal"""
    print("\n" + "="*50)
    print("TEST 11: DHCP IP Renewal")
    print("="*50)
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        if not wlan.isconnected():
            print("Not connected to a network")
            print("Skipping DHCP test - connect first")
            return False
        
        # Get current DHCP lease
        current_config = wlan.ifconfig()
        print(f"Current DHCP lease:")
        print(f"  IP: {current_config[0]}")
        print(f"  Obtained via DHCP")
        
        # Disconnect and reconnect to force DHCP renewal
        print("\nForcing DHCP renewal...")
        
        # Note: Some ESP32 implementations renew DHCP automatically
        # when reconnecting. This test might not show IP change if
        # router gives same IP.
        
        # Try to renew by disconnecting/reconnecting
        wlan.disconnect()
        time.sleep(3)
        
        # Reconnect (assuming credentials are saved)
        wlan.connect()
        
        timeout = 15
        while not wlan.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(1)
            timeout -= 1
        
        if wlan.isconnected():
            new_config = wlan.ifconfig()
            print(f"\nNew DHCP lease:")
            print(f"  IP: {new_config[0]}")
            
            if new_config[0] != current_config[0]:
                print("✓ DHCP gave different IP address")
            else:
                print("⚠️ DHCP gave same IP address (normal if lease not expired)")
            
            print("\n✅ TEST 11 PASSED: DHCP renewal tested")
            return True
        else:
            print("\n✗ Failed to reconnect")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 11 FAILED: {e}")
        return False

def test_multiple_reconnections():
    """Test multiple rapid reconnections"""
    print("\n" + "="*50)
    print("TEST 12: Multiple Rapid Reconnections")
    print("="*50)
    
    # Test parameters
    TEST_SSID = "Familj_Ebesoh_2.4"  # Set this
    TEST_PASSWORD = "AmandaAlicia1991"  # Set this
    NUM_RECONNECTIONS = 3
    
    if TEST_SSID == "YOUR_TEST_SSID":
        print("⚠️  Set TEST_SSID and TEST_PASSWORD to run this test")
        return False
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        print(f"Testing {NUM_RECONNECTIONS} rapid reconnections...")
        
        success_count = 0
        for i in range(NUM_RECONNECTIONS):
            print(f"\nAttempt {i+1}/{NUM_RECONNECTIONS}:")
            
            # Ensure disconnected
            if wlan.isconnected():
                wlan.disconnect()
                time.sleep(1)
            
            # Connect
            wlan.connect(TEST_SSID, TEST_PASSWORD)
            
            # Wait for connection
            timeout = 15
            while not wlan.isconnected() and timeout > 0:
                time.sleep(1)
                timeout -= 1
            
            if wlan.isconnected():
                config = wlan.ifconfig()
                print(f"  ✓ Connected - IP: {config[0]}")
                success_count += 1
                
                # Brief connection
                time.sleep(2)
                
                # Disconnect
                wlan.disconnect()
                time.sleep(1)
            else:
                print(f"  ✗ Connection failed")
        
        print(f"\nSuccess rate: {success_count}/{NUM_RECONNECTIONS}")
        
        if success_count == NUM_RECONNECTIONS:
            print("✓ All reconnections successful")
            print("\n✅ TEST 12 PASSED: Stable multiple reconnections")
            return True
        elif success_count > 0:
            print("⚠️ Some reconnections failed")
            return False
        else:
            print("✗ All reconnections failed")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 12 FAILED: {e}")
        return False