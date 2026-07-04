import pyqtgraph as pg
from collections import deque


class IMUGraphs:

    def __init__(self, maxlen=500):

        pg.setConfigOption("background", "#0d0f14")
        pg.setConfigOption("foreground", "w")

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
        self.win.resize(1200, 800)

        self.win.setWindowTitle("MPU6050 Live Viewer")

        # ---------------- ACCEL ----------------
        self.p1 = self.win.addPlot(title="Accelerometer (g)")
        self.p1.showGrid(x=True, y=True, alpha=0.3)
        self.p1.addLegend()

        self.curve_ax = self.p1.plot(pen="r", name="Ax")
        self.curve_ay = self.p1.plot(pen="g", name="Ay")
        self.curve_az = self.p1.plot(pen="b", name="Az")

        # ---------------- GYRO ----------------
        self.win.nextRow()

        self.p2 = self.win.addPlot(title="Gyroscope (deg/s)")
        self.p2.showGrid(x=True, y=True, alpha=0.3)
        self.p2.addLegend()

        self.curve_gx = self.p2.plot(pen="r", name="Gx")
        self.curve_gy = self.p2.plot(pen="g", name="Gy")
        self.curve_gz = self.p2.plot(pen="b", name="Gz")

        # Timer update (handled externally too)
        self.win.show()

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
