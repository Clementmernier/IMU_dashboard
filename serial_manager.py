import serial
import serial.tools.list_ports
import threading
import time


class SerialManager:

    def __init__(self, baudrate=115200):
        self.baudrate = baudrate

        self.serial = None
        self.running = False
        self.thread = None

        self.data = {
            "ax": 0,
            "ay": 0,
            "az": 0,

            "gx": 0,
            "gy": 0,
            "gz": 0,

            "temp": 0,

            "roll": 0,
            "pitch": 0,
            "yaw": 0
        }

        self.callbacks = []

        self.frequency = 0

    ##########################################################

    def available_ports(self):
        return list(serial.tools.list_ports.comports())

    ##########################################################

    def auto_connect(self):

        ports = self.available_ports()

        for port in ports:

            try:

                ser = serial.Serial(
                    port.device,
                    self.baudrate,
                    timeout=1
                )

                time.sleep(2)

                self.serial = ser

                print(f"Connecté à {port.device}")

                return True

            except:

                pass

        return False

    ##########################################################

    def connect(self, port):

        self.serial = serial.Serial(
            port,
            self.baudrate,
            timeout=1
        )

        time.sleep(2)

        return True

    ##########################################################

    def disconnect(self):

        self.running = False

        if self.thread is not None:
            self.thread.join()

        if self.serial is not None:
            self.serial.close()

    ##########################################################

    def start(self):

        if self.serial is None:
            raise Exception("Aucun port série connecté.")

        self.running = True

        self.thread = threading.Thread(
            target=self.read_loop,
            daemon=True
        )

        self.thread.start()

    ##########################################################

    def add_callback(self, callback):

        self.callbacks.append(callback)

    ##########################################################

    def read_loop(self):

        counter = 0
        timer = time.time()

        while self.running:

            try:

                line = self.serial.readline().decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                if not line:
                    continue

                if line.startswith("AX"):
                    continue

                values = line.split(",")

                if len(values) != 10:
                    continue

                self.data["ax"] = float(values[0])
                self.data["ay"] = float(values[1])
                self.data["az"] = float(values[2])

                self.data["gx"] = float(values[3])
                self.data["gy"] = float(values[4])
                self.data["gz"] = float(values[5])

                self.data["temp"] = float(values[6])

                self.data["roll"] = float(values[7])
                self.data["pitch"] = float(values[8])
                self.data["yaw"] = float(values[9])

                counter += 1

                elapsed = time.time() - timer

                if elapsed >= 1:

                    self.frequency = counter / elapsed

                    counter = 0
                    timer = time.time()

                for callback in self.callbacks:

                    callback(self.data)

            except Exception:

                pass

    ##########################################################

    def get_data(self):

        return self.data.copy()

    ##########################################################

    def get_frequency(self):

        return self.frequency

    ##########################################################

    def send(self, text):

        if self.serial is None:
            return

        self.serial.write((text + "\n").encode())

    ##########################################################

    def is_connected(self):

        return self.serial is not None and self.serial.is_open
