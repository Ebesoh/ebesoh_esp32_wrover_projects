# gps_coordinate_sanity_test.py
#Goal: Catch broken parsers or corrupt data.
def test_coordinate_sanity(nmea_lines):
    print("TEST: Coordinate sanity")

    for line in nmea_lines:
        if not line.startswith("$GPGGA"):
            continue

        parts = line.split(",")
        try:
            lat = float(parts[2])
            lon = float(parts[4])
        except Exception:
            continue

        if 0 < lat < 9000 and 0 < lon < 18000:
            print("Coordinates look sane")
            return True

    print("No sane coordinates found")
    return False
