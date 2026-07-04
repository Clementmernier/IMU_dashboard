import numpy as np
import pyqtgraph.opengl as gl
from PyQt5 import QtCore


class IMUCube3D:

    def __init__(self):

        # ---------------- WINDOW ----------------
        self.view = gl.GLViewWidget()
        self.view.setWindowTitle("IMU 3D Orientation")
        self.view.setCameraPosition(distance=5)

        self.view.setBackgroundColor("#0d0f14")

        # ---------------- GRID ----------------
        grid = gl.GLGridItem()
        grid.scale(1, 1, 1)
        self.view.addItem(grid)

        # ---------------- CUBE ----------------
        self.cube = self.create_cube()
        self.view.addItem(self.cube)

        # NOTE: pas de self.view.show() ici, la vue est intégrée
        # dans le layout du dashboard principal (voir main.py)

        # angles
        self.roll = 0
        self.pitch = 0
        self.yaw = 0

    # -----------------------------------------------------

    def create_cube(self):

        # 8 points cube
        verts = np.array([
            [-1, -1, -1],
            [ 1, -1, -1],
            [ 1,  1, -1],
            [-1,  1, -1],
            [-1, -1,  1],
            [ 1, -1,  1],
            [ 1,  1,  1],
            [-1,  1,  1],
        ])

        faces = np.array([
            [0,1,2], [0,2,3],  # bottom
            [4,5,6], [4,6,7],  # top
            [0,1,5], [0,5,4],  # front
            [2,3,7], [2,7,6],  # back
            [1,2,6], [1,6,5],  # right
            [0,3,7], [0,7,4],  # left
        ])

        colors = np.array([
            [1,0,0,0.6],
            [0,1,0,0.6],
            [0,0,1,0.6],
            [1,1,0,0.6],
            [1,0,1,0.6],
            [0,1,1,0.6],
        ])

        return gl.GLMeshItem(
            vertexes=verts,
            faces=faces,
            faceColors=colors,
            smooth=False,
            drawEdges=True,
            edgeColor=(1,1,1,0.2)
        )

    # -----------------------------------------------------

    def set_angles(self, roll, pitch, yaw):

        self.roll = np.radians(roll)
        self.pitch = np.radians(pitch)
        self.yaw = np.radians(yaw)

    # -----------------------------------------------------

    def update(self):

        # apply rotation (Yaw-Pitch-Roll, ordre appliqué via rotate() successifs)
        self.cube.resetTransform()

        self.cube.rotate(np.degrees(self.yaw), 0, 0, 1)
        self.cube.rotate(np.degrees(self.pitch), 0, 1, 0)
        self.cube.rotate(np.degrees(self.roll), 1, 0, 0)

    # -----------------------------------------------------

    def attach(self, serial_manager):

        def callback(data):
            self.set_angles(
                data["roll"],
                data["pitch"],
                data["yaw"]
            )

        serial_manager.add_callback(callback)
