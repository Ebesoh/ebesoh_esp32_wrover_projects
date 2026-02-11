"""
plot_altitude.py

Live altitude vs time plot that works in Thonny
(no background thread, no Tk crashes).
"""

import matplotlib.pyplot as plt
import time

class AltitudePlot:
    def __init__(self):
        self.t = []
        self.alt = []
        self.start_time = time.time()

        self.fig, self.ax = plt.subplots()
        (self.line,) = self.ax.plot([], [])

        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Altitude (m)")
        self.ax.set_title("Live Altitude vs Time")

        plt.ion()
        plt.show()

    def add_point(self, altitude_m):
        now = time.time() - self.start_time
        self.t.append(now)
        self.alt.append(altitude_m)

        # Update plot safely in the main thread
        self.line.set_xdata(self.t)
        self.line.set_ydata(self.alt)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

