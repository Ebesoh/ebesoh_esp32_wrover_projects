# test_wifi_signal.py
import network
import time

def test_signal_strength():
    """Test WiFi signal strength monitoring"""
    print("\n" + "="*50)
    print("TEST 13: Signal Strength Monitoring")
    print("="*50)
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        print("Testing signal strength...")
        print("Note: Must be connected to a network for RSSI")
        
        if not wlan.isconnected():
            print("Not connected. Will scan networks instead...")
            
            # Scan for networks to show RSSI
            networks = wlan.scan()
            
            if networks:
                print(f"\nSignal strengths of visible networks:")
                for net in networks[:5]:  # Show top 5
                    ssid = net[0].decode('utf-8') if net[0] else "Hidden"
                    rssi = net[3]
                    
                    # Truncate long SSIDs
                    if len(ssid) > 20:
                        ssid = ssid[:17] + "..."
                    
                    # Interpret RSSI
                    if rssi > -50:
                        quality = "Excellent"
                    elif rssi > -60:
                        quality = "Good"
                    elif rssi > -70:
                        quality = "Fair"
                    else:
                        quality = "Poor"
                    
                    print(f"  {ssid:<20} RSSI: {rssi:>4} dBm ({quality})")
            else:
                print("No networks found")
                return False
        else:
            # If connected, we can't easily get RSSI in MicroPython
            # Some firmware might support wlan.status('rssi')
            print("Connected to network")
            print("Note: RSSI for current connection not available in standard MicroPython")
        
        print("\n TEST 13 PASSED: Signal strength monitoring tested")
        return True
        
    except Exception as e:
        print(f"\n TEST 13 FAILED: {e}")
        return False

def test_power_management():
    """Test WiFi power management modes"""
    print("\n" + "="*50)
    print("TEST 14: Power Management")
    print("="*50)
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        print("Testing power management modes...")
        
        # Try to set power management mode
        # Note: This may not be supported on all ESP32 firmware versions
        try:
            # Try different power modes if supported
            power_modes = {
                'none': network.WIFI_PS_NONE,
                'min': network.WIFI_PS_MIN_MODEM,
                'max': network.WIFI_PS_MAX_MODEM,
            }
            
            for mode_name, mode_value in power_modes.items():
                try:
                    wlan.config(pm=mode_value)
                    print(f"  Set power mode to: {mode_name}")
                    time.sleep(1)
                except:
                    print(f"  Mode '{mode_name}' not supported")
            
            # Set back to default
            wlan.config(pm=network.WIFI_PS_NONE)
            print("\n Power management tested")
            
        except Exception as e:
            print(f" Power management not supported: {e}")
            print("This is normal for some MicroPython builds")
        
        print("\n TEST 14 PASSED: Power management tested")
        return True
        
    except Exception as e:
        print(f"\n TEST 14 FAILED: {e}")
        return False

def test_connection_stability():
    """Test connection stability over time"""
    print("\n" + "="*50)
    print("TEST 15: Connection Stability")
    print("="*50)
    
    TEST_SSID = "YOUR_TEST_SSID"  # Set this
    TEST_PASSWORD = "YOUR_TEST_PASSWORD"  # Set this
    TEST_DURATION = 30  # seconds
    
    if TEST_SSID == "YOUR_TEST_SSID":
        print("  Set TEST_SSID and TEST_PASSWORD to run this test")
        return False
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        
        # Connect first
        print(f"Connecting to {TEST_SSID}...")
        wlan.connect(TEST_SSID, TEST_PASSWORD)
        
        timeout = 20
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
        
        if not wlan.isconnected():
            print(" Failed to connect")
            return False
        
        config = wlan.ifconfig()
        print(f" Connected - IP: {config[0]}")
        
        # Monitor connection for specified duration
        print(f"\nMonitoring connection for {TEST_DURATION} seconds...")
        print("Press Ctrl+C in Thonny to stop early")
        
        start_time = time.time()
        disconnections = 0
        last_status = wlan.isconnected()
        
        while time.time() - start_time < TEST_DURATION:
            current_status = wlan.isconnected()
            
            if current_status != last_status:
                if current_status:
                    print(f"\n Reconnected at {time.time() - start_time:.1f}s")
                else:
                    print(f"\n Disconnected at {time.time() - start_time:.1f}s")
                    disconnections += 1
            
            last_status = current_status
            
            # Check IP config periodically
            if current_status:
                config = wlan.ifconfig()
                # Simple check - just see if we have a non-zero IP
                if config[0] == '0.0.0.0':
                    print(f"  Lost IP at {time.time() - start_time:.1f}s")
            
            print(".", end="")
            time.sleep(1)
        
        print(f"\n\nTest completed:")
        print(f"  Duration: {TEST_DURATION} seconds")
        print(f"  Disconnections: {disconnections}")
        
        if disconnections == 0:
            print(" Stable connection throughout test")
            print("\n TEST 15 PASSED: Connection is stable")
            return True
        else:
            print(f"  Connection unstable ({disconnections} disconnections)")
            return False
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        return False
    except Exception as e:
        print(f"\n TEST 15 FAILED: {e}")
        return False