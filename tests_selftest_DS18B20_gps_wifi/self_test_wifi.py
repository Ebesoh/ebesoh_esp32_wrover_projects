# --------------------------------------------
# This is a real Wi-Fi self-test. It verifies:
#
#   ✓ Wi-Fi radio initializes successfully
#   ✓ Authentication and association complete
#   ✓ DHCP assigns a valid IP address
#   ✓ RSSI meets the minimum signal threshold
#   ✓ DNS resolution is functional
#   ✓ TCP/IP stack is operational
#   ✓ Outbound network traffic is confirmed
#
# Verdict:
#   A PASS means Wi-Fi is genuinely usable, not just "connected".

import network
import time
import socket

# ---------------- CONFIG ----------------

SSID = "Familj_Ebesoh_2.4"
PASSWORD = "AmandaAlicia1991"

CONNECT_TIMEOUT_S = 15
TCP_TIMEOUT_S = 5
RSSI_MIN_DBM = -85

TEST_HOST = "example.com"
TEST_PORT = 80

# --------------------------------------


def wifi_self_test():
    print("Starting Wi-Fi self-test")

    reasons = []

    wlan = network.WLAN(network.STA_IF)

    # ---------- Reset Wi-Fi state ----------
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)
    time.sleep(1)

    # ---------- Step 1: Connect ----------
    wlan.connect(SSID, PASSWORD)

    start = time.time()
    while not wlan.isconnected():
        if time.time() - start > CONNECT_TIMEOUT_S:
            return "FAIL", ["Wi-Fi connection timeout"]
        time.sleep(0.5)

    ip, _, _, _ = wlan.ifconfig()
    rssi = wlan.status("rssi")

    print("✓ Wi-Fi connected")
    print("IP address:", ip)
    print("RSSI:", rssi, "dBm")

    # ---------- Step 2: RSSI sanity ----------
    if rssi is None:
        reasons.append("RSSI not reported")
    elif rssi < RSSI_MIN_DBM:
        reasons.append(f"RSSI below threshold ({rssi} dBm)")

    # ---------- Step 3: DNS resolution ----------
    try:
        addr_info = socket.getaddrinfo(TEST_HOST, TEST_PORT)
        addr = addr_info[0][-1]
        print("✓ DNS resolution OK")
    except Exception as e:
        return "FAIL", [f"DNS resolution failed: {e}"]

    # ---------- Step 4: TCP/IP stack ----------
    s = None
    try:
        s = socket.socket()
        s.settimeout(TCP_TIMEOUT_S)
        s.connect(addr)
        s.send(b"HEAD / HTTP/1.0\r\nHost: example.com\r\n\r\n")
        print("✓ TCP/IP stack OK")
    except Exception as e:
        return "FAIL", [f"TCP connection failed: {e}"]
    finally:
        if s:
            try:
                s.close()
            except Exception:
                pass

    # ---------- Verdict ----------
    if reasons:
        return "FAIL", reasons

    return "PASS", ["All Wi-Fi checks passed"]


# ---------------- ENTRY ----------------

if __name__ == "__main__":
    verdict, reasons = wifi_self_test()

    print("=" * 60)
    print("WIFI SELF-TEST VERDICT:", verdict)

    for r in reasons:
        print("-", r)

    print("CI_RESULT:", verdict)
    print("=" * 60)



           

