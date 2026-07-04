import os
os.environ.setdefault("PYQTGRAPH_QT_LIB", "PyQt5")

import pyqtgraph as pg
from collections import deque


ACCENT = "#5ee6c8"
BG_DARK = "#0d0f14"
GRID_COLOR = "#252b3a"

# Couleurs cohérentes avec le thème du dashboard
COLOR_X = "#e65e5e"   # rouge doux
COLOR_Y = "#5ee6c8"   # accent (vert/cyan)
COLOR_Z = "#5e8ee6"   # bleu doux


class IMUGraphs:

    def __init__(self, maxlen=500):

        pg.setConfigOptions(antialias=True)
        pg.setConfigOption("background", BG_DARK)
        pg.setConfigOption("foreground", "#e6e9f0")

        self.maxlen = maxlen

        # Buffers
        self.ax = deque(maxlen=maxlen)
        self.ay = deque(maxlen=maxlen)
        self.az = deque(maxlen=maxlen)

        self.gx = deque(maxlen=maxlen)
        self.gy = deque(maxlen=maxlen)
        self.gz = deque(maxlen=maxlen)

        self.t = deque(maxlen=maxlen)
        self.index = 0

        # Window
        self.win = pg.GraphicsLayoutWidget(title="IMU Live Dashboard")
        self.win.setBackground(BG_DARK)

        # ---------------- ACCEL ----------------
        self.p1 = self.win.addPlot(title="Accéléromètre (g)")
        self._style_plot(self.p1)

        self.curve_ax = self.p1.plot(pen=pg.mkPen(COLOR_X, width=2), name="Ax")
        self.curve_ay = self.p1.plot(pen=pg.mkPen(COLOR_Y, width=2), name="Ay")
        self.curve_az = self.p1.plot(pen=pg.mkPen(COLOR_Z, width=2), name="Az")

        # ---------------- GYRO ----------------
        self.win.nextRow()

        self.p2 = self.win.addPlot(title="Gyroscope (deg/s)")
        self._style_plot(self.p2)

        self.curve_gx = self.p2.plot(pen=pg.mkPen(COLOR_X, width=2), name="Gx")
        self.curve_gy = self.p2.plot(pen=pg.mkPen(COLOR_Y, width=2), name="Gy")
        self.curve_gz = self.p2.plot(pen=pg.mkPen(COLOR_Z, width=2), name="Gz")

    # -----------------------------------------------------

    def _style_plot(self, plot):
        plot.showGrid(x=True, y=True, alpha=0.15)
        plot.addLegend(offset=(10, 10))
        plot.getAxis("left").setPen(GRID_COLOR)
        plot.getAxis("bottom").setPen(GRID_COLOR)
        plot.setMenuEnabled(False)

    # -----------------------------------------------------

    def add_data(self, data):

        self.ax.append(data["ax"])
        self.ay.append(data["ay"])
        self.az.append(data["az"])

        self.gx.append(data["gx"])
        self.gy.append(data["gy"])
        self.gz.append(data["gz"])

        self.t.append(self.index)
        self.index += 1

    # -----------------------------------------------------

    def update(self):

        if len(self.ax) < 2:
            return

        x = list(self.t)

        self.curve_ax.setData(x, list(self.ax))
        self.curve_ay.setData(x, list(self.ay))
        self.curve_az.setData(x, list(self.az))

        self.curve_gx.setData(x, list(self.gx))
        self.curve_gy.setData(x, list(self.gy))
        self.curve_gz.setData(x, list(self.gz))

    # -----------------------------------------------------

    def attach(self, serial_manager):

        def callback(data):
            self.add_data(data)

        serial_manager.add_callback(callback)
