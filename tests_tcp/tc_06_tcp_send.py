# ==============================================================
# TEST CASE DESCRIPTION — TC-06
# ==============================================================
# Purpose:
#   Verify that the ESP32 can transmit data over TCP.
#
# CI Alignment:
#   → Functional validation (Jobs 9–15)
#
# Preconditions:
#   - Successful TCP handshake (TC-05a passed).
#
# Test Steps:
#   1. Send HTTP GET request.
#   2. Verify non-zero bytes sent.
#
# Expected Result:
#   - At least one byte transmitted.
#
# ISO/IEC Reference:
#   - ISO/IEC 8073:1997, Clause 10 (Data transfer)
# ==============================================================

def run(sock):
    # Simple HTTP GET request
    request = (
        b"GET / HTTP/1.1\r\n"
        b"Host: example.com\r\n"
        b"Connection: close\r\n\r\n"
    )

    # Send data over TCP
    sent = sock.send(request)

    # If 0 bytes were sent, something is wrong
    if sent == 0:
        raise Exception("Socket send returned 0 bytes")

    return sent
