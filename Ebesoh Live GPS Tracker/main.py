"""
main.py — FINAL WORKING SILENT VERSION

- Reads raw NMEA from ESP32 over USB serial
- Buffers data so we never miss or split sentences
- Parses $GPRMC / $GNRMC and $GPGGA
- Runs 2D Kalman filter on position
- Smooths speed with 1D Kalman filter
- Scales raw uncertainty using HDOP
- Syncs GPS (UTC) to PC time correctly
- Logs everything to CSV
- Streams data to Flask for live map
- Sends the FIRST valid point (no “Waiting for data…”)
"""

import math
import csv
import time
import calendar
from pathlib import Path

import serial
import numpy as np

from conversions import dms_to_decimal, latlon_to_xy, xy_to_latlon
from kalman_filter import KalmanFilter
from live_server import start_in_background, add_point
from plotter import LiveLatLonPlot

# ===========================
# USER SETTINGS
# ===========================

SERIAL_PORT = "COM5"
BAUD = 115200

dt = 0.2                 # GPS update period
BASE_GPS_SIGMA = 2.5     # datasheet accuracy (1σ, meters)
TIME_SYNC_WINDOW = 10
LOOP_SLEEP = 0.05

# ===========================
# 1D KALMAN FILTER FOR SPEED
# ===========================

class SpeedKalman:
    def __init__(self, dt):
        self.x = np.zeros((2, 1))  # [speed, acceleration]
        self.P = np.array([[10.0, 0.0],
                           [0.0,  1.0]])
        self.A = np.array([[1.0, dt],
                           [0.0, 1.0]])
        self.H = np.array([[1.0, 0.0]])
        self.Q = np.array([[0.05, 0.0],
                           [0.0,  0.01]])
        self.R = np.array([[1.0]])
        self.I = np.eye(2)

    def step(self, z):
        # Predict
        self.x = self.A @ self.x
        self.P = self.A @ self.P @ self.A.T + self.Q

        # Update
        z = np.array([[z]])
        y = z - (self.H @ self.x)
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)

        self.x = self.x + K @ y
        self.P = (self.I - K @ self.H) @ self.P

        return float(self.x[0, 0])

# ===========================
# GPS → PC TIME SYNC (UTC SAFE)
# ===========================

def gprmc_utc_to_epoch(fields):
    try:
        t = fields[1]
        hh = int(t[0:2])
        mm = int(t[2:4])
        ss = float(t[4:])

        d = fields[9]
        day = int(d[0:2])
        month = int(d[2:4])
        year = 2000 + int(d[4:6])

        tm = time.struct_time((year, month, day, hh, mm, int(ss), 0, 0, 0))
        return calendar.timegm(tm) + (ss - int(ss))
    except:
        return None

time_offsets = []

def update_time_offset(gps_epoch):
    pc_epoch = time.time()
    offset = pc_epoch - gps_epoch

    time_offsets.append(offset)
    if len(time_offsets) > TIME_SYNC_WINDOW:
        time_offsets.pop(0)

    return sum(time_offsets) / len(time_offsets)

# ===========================
# CSV LOGGER
# ===========================

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

timestamp = time.strftime("%Y%m%d_%H%M%S")
csv_path = log_dir / f"gps_log_{timestamp}.csv"

csv_file = open(csv_path, "w", newline="")
csv_writer = csv.writer(csv_file)

csv_writer.writerow([
    "gps_epoch_s",
    "pc_epoch_s",
    "time_offset_ms",
    "raw_lat", "raw_lon",
    "filt_lat", "filt_lon",
    "raw_unc_m",
    "filt_unc_x_m", "filt_unc_y_m",
    "speed_kmh",
    "sats_used", "sats_in_view",
    "direction",
    "altitude_m",
    "alt_unc_m",
    "fix_quality"
])

# Startup messages only
print(f"Logging to: {csv_path}")
print("Starting live map server at http://127.0.0.1:5000")
print("Opening serial...")
print("Running...")

# ===========================
# START LIVE MAP SERVER
# ===========================

start_in_background()

# ===========================
# OPEN SERIAL
# ===========================

ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)

# ===========================
# FILTERS + PLOTTER
# ===========================

