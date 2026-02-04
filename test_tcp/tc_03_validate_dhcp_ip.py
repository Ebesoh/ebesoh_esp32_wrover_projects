# ==============================================================
# TEST CASE DESCRIPTION — TC-03
# ==============================================================
# Purpose:
#   Verify that the ESP32 receives a valid IP address via DHCP.
#
# CI Alignment:
#   → GitHub Job 12: wifi-test
#
# Preconditions:
#   - Wi-Fi connected (TC-02 passed).
#
# Test Steps:
#   1. Read IP from wlan.ifconfig().
#   2. Check that IP is not 0.0.0.0 or empty.
#
# Expected Result:
#   - A valid IPv4 address is assigned.
#
# ISO/IEC Reference:
#   - ISO/IEC 8348:1993, Clause 7.1 (Address assignment)
# ==============================================================

def run(ip_config):
    # First element is the assigned IP
    ip = ip_config[0]

    # 0.0.0.0 means DHCP failed
    if ip == "0.0.0.0" or ip == "":
        raise Exception(f"Invalid IP assigned: {ip}")

    return ip

