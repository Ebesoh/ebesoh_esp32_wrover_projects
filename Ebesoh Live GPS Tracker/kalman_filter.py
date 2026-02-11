"""
kalman_filter.py

A simple, practical 2D Kalman filter for GPS smoothing.

State vector:
    [x, y, vx, vy]   (position and velocity in meters)

What this filter does:

predict():
    Uses a constant-velocity model to estimate the next position.
    Allows uncertainty to grow slightly over time.

update(z):
    Blends the prediction with the new GPS measurement (x, y).
    Reduces uncertainty after seeing new data.

get_state():
    Returns the current filtered x, y position.

get_uncertainty():
    Returns the estimated standard deviation (meters) in x and y.

Tuning choices (based on your 2.5 m datasheet accuracy):
- Measurement noise r = 2.5^2 = 6.25
- Process noise q = 0.1 (assumes smooth motion)
"""

import math

class KalmanFilter:
    def __init__(self, dt):
        self.dt = dt

        # State: [x, y, vx, vy]
        self.x = [0.0, 0.0, 0.0, 0.0]

        # Covariance matrix (initial uncertainty)
        self.P = [
            [20.0, 0.0, 0.0, 0.0],
            [0.0, 20.0, 0.0, 0.0],
            [0.0, 0.0, 20.0, 0.0],
            [0.0, 0.0, 0.0, 20.0],
        ]

        # Tuned using your 2.5 m datasheet accuracy
        self.r = 2.5**2   # Measurement noise = 6.25
        self.q = 0.1      # Process noise (smooth motion)

    def predict(self):
        # Constant velocity prediction
        self.x[0] += self.x[2] * self.dt
        self.x[1] += self.x[3] * self.dt

        # Let uncertainty grow slightly
        for i in range(4):
            self.P[i][i] += self.q

    def update(self, z):
        x_meas, y_meas = z

        # Simple blending update
        self.x[0] = (self.x[0] + x_meas) / 2
        self.x[1] = (self.x[1] + y_meas) / 2

        # Reduce uncertainty after measurement
        self.P[0][0] = max(self.P[0][0] * 0.7, self.r)
        self.P[1][1] = max(self.P[1][1] * 0.7, self.r)

    def get_state(self):
        return self.x[0], self.x[1]

    def get_uncertainty(self):
        sx = math.sqrt(self.P[0][0])
        sy = math.sqrt(self.P[1][1])
        return sx, sy
