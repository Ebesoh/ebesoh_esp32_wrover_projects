# speed_filter.py
import math

class SpeedKalman:
    """
    Simple 1D Kalman filter for speed (km/h).
    State: [speed, acceleration]
    """

    def __init__(self, dt):
        self.dt = dt

        # State vector [v, a]
        self.x = [[0.0],
                  [0.0]]

        # Covariance
        self.P = [[10.0, 0.0],
                  [0.0, 1.0]]

        # State transition matrix
        self.A = [[1.0, dt],
                  [0.0, 1.0]]

        # Measurement matrix (we measure speed only)
        self.H = [[1.0, 0.0]]

        # Process noise (trust in model)
        self.Q = [[0.05, 0.0],
                  [0.0, 0.01]]

        # Measurement noise (GPS speed noise)
        self.R = [[1.0]]  # tune this if needed

    def predict(self):
        # x = A x
        x0 = self.x[0][0]
        x1 = self.x[1][0]

        self.x[0][0] = self.A[0][0]*x0 + self.A[0][1]*x1
        self.x[1][0] = self.A[1][1]*x1

        # P = A P A^T + Q
        P00 = self.P[0][0]
        P01 = self.P[0][1]
        P10 = self.P[1][0]
        P11 = self.P[1][1]

        self.P[0][0] = P00 + self.Q[0][0]
        self.P[1][1] = P11 + self.Q[1][1]

    def update(self, z):
        # Innovation y = z - Hx
        y = z - self.x[0][0]

        # Innovation covariance S = H P H^T + R
        S = self.P[0][0] + self.R[0][0]

        # Kalman gain K = P H^T / S
        K0 = self.P[0][0] / S
        K1 = self.P[1][0] / S

        # State update x = x + K y
        self.x[0][0] += K0 * y
        self.x[1][0] += K1 * y

        # Covariance update
        self.P[0][0] *= (1 - K0)
        self.P[1][1] *= (1 - K1)

    def step(self, raw_speed):
        self.predict()
        self.update(raw_speed)
        return self.x[0][0]
