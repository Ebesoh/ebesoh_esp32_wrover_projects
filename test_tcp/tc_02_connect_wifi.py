# ==============================================================
# TEST CASE DESCRIPTION — TC-02
# ==============================================================
# Purpose:
#   Verify that the ESP32 can associate with a Wi-Fi access point.
#
# CI Alignment:
#   → GitHub Job 12: wifi-test
#
# Preconditions:
#   - Valid SSID and PASSWORD configured in config.py.
#   - TC-01 passed.
#
# Test Steps:
#   1. Activate Wi-Fi interface.
#   2. Attempt to connect to the access point.
#   3. Wait until connection and IP assignment.
#
# Expected Result:
#   - ESP32 associates with AP and obtains an IP address.
#
# ISO/IEC Reference:
#   - ISO/IEC 8802-11:2020, Clause 11 (Association procedures)
# ==============================================================

import network
from config import SSID, PASSWORD
from helper_wifi import wait_for_wifi

def run(wlan):
    # Ensure radio is active
    wlan.active(True)

    # Initiate association if not already connected
    if not wlan.isconnected():
        wlan.connect(SSID, PASSWORD)

    # Block until L2 + L3 are ready
    return wait_for_wifi(wlan)
