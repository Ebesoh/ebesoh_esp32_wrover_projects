# ---------------------------------------------------------------------
# CENTRAL TEST RUNNER — executes all test cases in order
# ---------------------------------------------------------------------
# This mirrors the "Testing Phase" of your GitHub CI (Jobs 9–15).
# ---------------------------------------------------------------------

import time

import tc_01_wifi_interface_exists as tc01
import tc_02_connect_wifi as tc02
import tc_03_validate_dhcp_ip as tc03
import tc_04_dns_resolution as tc04
import tc_05a_tcp_three_way_handshake as tc05a
import tc_06_tcp_send as tc06
import tc_07_tcp_receive as tc07
import tc_08_close_socket as tc08
import tc_10_tcp_four_step_handshake as tc10
import tc_09_reconnect_robustness as tc09

def log(msg):
    print("[TCP-TEST] " + msg)

def run_test(name, func, *args):
    log(f"START → {name}")
    start = time.ticks_ms()

    result = func(*args)

    elapsed = time.ticks_diff(time.ticks_ms(), start)
    log(f"PASS  → {name} (took {elapsed} ms)")
    return result, elapsed

def run_all_tests():
    log("=== START TCP/IP TEST SUITE ===")
    suite_start = time.ticks_ms()

    timings = {}
    tcp_timings = {}

    try:
        # --- TC-01 ---
        wlan, t = run_test("TC-01 Wi-Fi interface exists", tc01.run)
        timings["TC-01"] = t

        # --- TC-02 ---
        ip_config, t = run_test("TC-02 Connect to Wi-Fi", tc02.run, wlan)
        timings["TC-02"] = t

        # --- TC-03 ---
        ip, t = run_test("TC-03 Validate DHCP IP", tc03.run, ip_config)
        timings["TC-03"] = t
        log(f"Device IP: {ip}")

        # --- TC-04 ---
        addr, t = run_test("TC-04 DNS resolution", tc04.run)
        timings["TC-04"] = t
        tcp_timings["DNS_LOOKUP_MS"] = t

        # --- TC-05a (3-way handshake) ---
        (sock, hs_ms), t = run_test(
            "TC-05a TCP 3-way handshake", tc05a.run, addr
        )
        timings["TC-05a"] = t
        tcp_timings["TCP_3WAY_HANDSHAKE_MS"] = hs_ms
        log(f"TCP 3-way handshake time: {hs_ms} ms")

        # --- TC-06 ---
        sent, t = run_test("TC-06 TCP send", tc06.run, sock)
        timings["TC-06"] = t

        # --- TC-07 ---
        recv, t = run_test("TC-07 TCP receive", tc07.run, sock)
        timings["TC-07"] = t

        # --- TC-08 ---
        _, t = run_test("TC-08 Close socket", tc08.run, sock)
        timings["TC-08"] = t

        # --- TC-10 (4-way handshake) ---
        close_ms, t = run_test(
            "TC-10 TCP 4-step handshake", tc10.run, sock
        )
        timings["TC-10"] = t
        tcp_timings["TCP_4STEP_HANDSHAKE_MS"] = close_ms
        log(f"TCP 4-step handshake time: {close_ms} ms")

        # --- TC-09 ---
        new_ip, t = run_test(
            "TC-09 Reconnect robustness", tc09.run, wlan
        )
        timings["TC-09"] = t
        log(f"Reconnected, IP = {new_ip[0]}")

        total_time = time.ticks_diff(time.ticks_ms(), suite_start)

        log("=== ALL TCP/IP TESTS PASSED ===")
        log("Per-test timing (ms):")
        for k, v in timings.items():
            log(f"  {k}: {v} ms")

        log("Handshake / TCP timings (ms):")
        for k, v in tcp_timings.items():
            log(f"  {k}: {v} ms")

        log(f"TOTAL SUITE TIME: {total_time} ms")
        return True

    except Exception as e:
        log(f"FAILED: {e}")
        raise

if __name__ == "__main__":
    run_all_tests()
