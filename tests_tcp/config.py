# ---------------------------------------------------------------------
# CENTRAL CONFIGURATION FOR ALL TCP/IP TESTS
# ---------------------------------------------------------------------
# This file defines all network parameters so tests remain portable
# across different labs, access points, or environments.
# ---------------------------------------------------------------------

# Wi-Fi credentials used by every test that connects to the network.
SSID = "Familj_Ebesoh_2.4"
PASSWORD = "AmandaAlicia1991"

# Target host for all TCP/DNS tests.
# A stable, publicly reachable endpoint.
TEST_HOST = "example.com"
TEST_PORT = 80  # Standard HTTP port

# Maximum time to wait for Wi-Fi association + DHCP.
CONNECT_TIMEOUT = 15  # seconds
