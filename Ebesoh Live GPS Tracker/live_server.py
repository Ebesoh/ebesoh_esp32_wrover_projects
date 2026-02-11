"""
live_server.py — serves data to the map, including PC/GPS time and sync status
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

lock = threading.Lock()

raw_track = []
filt_track = []

latest_uncertainty = {
    "raw": 0.0,
    "filt_x": 0.0,
    "filt_y": 0.0,
    "alt": 0.0
}

latest_speed = 0.0
latest_sats_used = 0
latest_sats_in_view = 0
latest_direction = "Stopped"
latest_altitude = 0.0
latest_fix_quality = 0
latest_fix_meaning = "Unknown"

latest_pc_time = 0.0
latest_gps_time = 0.0
latest_time_offset_ms = 0.0

@app.route("/")
def index():
    return send_from_directory(".", "map.html")

@app.route("/points")
def points():
    with lock:
        return jsonify({
            "raw": list(raw_track),
            "filtered": list(filt_track),
            "uncertainty": dict(latest_uncertainty),
            "speed_kmh": latest_speed,
            "sats_used": latest_sats_used,
            "sats_in_view": latest_sats_in_view,
            "direction": latest_direction,
            "altitude_m": latest_altitude,
            "fix_quality": latest_fix_quality,
            "fix_meaning": latest_fix_meaning,
            "pc_time": latest_pc_time,
            "gps_time": latest_gps_time,
            "time_offset_ms": latest_time_offset_ms
        })

def add_point(raw_lat, raw_lon, filt_lat, filt_lon,
              raw_sigma_m, filt_sx_m, filt_sy_m,
              speed_kmh,
              sats_used, sats_in_view,
              direction,
              altitude_m,
              alt_unc_m,
              fix_quality,
              fix_meaning,
              pc_time,
              gps_time,
              time_offset_ms):

    global latest_speed, latest_sats_used, latest_sats_in_view
    global latest_direction, latest_altitude
    global latest_fix_quality, latest_fix_meaning
    global latest_pc_time, latest_gps_time, latest_time_offset_ms

    with lock:
        raw_track.append([raw_lat, raw_lon])
        filt_track.append([filt_lat, filt_lon])

        latest_uncertainty["raw"] = float(raw_sigma_m)
        latest_uncertainty["filt_x"] = float(filt_sx_m)
        latest_uncertainty["filt_y"] = float(filt_sy_m)
        latest_uncertainty["alt"] = float(alt_unc_m)

        latest_speed = float(speed_kmh)
        latest_sats_used = int(sats_used)
        latest_sats_in_view = int(sats_in_view)
        latest_direction = str(direction)
        latest_altitude = float(altitude_m)
        latest_fix_quality = int(fix_quality)
        latest_fix_meaning = str(fix_meaning)

        latest_pc_time = float(pc_time)
        latest_gps_time = float(gps_time) if gps_time is not None else 0.0
        latest_time_offset_ms = float(time_offset_ms)

def start_in_background():
    t = threading.Thread(
        target=lambda: app.run(
            host="0.0.0.0",
            port=5000,
            debug=False,
            use_reloader=False
        ),
        daemon=True
    )
    t.start()

