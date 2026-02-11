"""
nmea_tables.py

Pretty-prints $GPRMC and $GPGGA fields with meaning and value.
"""

def print_gprmc_table(fields):
    meanings = [
        "RMC - Recommended Minimum Data",
        "UTC time",
        "Status (A=valid)",
        "Latitude (raw)",
        "N/S",
        "Longitude (raw)",
        "E/W",
        "Speed over ground (knots)",
        "Course over ground (deg)",
        "Date (DDMMYY)",
        "Magnetic variation",
        "Mag var E/W",
        "Mode",
        "Checksum"
    ]

    print("\n--- $GPRMC FIELDS ---")
    for i, m in enumerate(meanings):
        val = fields[i] if i < len(fields) else ""
        print(f"{i:02d} | {m:<35} | {val}")

def print_gpgga_table(fields):
    meanings = [
        "GGA - Fix data",
        "UTC time",
        "Latitude (raw)",
        "N/S",
        "Longitude (raw)",
        "E/W",
        "Fix quality",
        "Satellites used",
        "HDOP",
        "Altitude (m)",
        "Altitude units",
        "Geoid separation",
        "Geoid units",
        "Age of DGPS",
        "DGPS station ID",
        "Checksum"
    ]

    print("\n--- $GPGGA FIELDS ---")
    for i, m in enumerate(meanings):
        val = fields[i] if i < len(fields) else ""
        print(f"{i:02d} | {m:<35} | {val}")
