"""
plotter.py

Live 2D plot of:
- Raw position (red)
- Filtered position (blue)

Designed to work reliably inside Thonny.
"""

import matplotlib.pyplot as plt

class LiveLatLonPlot:
    def __init__(self):
        self.raw_x = []
        self.raw_y = []
        self.filt_x = []
        self.filt_y = []

        self.fig, self.ax = plt.subplots()

        (self.raw_line,) = self.ax.plot([], [], 'r-', label="Raw")
        (self.filt_line,) = self.ax.plot([], [], 'b-', label="Filtered")

        self.ax.set_xlabel("X (meters)")
        self.ax.set_ylabel("Y (meters)")
        self.ax.set_title("Raw vs Filtered Position (Local Frame)")
        self.ax.legend()
        self.ax.grid(True)

        plt.ion()
        plt.show()

    def add_point(self, x_raw, y_raw, x_filt, y_filt):
        self.raw_x.append(x_raw)
        self.raw_y.append(y_raw)
        self.filt_x.append(x_filt)
        self.filt_y.append(y_filt)

        # Update lines
        self.raw_line.set_xdata(self.raw_x)
        self.raw_line.set_ydata(self.raw_y)

        self.filt_line.set_xdata(self.filt_x)
        self.filt_line.set_ydata(self.filt_y)

        # Rescale view automatically
        self.ax.relim()
        self.ax.autoscale_view()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

