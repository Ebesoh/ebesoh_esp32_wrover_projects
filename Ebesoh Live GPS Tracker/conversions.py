"""
conversions.py

All coordinate math lives here.

GPS gives positions in latitude/longitude (degrees), but your Kalman filter
works best in meters. This file handles all conversions.

Functions:

dms_to_decimal(dms, direction):
    Converts NMEA format (degrees + minutes) into decimal degrees.

latlon_to_xy(lat, lon, lat0, lon0):
    Converts latitude/longitude into local x/y coordinates in meters,
    using the first valid GPS fix as the origin.

xy_to_latlon(x, y, lat0, lon0):
    Converts filtered x/y positions (meters) back into latitude/longitude
    for display on the map.
"""

import math

def dms_to_decimal(dms, direction):
    if not dms:
        return None
    deg = int(float(dms) / 100)
    minutes = float(dms) - deg * 100
    dec = deg + minutes / 60.0
    if direction in ["S", "W"]:
        dec = -dec
    return dec

def latlon_to_xy(lat, lon, lat0, lon0):
    R = 6371000  # Earth radius in meters
    x = math.radians(lon - lon0) * R * math.cos(math.radians(lat0))
    y = math.radians(lat - lat0) * R
    return x, y

def xy_to_latlon(x, y, lat0, lon0):
    R = 6371000
    lat = lat0 + math.degrees(y / R)
    lon = lon0 + math.degrees(x / (R * math.cos(math.radians(lat0))))
    return lat, lon
