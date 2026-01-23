#--------------------------------------------
#  This is not superficial. It checks:

#     ✅ Wi-Fi radio starts

#     ✅ Authentication works

#     ✅ IP address assigned

#     ✅ RSSI above minimum threshold

#     ✅ DNS resolution works

#     ✅ TCP/IP stack works

#     ✅ Outbound network traffic works

#      Verdict: If this says PASS, Wi-Fi is genuinely functional.

import network
import time
import socket

SSID = "Familj_Ebesoh_2.4"
PASSWORD = "AmandaAlicia1991"

CONNECT_TIMEOUT = 15      # seconds
TCP_TIMEOUT = 5           # seconds
RSSI_MIN = -85            # dBm


def wifi_self_test():
    verdict = "PASS"
    reasons = []

    wlan = network.WLAN(network.STA_IF)

    # Reset Wi-Fi state
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)
    time.sleep(1)

    print("Starting Wi-Fi self-test...")
    wlan.connect(SSID, PASSWORD)

    # -------- Step 1: Connect --------
    start = time.time()
    while not wlan.isconnected():
        if time.time() - start > CONNECT_TIMEOUT:
            verdict = "FAIL"
            reasons.append("Wi-Fi connection timeout")
            break
        time.sleep(0.5)

    if not wlan.isconnected():
        return verdict, reasons

    ip = wlan.ifconfig()[0]
    rssi = wlan.status("rssi")

    print("Wi-Fi connected")
    print("IP:", ip)
    print("RSSI:", rssi, "dBm")

    # -------- Step 2: RSSI check --------
    if rssi is None or rssi < RSSI_MIN:
        verdict = "FAIL"
        reasons.append("Weak RSSI ({})".format(rssi))

    # -------- Step 3: TCP stack test --------
    try:
        addr = socket.getaddrinfo("example.com", 80)[0][-1]
        s = socket.socket()
        s.settimeout(TCP_TIMEOUT)
        s.connect(addr)
        s.send(b"HEAD / HTTP/1.0\r\nHost: example.com\r\n\r\n")
        s.close()
        print("TCP stack OK")
    except Exception as e:
        verdict = "FAIL"
        reasons.append("TCP test failed")

    return verdict, reasons


# -----------------------------
# RUN SELF TEST
# -----------------------------

verdict, reasons = wifi_self_test()

print("==============================")
print("WIFI SELF-TEST VERDICT:", verdict)

if reasons:
    for r in reasons:
        print("-", r)
else:
    print("All checks passed")

print("==============================")

           

