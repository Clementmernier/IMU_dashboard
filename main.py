import os
os.environ["PYQTGRAPH_QT_LIB"] = "PyQt5"

import sys
from PyQt5 import QtWidgets, QtCore, QtGui

from viewer3d import IMUCube3D
from serial_manager import SerialManager
from graphs import IMUGraphs


# =====================================================================
#  THEME
# =====================================================================

ACCENT = "#5ee6c8"
ACCENT_DIM = "#2f7d6d"
BG_DARK = "#0d0f14"
BG_PANEL = "#141822"
BG_CARD = "#1a1f2b"
BORDER = "#252b3a"
TEXT = "#e6e9f0"
TEXT_DIM = "#7b8496"
DANGER = "#e65e5e"

STYLE_SHEET = f"""
QMainWindow {{
    background-color: {BG_DARK};
}}

QWidget#sidebar {{
    background-color: {BG_PANEL};
    border-right: 1px solid {BORDER};
}}

QLabel {{
    color: {TEXT};
}}

QLabel#appTitle {{
    color: {TEXT};
    font-size: 16px;
    font-weight: 600;
}}

QLabel#appSubtitle {{
    color: {TEXT_DIM};
    font-size: 11px;
}}

QLabel#sectionLabel {{
    color: {TEXT_DIM};
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
}}

QFrame#card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

QLabel.metricName {{
    color: {TEXT_DIM};
    font-size: 11px;
}}

QLabel.metricValue {{
    color: {TEXT};
    font-size: 15px;
    font-weight: 600;
}}

QComboBox {{
    background-color: {BG_CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    color: {TEXT};
    selection-background-color: {ACCENT_DIM};
    border: 1px solid {BORDER};
}}

QPushButton {{
    background-color: {BG_CARD};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 12px;
    font-weight: 500;
}}

QPushButton:hover {{
    border: 1px solid {ACCENT_DIM};
}}

QPushButton:pressed {{
    background-color: {ACCENT_DIM};
}}

QPushButton#primaryBtn {{
    background-color: {ACCENT};
    color: #0d0f14;
    border: none;
    font-weight: 600;
}}

QPushButton#primaryBtn:hover {{
    background-color: #7cf0d6;
}}

QPushButton#stopBtn {{
    color: {DANGER};
}}

QPushButton#stopBtn:hover {{
    border: 1px solid {DANGER};
}}

QFrame#headerBar {{
    background-color: {BG_PANEL};
    border-bottom: 1px solid {BORDER};
}}

QFrame#freqBadge {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
"""


# =====================================================================
#  SMALL REUSABLE WIDGETS
# =====================================================================

class StatusDot(QtWidgets.QLabel):
    """Petit indicateur circulaire coloré (connecté / déconnecté / actif)."""

    def __init__(self, color=DANGER, size=10):
        super().__init__()
        self._size = size
        self.setFixedSize(size, size)
        self.set_color(color)

    def set_color(self, color):
        self.setStyleSheet(
            f"background-color: {color}; border-radius: {self._size // 2}px;"
        )


class MetricCard(QtWidgets.QFrame):
    """Carte regroupant plusieurs valeurs numériques liées (accel, gyro...)."""

    def __init__(self, title, metric_keys, unit=""):
        super().__init__()
        self.setObjectName("card")

        self.value_labels = {}

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        title_label = QtWidgets.QLabel(title.upper())
        title_label.setObjectName("sectionLabel")
        layout.addWidget(title_label)

        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(4)

        for i, key in enumerate(metric_keys):
            name_lbl = QtWidgets.QLabel(key.upper())
            name_lbl.setProperty("class", "metricName")
            name_lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px;")

            value_lbl = QtWidgets.QLabel(f"0.00{unit}")
            value_lbl.setStyleSheet(
                f"color: {TEXT}; font-size: 15px; font-weight: 600;"
            )
            value_lbl.setFont(QtGui.QFont("Consolas", 12))

            grid.addWidget(name_lbl, 0, i)
            grid.addWidget(value_lbl, 1, i)

            self.value_labels[key] = value_lbl

        layout.addLayout(grid)
        self.unit = unit

    def update_value(self, key, value):
        if key in self.value_labels:
            self.value_labels[key].setText(f"{value:.2f}{self.unit}")


# =====================================================================
#  MAIN DASHBOARD
# =====================================================================

