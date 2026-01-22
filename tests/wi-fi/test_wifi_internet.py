# test_wifi_internet.py
import network
import socket
import time

def test_dns_resolution():
    """Test DNS resolution functionality"""
    print("\n" + "="*50)
    print("TEST 16: DNS Resolution")
    print("="*50)
    
    try:
        wlan = network.WLAN(network.STA_IF)
        
        if not wlan.isconnected():
            print("Not connected to WiFi")
            print("Skipping DNS test - connect to network first")
            return False
        
        print("Testing DNS resolution...")
        
        # Test domains
        test_domains = [
            "google.com",
            "micropython.org",
            "example.com",
            "github.com"
        ]
        
        successes = 0
        for domain in test_domains:
            try:
                print(f"\nResolving {domain}...")
                addr_info = socket.getaddrinfo(domain, 80)
                
                if addr_info:
                    ip_address = addr_info[0][4][0]
                    print(f"  ✓ Resolved to: {ip_address}")
                    successes += 1
                else:
                    print(f"  ✗ No resolution")
                    
            except Exception as e:
                print(f"  ✗ Failed: {e}")
        
        print(f"\nDNS Success rate: {successes}/{len(test_domains)}")
        
        if successes > 0:
            print("\n✅ TEST 16 PASSED: DNS resolution works")
            return True
        else:
            print("\n✗ All DNS resolutions failed")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 16 FAILED: {e}")
        return False

def test_http_connectivity():
    """Test HTTP connectivity to external servers"""
    print("\n" + "="*50)
    print("TEST 17: HTTP Connectivity")
    print("="*50)
    
    try:
        wlan = network.WLAN(network.STA_IF)
        
        if not wlan.isconnected():
            print("Not connected to WiFi")
            print("Skipping HTTP test - connect to network first")
            return False
        
        print("Testing HTTP connectivity...")
        
        # Test URLs (small responses)
        test_urls = [
            ("http://httpbin.org/ip", "IP echo service"),
            ("http://worldtimeapi.org/api/timezone/Etc/UTC", "Time API"),
            ("http://api.ipify.org?format=json", "IP address service"),
        ]
        
        import urequests
        
        successes = 0
        for url, description in test_urls:
            try:
                print(f"\nTesting {description}:")
                print(f"  URL: {url}")
                
                response = urequests.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"  ✓ HTTP 200 OK")
                    print(f"  Response length: {len(response.text)} chars")
                    successes += 1
                else:
                    print(f"  ✗ HTTP {response.status_code}")
                
                response.close()
                
            except Exception as e:
                print(f"  ✗ Failed: {e}")
        
        print(f"\nHTTP Success rate: {successes}/{len(test_urls)}")
        
        if successes > 0:
            print("\n✅ TEST 17 PASSED: HTTP connectivity works")
            return True
        else:
            print("\n✗ All HTTP tests failed")
            return False
            
    except ImportError:
        print("urequests module not installed")
        print("Install via: Tools > Manage packages > urequests")
        return False
    except Exception as e:
        print(f"\n❌ TEST 17 FAILED: {e}")
        return False

def test_socket_operations():
    """Test raw socket operations"""
    print("\n" + "="*50)
    print("TEST 18: Socket Operations")
    print("="*50)
    
    try:
        wlan = network.WLAN(network.STA_IF)
        
        if not wlan.isconnected():
            print("Not connected to WiFi")
            print("Skipping socket test - connect to network first")
            return False
        
        print("Testing socket operations...")
        
        # Test 1: Create socket
        print("\n1. Creating socket...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        print("  ✓ Socket created")
        
        # Test 2: Connect to a server
        print("\n2. Testing connection to google.com:80...")
        try:
            sock.connect(("google.com", 80))
            print("  ✓ Connected to google.com:80")
            
            # Test 3: Send HTTP request
            print("\n3. Sending HTTP request...")
            request = b"GET / HTTP/1.0\r\nHost: google.com\r\n\r\n"
            sock.send(request)
            print("  ✓ Request sent")
            
            # Test 4: Receive response
            print("\n4. Receiving response (first 100 bytes)...")
            response = sock.recv(100)
            if response:
                print("  ✓ Response received")
                print(f"  Preview: {response[:50]}...")
            else:
                print("  ✗ No response")
            
            # Test 5: Close socket
            print("\n5. Closing socket...")
            sock.close()
            print("  ✓ Socket closed")
            
            print("\n✅ TEST 18 PASSED: All socket operations work")
            return True
            
        except Exception as e:
            print(f"  ✗ Socket operation failed: {e}")
            sock.close()
            return False
            
    except Exception as e:
        print(f"\n❌ TEST 18 FAILED: {e}")
        return False