kf = KalmanFilter(dt)
speed_filter = SpeedKalman(dt)
plotter = LiveLatLonPlot()

lat0 = None
lon0 = None

sats_used = 0
sats_in_view = 0
raw_sigma_m = BASE_GPS_SIGMA
altitude_m = 0.0
alt_unc_m = BASE_GPS_SIGMA * 1.5
fix_quality = 0
fix_meaning = "Unknown"

# ===========================
# BUFFERED SERIAL READER
# ===========================

buffer = b""

while True:
    chunk = ser.read(64)
    if not chunk:
        time.sleep(LOOP_SLEEP)
        continue

    buffer += chunk

    while b"\n" in buffer:
        line_bytes, buffer = buffer.split(b"\n", 1)
        line = line_bytes.decode(errors="ignore").strip()
        fields = line.split(",")

        # --- GPGGA ---
        if "$GPGGA" in line:
            try:
                sats_used = int(fields[7])
                hdop = float(fields[8])
                altitude_m = float(fields[9])
                fix_quality = int(fields[6])
            except:
                sats_used = 0
                hdop = 99.9
                altitude_m = 0.0
                fix_quality = 0

            sats_in_view = sats_used
            raw_sigma_m = BASE_GPS_SIGMA * max(1.0, hdop)
            alt_unc_m = raw_sigma_m * 1.5

            fix_meaning = {
                0: "No fix",
                1: "GPS fix",
                2: "DGPS fix",
                4: "RTK fixed",
                5: "RTK float"
            }.get(fix_quality, "Unknown")

        # --- GPRMC / GNRMC ---
        if "$GPRMC" in line or "$GNRMC" in line:
            lat = dms_to_decimal(fields[3], fields[4])
            lon = dms_to_decimal(fields[5], fields[6])

            gps_epoch = gprmc_utc_to_epoch(fields)
            pc_now = time.time()

            if gps_epoch is not None:
                update_time_offset(gps_epoch)

            time_offset_ms = (pc_now - gps_epoch) * 1000.0 if gps_epoch else 0.0

            try:
                sog_knots = float(fields[7])
            except:
                sog_knots = 0.0

            raw_speed_kmh = sog_knots * 1.852
            smooth_speed_kmh = speed_filter.step(raw_speed_kmh)

            try:
                cog_deg = float(fields[8])
            except:
                cog_deg = 0.0

            direction = "Forward" if cog_deg >= 180 else "Reverse"

            if lat0 is None and lat is not None:
                lat0, lon0 = lat, lon  # set origin once

            if lat is None:
                continue

            # --- FILTERING ---
            x_raw, y_raw = latlon_to_xy(lat, lon, lat0, lon0)

            kf.predict()
            kf.update([x_raw, y_raw])

            x_f, y_f = kf.get_state()
            sx, sy = kf.get_uncertainty()

            lat_raw_disp, lon_raw_disp = xy_to_latlon(x_raw, y_raw, lat0, lon0)
            lat_filt_disp, lon_filt_disp = xy_to_latlon(x_f, y_f, lat0, lon0)

            plotter.add_point(x_raw, y_raw, x_f, y_f)

            # --- LOG TO CSV ---
            csv_writer.writerow([
                round(gps_epoch if gps_epoch else 0, 3),
                round(pc_now, 3),
                round(time_offset_ms, 1),
                lat_raw_disp, lon_raw_disp,
                lat_filt_disp, lon_filt_disp,
                raw_sigma_m,
                sx, sy,
                smooth_speed_kmh,
                sats_used, sats_in_view,
                direction,
                altitude_m,
                alt_unc_m,
                fix_quality
            ])
            csv_file.flush()

            # --- SEND TO MAP (FIRST POINT INCLUDED) ---
            add_point(
                lat_raw_disp, lon_raw_disp,
                lat_filt_disp, lon_filt_disp,
                raw_sigma_m,
                sx, sy,
                smooth_speed_kmh,
                sats_used, sats_in_view,
                direction,
                altitude_m,
                alt_unc_m,
                fix_quality,
                fix_meaning,
                pc_now,
                gps_epoch,
                time_offset_ms
            )

    time.sleep(LOOP_SLEEP)
