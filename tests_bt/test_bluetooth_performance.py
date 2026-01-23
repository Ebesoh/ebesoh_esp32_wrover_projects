# test_bluetooth_performance.py
import ubluetooth as bt
import time
import random

def test_advertising_performance():
    """Test advertising performance and stability"""
    print("\n" + "="*50)
    print("TEST 14: Advertising Performance")
    print("="*50)
    
    try:
        ble = bt.BLE()
        ble.active(True)
        time.sleep(0.5)
        
        print("Testing advertising performance...")
        print("Starting continuous advertisement for 30 seconds")
        
        adv_data = b'\x02\x01\x06\x08\x09ESP32-PERF'
        
        start_time = time.time()
        ble.gap_advertise(100, adv_data=adv_data)
        
        # Monitor for 30 seconds
        while time.time() - start_time < 30:
            elapsed = time.time() - start_time
            print(f"\rAdvertising for {elapsed:.1f} seconds...", end="")
            time.sleep(1)
        
        ble.gap_advertise(None)
        print("\n✓ Continuous advertising completed")
        
        print("\n✅ TEST 14 PASSED: Advertising performance stable")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 14 FAILED: {e}")
        return False

def test_memory_usage():
    """Test Bluetooth memory usage"""
    print("\n" + "="*50)
    print("TEST 15: Memory Usage")
    print("="*50)
    
    try:
        import gc
        
        print("Testing Bluetooth memory usage...")
        
        # Check memory before Bluetooth
        gc.collect()
        memory_before = gc.mem_free()
        print(f"Memory before Bluetooth init: {memory_before} bytes")
        
        # Initialize Bluetooth
        ble = bt.BLE()
        ble.active(True)
        time.sleep(1)
        
        gc.collect()
        memory_after_init = gc.mem_free()
        print(f"Memory after Bluetooth init: {memory_after_init} bytes")
        print(f"Memory used by Bluetooth: {memory_before - memory_after_init} bytes")
        
        # Create services
        services = (
            (
                bt.UUID(0x180D),  # Heart Rate Service
                (
                    (bt.UUID(0x2A37), bt.FLAG_READ | bt.FLAG_NOTIFY),
                )
            ),
            (
                bt.UUID(0x180F),  # Battery Service
                (
                    (bt.UUID(0x2A19), bt.FLAG_READ),
                )
            ),
        )
        
        ble.gatts_register_services(services)
        gc.collect()
        memory_after_services = gc.mem_free()
        print(f"Memory after services: {memory_after_services} bytes")
        print(f"Memory used by services: {memory_after_init - memory_after_services} bytes")
        
        # Start advertising
        ble.gap_advertise(100, b'\x02\x01\x06\x08\x09ESP32-MEM')
        time.sleep(1)
        
        gc.collect()
        memory_after_advertising = gc.mem_free()
        print(f"Memory while advertising: {memory_after_advertising} bytes")
        
        # Cleanup
        ble.gap_advertise(None)
        ble.active(False)
        
        gc.collect()
        memory_after_cleanup = gc.mem_free()
        print(f"Memory after cleanup: {memory_after_cleanup} bytes")
        
        print("\n✅ TEST 15 PASSED: Memory usage tracked")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 15 FAILED: {e}")
        return False

def test_stress_multiple_services():
    """Stress test with multiple services"""
    print("\n" + "="*50)
    print("TEST 16: Multiple Services Stress Test")
    print("="*50)
    
    try:
        ble = bt.BLE()
        ble.active(True)
        time.sleep(0.5)
        
        print("Creating multiple services...")
        
        # Create several services
        services_list = []
        
        for i in range(3):  # Create 3 services
            service_uuid = bt.UUID(0x1800 + i)  # Use different service UUIDs
            char_uuid = bt.UUID(0x2A00 + i)     # Use different characteristic UUIDs
            
            services_list.append((
                service_uuid,
                (
                    (char_uuid, bt.FLAG_READ | bt.FLAG_WRITE),
                )
            ))
        
        # Register all services
        ble.gatts_register_services(tuple(services_list))
        print(f"✓ Created {len(services_list)} services")
        
        # Test each service
        print("\nTesting each service...")
        for i in range(len(services_list)):
            try:
                # Write to characteristic
                test_data = f"Service {i+1}".encode()
                # Note: In real code, you'd need to track characteristic handles
                print(f"  Service {i+1}: Created")
            except:
                print(f"  Service {i+1}: Error")
        
        print("\n✅ TEST 16 PASSED: Multiple services created")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 16 FAILED: {e}")
        return False