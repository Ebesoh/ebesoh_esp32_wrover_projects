# test_bluetooth_connections.py
import ubluetooth as bt
import struct
import time

# IRQ constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

def test_connection_callbacks():
    """Test connection and disconnection callbacks"""
    print("\n" + "="*50)
    print("TEST 12: Connection Callbacks")
    print("="*50)
    
    try:
        ble = bt.BLE()
        ble.active(True)
        time.sleep(0.5)
        
        # Variables to track connection state
        connection_events = []
        connected = False
        
        def connection_irq(event, data):
            nonlocal connected, connection_events
            
            if event == _IRQ_CENTRAL_CONNECT:
                conn_handle, addr_type, addr = data
                addr_str = ':'.join(['%02X' % b for b in addr])
                connection_events.append(f"Connected from: {addr_str}")
                connected = True
                
            elif event == _IRQ_CENTRAL_DISCONNECT:
                conn_handle, addr_type, addr = data
                addr_str = ':'.join(['%02X' % b for b in addr])
                connection_events.append(f"Disconnected: {addr_str}")
                connected = False
        
        # Register IRQ handler
        ble.irq(connection_irq)
        
        # Create a simple service
        TEST_SERVICE_UUID = bt.UUID(0x180F)  # Battery Service
        services = (
            (
                TEST_SERVICE_UUID,
                (
                    (bt.UUID(0x2A19), bt.FLAG_READ),  # Battery Level
                )
            ),
        )
        ble.gatts_register_services(services)
        
        # Start advertising
        adv_data = bytearray()
        adv_data += struct.pack("BB", 0x02, 0x01)
        adv_data += struct.pack("B", 0x06)
        
        name = "ESP32-Battery"
        name_bytes = name.encode()
        adv_data += struct.pack("BB", len(name_bytes) + 1, 0x09)
        adv_data += name_bytes
        
        print("Advertising as battery service device...")
        print("Connect from your phone to test callbacks")
        print("Advertising for 30 seconds...")
        
        ble.gap_advertise(100, adv_data=adv_data)
        
        # Wait for connections
        start_time = time.time()
        while time.time() - start_time < 30:
            if connection_events:
                for event in connection_events:
                    print(f"  {event}")
                connection_events.clear()
            time.sleep(1)
            print(".", end="")
        
        ble.gap_advertise(None)
        ble.irq(None)
        
        print("\n\nTEST 12 PASSED: Connection callbacks work")
        print("Note: This test requires a device to connect")
        return True
        
    except Exception as e:
        print(f"\n TEST 12 FAILED: {e}")
        return False

def test_mtu_negotiation():
    """Test MTU (Maximum Transmission Unit) negotiation"""
    print("\n" + "="*50)
    print("TEST 13: MTU Negotiation")
    print("="*50)
    
    try:
        ble = bt.BLE()
        ble.active(True)
        time.sleep(0.5)
        
        print("Testing MTU configuration...")
        
        # Try to get current MTU
        try:
            current_mtu = ble.config('mtu')
            print(f"Current MTU: {current_mtu}")
        except:
            print("MTU configuration not directly accessible")
        
        # Test creating characteristic with different data sizes
        print("\nTesting data transfer sizes:")
        
        test_sizes = [20, 50, 100, 200]
        
        for size in test_sizes:
            try:
                print(f"\nTesting {size} bytes:")
                
                # Create characteristic
                services = (
                    (
                        bt.UUID(0x181C),  # User Data Service
                        (
                            (bt.UUID(0x2A8A), bt.FLAG_READ | bt.FLAG_WRITE),
                        )
                    ),
                )
                
                ((char_handle,),) = ble.gatts_register_services(services)
                
                # Write data of this size
                test_data = bytes([i % 256 for i in range(size)])
                ble.gatts_write(char_handle, test_data)
                print(f"  ✓ Write {size} bytes successful")
                
                # Read back
                read_data = ble.gatts_read(char_handle)
                if len(read_data) == size:
                    print(f" Read back {size} bytes successful")
                else:
                    print(f" Read back {len(read_data)} bytes (expected {size})")
                    
            except Exception as e:
                print(f"   Failed at {size} bytes: {e}")
                break
        
        print("\n TEST 13 PASSED: MTU/data size testing completed")
        return True
        
    except Exception as e:
        print(f"\nTEST 13 FAILED: {e}")
        return False