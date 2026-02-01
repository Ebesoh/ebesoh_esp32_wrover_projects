# gps_fix_consistency_test.py
#Goal: Require multiple valid fixes, not one.
def is_valid_fix(line):
    if not line.startswith("$GPGGA"):
        return False

    parts = line.split(",")
    if len(parts) < 7:
        return False

    fix_quality = parts[6]
    return fix_quality and fix_quality != "0"


def test_fix_consistency(nmea_lines, min_fixes=3):
    print("TEST: GPS fix consistency")

    fixes = 0
    for line in nmea_lines:
        if is_valid_fix(line):
            fixes += 1

    print("Valid fixes detected:", fixes)
    return fixes >= min_fixes

