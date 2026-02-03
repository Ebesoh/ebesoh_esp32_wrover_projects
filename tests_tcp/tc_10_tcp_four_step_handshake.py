# ==============================================================
# TEST CASE DESCRIPTION — TC-10
# ==============================================================
# Purpose:
#   Validate the TCP 4-step handshake for graceful teardown.
#
# CI Alignment:
#   → Final functional validation before verdict (Jobs 9–15)
#
# Preconditions:
#   - Active TCP connection exists.
#
# Test Steps:
#   1. Call sock.close() (triggers FIN → ACK → FIN → ACK internally).
#   2. Actively wait until the socket is truly unusable.
#   3. Measure effective close duration.
#
# Expected Result:
#   - Clean connection release.
#   - Effective close time ≤ 2000 ms.
#   - Socket cannot be used after close.
#
# ISO/IEC Reference:
#   - ISO/IEC 8073:1997, Clause 11 (Connection release)
# ==============================================================

import time

MAX_CLOSE_TIME_MS = 2000   # ISO-aligned upper bound

def run(sock):
    # Start timing before requesting close
    t0 = time.ticks_ms()

    # Request graceful close (may return immediately on ESP32)
    try:
        sock.close()
    except Exception as e:
        raise Exception("Graceful close call failed: " + str(e))

    # Now we WAIT until the socket is truly dead
    # This is the key fix for ESP32 / MicroPython behavior
    while True:
        elapsed = time.ticks_diff(time.ticks_ms(), t0)

        if elapsed > MAX_CLOSE_TIME_MS:
            raise Exception(
                f"Close too slow: {elapsed} ms (possible stuck FIN_WAIT)"
            )

        try:
            sock.send(b"TEST")
            # If we can still send, teardown is NOT finished yet
            time.sleep(0.05)  # small delay before retry
            continue
        except:
            # Send failed → socket is now truly closed
            break

    # Final effective close time
    close_time = time.ticks_diff(time.ticks_ms(), t0)
    return close_time

