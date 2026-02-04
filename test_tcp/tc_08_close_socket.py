# ==============================================================
# TEST CASE DESCRIPTION — TC-08
# ==============================================================
# Purpose:
#   Verify that socket.close() does not crash.
#
# CI Alignment:
#   → Functional validation (Jobs 9–15)
#
# Preconditions:
#   - Active TCP connection exists.
#
# Test Steps:
#   1. Call sock.close().
#
# Expected Result:
#   - Socket closes without exceptions.
#
# ISO/IEC Reference:
#   - ISO/IEC 8073:1997, Clause 11 (Connection release)
# ==============================================================

def run(sock):
    sock.close()
