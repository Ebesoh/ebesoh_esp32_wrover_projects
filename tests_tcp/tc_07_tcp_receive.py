# ==============================================================
# TEST CASE DESCRIPTION — TC-07
# ==============================================================
# Purpose:
#   Verify that the ESP32 can receive data over TCP.
#
# CI Alignment:
#   → Functional validation (Jobs 9–15)
#
# Preconditions:
#   - Data successfully sent (TC-06 passed).
#
# Test Steps:
#   1. Call recv().
#   2. Validate data received.
#   3. Check for HTTP header.
#
# Expected Result:
#   - Valid HTTP response received.
#
# ISO/IEC Reference:
#   - ISO/IEC 8073:1997, Clause 10 (Data transfer)
# ==============================================================

def run(sock):
    # Receive up to 1024 bytes
    data = sock.recv(1024)

    # No data means server did not respond
    if not data:
        raise Exception("No data received from server")

    # Basic sanity check: should contain HTTP response
    if b"HTTP" not in data:
        raise Exception("Invalid HTTP response")

    return len(data)

