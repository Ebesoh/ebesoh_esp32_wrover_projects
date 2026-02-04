# ==============================================================
# TEST CASE DESCRIPTION — TC-09
# ==============================================================
# Purpose:
#   Verify that the ESP32 can recover from Wi-Fi disconnection.
#
# CI Alignment:
#   → Functional validation (Jobs 9–15)
#
# Preconditions:
#   - Wi-Fi was previously connected.
#
# Test Steps:
#   1. Disconnect from AP.
#   2. Wait 2 seconds.
#   3. Reconnect to AP.
#   4. Wait for new IP.
#
# Expected Result:
#   - Successful reconnection and IP assignment.
#
# ISO/IEC Reference:
#   - ISO/IEC 8802-11:2020, Clause 10 (Re-association)
#   - ISO/IEC 8348:1993, Clause 7.1 (Dynamic address assignment)
# ==============================================================

import time
from config import SSID, PASSWORD
from helper_wifi import wait_for_wifi

def run(wlan):
    wlan.disconnect()
    time.sleep(2)
    wlan.connect(SSID, PASSWORD)
    return wait_for_wifi(wlan)
