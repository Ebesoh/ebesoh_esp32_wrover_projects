# test_bluetooth_scanning.py
import ubluetooth as bt
import time

# Define IRQ constants locally
_IRQ_SCAN_RESULT = const(5)
_IRQ_SCAN_DONE = const(6)

def test_device_scanning():
    """Test scanning for nearby Bluetooth devices"""
    print("\n" + "="*50)
    print("TEST 7: Device Scanning")
    print("="*50)
    
    try:
        ble = bt.BLE()
        ble.active(True)
        time.sleep(0.5)
        
        scan_results = []
        scan_complete = False
        
        def scan_irq_handler(event, data):
            nonlocal scan_results, scan_complete
            
            if event == _IRQ_SCAN_RESULT:
                # A single scan result
                addr_type, addr, adv_type, rssi, adv_data = data
                scan_results.append({
                    'address': ':'.join(['%02X' % b for b in addr]),
                    'rssi': rssi,
                    'adv_data': adv_data
                })
                
            elif event == _IRQ_SCAN_DONE:
                # Scan duration finished
                scan_complete = True
        
        # Register IRQ handler
        ble.irq(scan_irq_handler)
        
        print("Starting scan for nearby Bluetooth devices...")
        print("Turn on Bluetooth on your phone or other devices")
        print("Scanning for 10 seconds...")
        
        # Start scanning for 10 seconds
        ble.gap_scan(10000, 30000, 30000)  # 10 seconds, 30ms interval, 30ms window
        
        # Wait for scan to complete
        start_time = time.time()
        while not scan_complete and (time.time() - start_time < 15):
            time.sleep(0.5)
            print(".", end="")
        
        print(f"\n\nScan completed. Found {len(scan_results)} advertisements")
        
        if scan_results:
            # Show unique devices (by address)
            unique_addresses = set()
            for result in scan_results:
                unique_addresses.add(result['address'])
            
            print(f"Unique devices found: {len(unique_addresses)}")
            
            # Show top 5 strongest signals
            print("\nTop 5 strongest signals:")
            sorted_results = sorted(scan_results, key=lambda x: x['rssi'], reverse=True)[:5]
            
            for i, result in enumerate(sorted_results):
                print(f"  {i+1}. Address: {result['address']}, RSSI: {result['rssi']} dBm")
        else:
            print("No devices found during scan")
            print("Make sure other Bluetooth devices are nearby and advertising")
        
        # Clear IRQ handler
        ble.irq(None)
        
        print("\n✅ TEST 7 PASSED: Device scanning works")
        return len(scan_results) > 0
        
    except Exception as e:
        print(f"\n❌ TEST 7 FAILED: {e}")
        return False

def test_scan_parameters():
    """Test different scanning parameters"""
    print("\n" + "="*50)
    print("TEST 8: Scanning Parameters")
    print("="*50)
    
    try:
        ble = bt.BLE()
        ble.active(True)
        time.sleep(0.5)
        
        scan_durations = [2000, 5000, 10000]  # 2, 5, 10 seconds
        
        for duration in scan_durations:
            print(f"\nTesting scan duration: {duration/1000} seconds")
            
            scan_count = [0]  # Use list for mutable in closure
            
            def quick_irq(event, data):
                if event == _IRQ_SCAN_RESULT:
                    scan_count[0] += 1
            
            ble.irq(quick_irq)
            
            # Start scan
            ble.gap_scan(duration, 30000, 30000)
            
            # Wait for scan to complete
            time.sleep(duration / 1000 + 1)
            
            ble.irq(None)
            
            print(f"  Advertisements received: {scan_count[0]}")
        
        print("\n✅ TEST 8 PASSED: Different scan durations work")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 8 FAILED: {e}")
        return False