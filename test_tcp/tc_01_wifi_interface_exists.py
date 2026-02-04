# ==============================================================
# TEST CASE DESCRIPTION — TC-01
# ==============================================================
# Purpose:
#   Verify that the ESP32 exposes a functional Wi-Fi station interface.
#
# CI Alignment:
#   → GitHub Job 12: wifi-test (bring-up prerequisite)
#
# Preconditions:
#   - ESP32 powered and running MicroPython.
#
# Test Steps:
#   1. Create a WLAN(STA_IF) interface.
#   2. Verify that a valid object is returned.
#
# Expected Result:
#   - WLAN interface exists and is usable.
#
# ISO/IEC Reference:
#   - ISO/IEC 8802-11:2020, Clause 5.2 (STA management)
#   - ISO/IEC 7498-1:1994, Clause 6 (OSI Layer model)
# ==============================================================

import network

def run():
    # Create Wi-Fi station interface (client mode)
    wlan = network.WLAN(network.STA_IF)

    # If this fails, the Wi-Fi stack is fundamentally broken
    if not wlan:
        raise Exception("Failed to create WLAN interface")

    # Return interface for downstream tests
    return wlan
