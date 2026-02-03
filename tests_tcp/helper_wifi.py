# ---------------------------------------------------------------------
# SHARED HELPER (NOT A TEST CASE)
# ---------------------------------------------------------------------
# Blocks until Wi-Fi is fully connected and an IP is assigned.
# Used by multiple test cases to guarantee L2/L3 readiness.
# ---------------------------------------------------------------------

import time
from config import CONNECT_TIMEOUT

def wait_for_wifi(wlan, timeout=CONNECT_TIMEOUT):
    """
    ISO/IEC Conceptual Mapping:
    - ISO/IEC 7498-1:1994, Clause 7.2 — Service availability

    Guarantees before higher-layer tests run:
    - Layer 2 (Wi-Fi association) is complete
    - Layer 3 (IP configuration via DHCP) is complete
    """

    start = time.time()  # Remember when we started waiting

    # Poll until the interface reports "connected"
    while not wlan.isconnected():

        # Fail if we exceed timeout
        if time.time() - start > timeout:
            raise Exception("WiFi connection timeout")

        # Small delay to avoid busy-waiting
        time.sleep(0.5)

    # Return (IP, subnet, gateway, DNS)
    return wlan.ifconfig()
