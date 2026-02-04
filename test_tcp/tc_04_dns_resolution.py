# ==============================================================
# TEST CASE DESCRIPTION — TC-04
# ==============================================================
# Purpose:
#   Verify that the ESP32 can resolve a hostname via DNS.
#
# CI Alignment:
#   → Part of functional network validation (Jobs 9–15)
#
# Preconditions:
#   - Valid IP configuration (TC-03 passed).
#   - Internet access available.
#
# Test Steps:
#   1. Call socket.getaddrinfo() on a known hostname.
#   2. Capture returned IP address.
#
# Expected Result:
#   - Hostname resolves to a valid IP.
#
# ISO/IEC Reference:
#   - ISO/IEC 7498-1:1994, Clause 7.4 (Naming services)
# ==============================================================

import socket
from config import TEST_HOST, TEST_PORT

def run():
    try:
        # Ask DNS to resolve hostname
        return socket.getaddrinfo(TEST_HOST, TEST_PORT)[0][-1]
    except Exception as e:
        raise Exception(f"DNS resolution failed: {e}")