class IMUDashboard(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ESP32 MPU6050 · IMU Dashboard")
        self.resize(1500, 850)
        self.setStyleSheet(STYLE_SHEET)

        # ---------------- BACKEND ----------------
        self.imu = SerialManager()
        self.graphs = IMUGraphs()
        self.cube3d = IMUCube3D()
        self.cube3d.attach(self.imu)
        self.graphs.attach(self.imu)

        # ---------------- ROOT LAYOUT ----------------
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        root = QtWidgets.QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self.build_header())

        body = QtWidgets.QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        body.addWidget(self.build_sidebar(), 0)
        body.addWidget(self.cube3d.view, 3)
        body.addWidget(self.graphs.win, 4)

        root.addLayout(body)

        # ---------------- TIMER ----------------
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(30)

        self.refresh_ports()

    # -----------------------------------------------------
    #  HEADER
    # -----------------------------------------------------

    def build_header(self):
        header = QtWidgets.QFrame()
        header.setObjectName("headerBar")
        header.setFixedHeight(56)

        layout = QtWidgets.QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)

        title_box = QtWidgets.QVBoxLayout()
        title_box.setSpacing(0)
        title = QtWidgets.QLabel("IMU Dashboard")
        title.setObjectName("appTitle")
        subtitle = QtWidgets.QLabel("ESP32 · MPU6050 · Temps réel")
        subtitle.setObjectName("appSubtitle")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)

        layout.addLayout(title_box)
        layout.addStretch()

        # Connection status
        self.status_dot = StatusDot(DANGER)
        self.status_label = QtWidgets.QLabel("Déconnecté")
        self.status_label.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px;")

        status_box = QtWidgets.QHBoxLayout()
        status_box.setSpacing(8)
        status_box.addWidget(self.status_dot)
        status_box.addWidget(self.status_label)
        layout.addLayout(status_box)

        layout.addSpacing(24)

        # Frequency badge
        freq_badge = QtWidgets.QFrame()
        freq_badge.setObjectName("freqBadge")
        freq_layout = QtWidgets.QHBoxLayout(freq_badge)
        freq_layout.setContentsMargins(12, 6, 12, 6)

        self.freq_value = QtWidgets.QLabel("0.0 Hz")
        self.freq_value.setFont(QtGui.QFont("Consolas", 11))
        self.freq_value.setStyleSheet(f"color: {ACCENT}; font-weight: 600;")
        freq_layout.addWidget(self.freq_value)

        layout.addWidget(freq_badge)

        return header

    # -----------------------------------------------------
    #  SIDEBAR
    # -----------------------------------------------------

    def build_sidebar(self):
        sidebar = QtWidgets.QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(300)

        layout = QtWidgets.QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # --- Connexion ---
        conn_label = QtWidgets.QLabel("CONNEXION")
        conn_label.setObjectName("sectionLabel")
        layout.addWidget(conn_label)

        self.port_combo = QtWidgets.QComboBox()
        layout.addWidget(self.port_combo)

        port_btns = QtWidgets.QHBoxLayout()
        self.btn_refresh = QtWidgets.QPushButton("⟳ Rafraîchir")
        self.btn_connect = QtWidgets.QPushButton("Connecter")
        self.btn_connect.setObjectName("primaryBtn")
        port_btns.addWidget(self.btn_refresh)
        port_btns.addWidget(self.btn_connect)
        layout.addLayout(port_btns)

        stream_btns = QtWidgets.QHBoxLayout()
        self.btn_start = QtWidgets.QPushButton("▶ Start")
        self.btn_stop = QtWidgets.QPushButton("■ Stop")
        self.btn_stop.setObjectName("stopBtn")
        stream_btns.addWidget(self.btn_start)
        stream_btns.addWidget(self.btn_stop)
        layout.addLayout(stream_btns)

        layout.addSpacing(8)

        # --- Cartes de données ---
        data_label = QtWidgets.QLabel("DONNÉES CAPTEURS")
        data_label.setObjectName("sectionLabel")
        layout.addWidget(data_label)

        self.card_accel = MetricCard("Accéléromètre", ["ax", "ay", "az"], unit=" g")
        self.card_gyro = MetricCard("Gyroscope", ["gx", "gy", "gz"], unit="°/s")
        self.card_orient = MetricCard("Orientation", ["roll", "pitch", "yaw"], unit="°")
        self.card_temp = MetricCard("Température", ["temp"], unit=" °C")

        layout.addWidget(self.card_accel)
        layout.addWidget(self.card_gyro)
        layout.addWidget(self.card_orient)
        layout.addWidget(self.card_temp)

        layout.addStretch()

        # --- Events ---
        self.btn_refresh.clicked.connect(self.refresh_ports)
        self.btn_connect.clicked.connect(self.connect_imu)
        self.btn_start.clicked.connect(self.start_stream)
        self.btn_stop.clicked.connect(self.stop_stream)

        return sidebar

    # -----------------------------------------------------
    #  PORTS
    # -----------------------------------------------------

    def refresh_ports(self):
        self.port_combo.clear()
        ports = self.imu.available_ports()

        if not ports:
            self.port_combo.addItem("Aucun port détecté")
            return

        for port in ports:
            self.port_combo.addItem(port.device)

    # -----------------------------------------------------
    #  ACTIONS
    # -----------------------------------------------------

    def connect_imu(self):
        selected = self.port_combo.currentText()

        try:
            if selected and "Aucun" not in selected:
                ok = self.imu.connect(selected)
            else:
                ok = self.imu.auto_connect()
        except Exception as e:
            ok = False
            print("Erreur connexion:", e)

        if ok:
            self.status_dot.set_color(ACCENT)
            self.status_label.setText(f"Connecté · {self.port_combo.currentText()}")
        else:
            self.status_dot.set_color(DANGER)
            self.status_label.setText("Échec de connexion")

    def start_stream(self):
        try:
            self.imu.start()
            self.status_dot.set_color(ACCENT)
        except Exception as e:
            print("Erreur start:", e)
            self.status_label.setText("Erreur au démarrage")

    def stop_stream(self):
        self.imu.disconnect()
        self.status_dot.set_color(DANGER)
        self.status_label.setText("Déconnecté")

    # -----------------------------------------------------
    #  UI REFRESH LOOP
    # -----------------------------------------------------

    def update_ui(self):
        data = self.imu.get_data()

        self.card_accel.update_value("ax", data["ax"])
        self.card_accel.update_value("ay", data["ay"])
        self.card_accel.update_value("az", data["az"])

        self.card_gyro.update_value("gx", data["gx"])
        self.card_gyro.update_value("gy", data["gy"])
        self.card_gyro.update_value("gz", data["gz"])

        self.card_orient.update_value("roll", data["roll"])
        self.card_orient.update_value("pitch", data["pitch"])
        self.card_orient.update_value("yaw", data["yaw"])

        self.card_temp.update_value("temp", data["temp"])

        self.freq_value.setText(f"{self.imu.get_frequency():.1f} Hz")

        self.graphs.update()
        self.cube3d.update()


# =====================================================================

def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    window = IMUDashboard()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
