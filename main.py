import sys
import time
from viewer3d import IMUCube3D
from PyQt5 import QtWidgets, QtCore, QtGui

from serial_manager import SerialManager
from graphs import IMUGraphs


class IMUDashboard(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ESP32 MPU6050 Dashboard")
        self.resize(1400, 800)
        
        # ---------------- BACKEND ----------------
        self.imu = SerialManager()
        self.graphs = IMUGraphs()

        # ---------------- UI ----------------
        self.central = QtWidgets.QWidget()
        self.setCentralWidget(self.central)

        self.layout = QtWidgets.QHBoxLayout(self.central)

        # Left panel (values)
        self.panel = QtWidgets.QVBoxLayout()

        self.labels = {}

        for key in ["ax","ay","az","gx","gy","gz","temp","roll","pitch","yaw"]:
            lbl = QtWidgets.QLabel(f"{key}: 0")
            lbl.setFont(QtGui.QFont("Consolas", 12))
            self.panel.addWidget(lbl)
            self.labels[key] = lbl

        self.freq_label = QtWidgets.QLabel("Hz: 0")
        self.freq_label.setFont(QtGui.QFont("Consolas", 12))
        self.panel.addWidget(self.freq_label)
        self.cube3d = IMUCube3D()
        self.cube3d.attach(self.imu)
        # Buttons
        self.btn_connect = QtWidgets.QPushButton("Auto Connect")
        self.btn_start = QtWidgets.QPushButton("Start")
        self.btn_stop = QtWidgets.QPushButton("Stop")

        self.panel.addWidget(self.btn_connect)
        self.panel.addWidget(self.btn_start)
        self.panel.addWidget(self.btn_stop)

        self.panel.addStretch()

        # Right side (cube 3D + graphs)
        self.layout.addLayout(self.panel, 1)
        self.layout.addWidget(self.cube3d.view, 3)
        self.layout.addWidget(self.graphs.win, 4)

        # ---------------- EVENTS ----------------
        self.btn_connect.clicked.connect(self.connect_imu)
        self.btn_start.clicked.connect(self.start_stream)
        self.btn_stop.clicked.connect(self.stop_stream)

        # Timer UI update
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(30)

        # Attach graphs
        self.graphs.attach(self.imu)

    # -----------------------------------------------------

    def connect_imu(self):
        ok = self.imu.auto_connect()
        if ok:
            print("IMU connecté")
        else:
            print("Aucun port détecté")

    # -----------------------------------------------------

    def start_stream(self):
        try:
            self.imu.start()
        except Exception as e:
            print("Erreur start:", e)

    # -----------------------------------------------------

    def stop_stream(self):
        self.imu.disconnect()

    # -----------------------------------------------------

    def update_ui(self):

        data = self.imu.get_data()

        for k, v in data.items():
            if k in self.labels:
                self.labels[k].setText(f"{k}: {v:.3f}")

        self.freq_label.setText(f"Hz: {self.imu.get_frequency():.1f}")

        self.graphs.update()
        self.cube3d.update()

# ---------------------------------------------------------

def main():

    app = QtWidgets.QApplication(sys.argv)

    window = IMUDashboard()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
