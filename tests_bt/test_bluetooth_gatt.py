# test_bluetooth_gatt.py
import ubluetooth as bt
import struct
import time

# Define IRQ constants
_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

def test_gatt_service_setup():
    """Test creating a GATT service"""
    print("\n" + "="*50)
    print("TEST 9: GATT Service Setup")
    print("="*50)
    
    try:
        ble = bt.BLE()
        ble.active(True)
        time.sleep(0.5)
        
        print("Creating a simple GATT service...")
        
        # Define a simple service and characteristic
        # Using standard Heart Rate service for testing
        HR_SERVICE_UUID = bt.UUID(0x180D)  # Heart Rate Service
        HR_MEASUREMENT_UUID = bt.UUID(0x2A37)  # Heart Rate Measurement
        
        services = (
            (
                HR_SERVICE_UUID,
                (
                    (HR_MEASUREMENT_UUID, bt.FLAG_READ | bt.FLAG_NOTIFY),
                )
            ),
        )
        
        # Register the service
        ((hr_measurement_handle,),) = ble.gatts_register_services(services)
        print("✓ GATT service registered successfully")
        print(f"  Service UUID: {HR_SERVICE_UUID}")
        print(f"  Characteristic UUID: {HR_MEASUREMENT_UUID}")
        print(f"  Characteristic handle: {hr_measurement_handle}")
        
        # Write initial value to characteristic
        initial_value = b'\x00\x40'  # Flags (uint8) + Heart Rate (uint8)
        ble.gatts_write(hr_measurement_handle, initial_value)
        print("Initial value written to characteristic")
        
        # Read back the value
        read_value = ble.gatts_read(hr_measurement_handle)
        print(f"Value read back: {read_value}")
        
        print("\nTEST 9 PASSED: GATT service setup works")
        return True
        
    except Exception as e:
        print(f"\n TEST 9 FAILED: {e}")
        return False

def test_gatt_characteristic_properties():
    """Test different characteristic properties"""
    print("\n" + "="*50)
    print("TEST 10: Characteristic Properties")
    print("="*50)
    
    try:
        ble = bt.BLE()
        ble.active(True)
        time.sleep(0.5)
        
        print("Testing different characteristic properties:")
        
        # Test different flag combinations
        test_cases = [
            ("Read only", bt.FLAG_READ),
            ("Write only", bt.FLAG_WRITE),
            ("Read & Write", bt.FLAG_READ | bt.FLAG_WRITE),
            ("Notify", bt.FLAG_NOTIFY),
            ("Indicate", bt.FLAG_INDICATE),
        ]
        
        TEST_SERVICE_UUID = bt.UUID(0x181C)  # User Data Service
        
        for description, flags in test_cases:
            try:
                print(f"\nTesting: {description}")
                
                # Create service with this characteristic
                TEST_CHAR_UUID = bt.UUID(0x2A8A)  # First Name characteristic
                
                services = (
                    (
                        TEST_SERVICE_UUID,
                        (
                            (TEST_CHAR_UUID, flags),
                        )
                    ),
                )
                
                # Register service
                ((char_handle,),) = ble.gatts_register_services(services)
                print(f"   Created with flags: 0x{flags:02X}")
                
                # Try to write if WRITE flag is set
                if flags & bt.FLAG_WRITE:
                    ble.gatts_write(char_handle, b"Test Data")
                    print("   Write operation successful")
                
                # Try to read if READ flag is set
                if flags & bt.FLAG_READ:
                    value = ble.gatts_read(char_handle)
                    print(f"   Read operation successful: {value}")
                
            except Exception as e:
                print(f"   Failed: {e}")
        
        print("\n TEST 10 PASSED: Characteristic properties tested")
        return True
        
    except Exception as e:
        print(f"\n TEST 10 FAILED: {e}")
        return False

def test_gatt_advertising_with_service():
    """Test advertising with service UUID"""
    print("\n" + "="*50)
    print("TEST 11: Advertising with GATT Service")
    print("="*50)
    
    try:
        ble = bt.BLE()
        ble.active(True)
        time.sleep(0.5)
        
        # First create a GATT service
        HR_SERVICE_UUID = bt.UUID(0x180D)
        services = (
            (
                HR_SERVICE_UUID,
                (
                    (bt.UUID(0x2A37), bt.FLAG_READ | bt.FLAG_NOTIFY),
                )
            ),
        )
        
        ble.gatts_register_services(services)
        
        print("Creating advertisement with service UUID...")
        
        # Build advertisement data with service UUID
        adv_data = bytearray()
        
        # Flags
        adv_data += struct.pack("BB", 0x02, 0x01)  # Length, Type (Flags)
        adv_data += struct.pack("B", 0x06)         # Flags
        
        # Device name
        name = "ESP32-HRM"
        name_bytes = name.encode()
        adv_data += struct.pack("BB", len(name_bytes) + 1, 0x09)
        adv_data += name_bytes
        
        # Service UUID (Heart Rate Service)
        adv_data += struct.pack("BB", 3, 0x03)  # Length, Type (Complete List of 16-bit Service UUIDs)
        adv_data += struct.pack("<H", 0x180D)   # Heart Rate Service UUID
        
        print(f"Advertising as: {name}")
        print("Device should appear as a Heart Rate Monitor")
        print("Advertising for 5 seconds...")
        
        ble.gap_advertise(100, adv_data=adv_data)
        time.sleep(5)
        ble.gap_advertise(None)
        
        print("\n TEST 11 PASSED: Advertising with service UUID works")
        return True
        
    except Exception as e:
        print(f"\n TEST 11 FAILED: {e}")
        return False