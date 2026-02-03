# ==============================================================
# TEST CASE DESCRIPTION — TC-05a
# ==============================================================
# Purpose:
#   Validate the TCP 3-way handshake for connection establishment.
#
# CI Alignment:
#   → Core functional validation (Jobs 9–15)
#
# Preconditions:
#   - DNS resolved (TC-04 passed).
#
# Test Steps:
#   1. Create a TCP socket.
#   2. Call connect() (SYN → SYN/ACK → ACK).
#   3. Measure handshake duration.
#   4. Verify timing is within allowed window.
#   5. Send test data to confirm usability.
#
# Expected Result:
#   - TCP connection established.
#   - Handshake time: 10 ms ≤ t ≤ 5000 ms.
#
# ISO/IEC Reference:
#   - ISO/IEC 8073:1997, Clause 9 (Connection establishment)
# ==============================================================

import socket, time

def run(addr):
    # Create TCP socket
    s = socket.socket()

    # Prevent infinite blocking in CI
    s.settimeout(5)

    # Start timing before SYN
    t0 = time.ticks_ms()

    try:
        # Internally performs SYN → SYN/ACK → ACK
        s.connect(addr)
    except Exception as e:
        s.close()
        raise Exception(f"TCP 3-way handshake failed: {e}")

    # Stop timing after ACK completes
    t1 = time.ticks_ms()

    handshake_time = time.ticks_diff(t1, t0)

    # Sanity check for real handshake timing
    if handshake_time < 10:
        raise Exception(f"Handshake too fast: {handshake_time} ms")

    if handshake_time > 5000:
        raise Exception(f"Handshake too slow: {handshake_time} ms")

    # Prove the connection is actually usable
    try:
        s.send(b"PING")
    except Exception as e:
        raise Exception("Socket unusable after handshake: " + str(e))

    return s, handshake_time
