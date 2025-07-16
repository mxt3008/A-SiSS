# gui_interface.py
# Interfaz gráfica modular del simulador con PyQt5

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pyvistaqt import QtInteractor


class GUIInterface(QWidget):
    def __init__(self, simulate_callback, export_callback, model3d_callback):
        super().__init__()
        self.simulate_callback = simulate_callback
        self.export_callback = export_callback
        self.model3d_callback = model3d_callback  # Nuevo callback

        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # Panel de controles
        controls = QVBoxLayout()
        self.label_info = QLabel("Simulador de silenciadores tipo splitter")
        controls.addWidget(self.label_info)

        self.btn_simulate = QPushButton("Simular")
        self.btn_simulate.clicked.connect(self.simulate_callback)
        controls.addWidget(self.btn_simulate)

        self.btn_export = QPushButton("Exportar PDF")
        self.btn_export.clicked.connect(self.export_callback)
        controls.addWidget(self.btn_export)

        # Botón para mostrar modelo 3D
        self.btn_model3d = QPushButton("Mostrar modelo 3D")
        self.btn_model3d.clicked.connect(self.model3d_callback)
        controls.addWidget(self.btn_model3d)

        main_layout.addLayout(controls, 1)

        # Visualizador 3D
        self.viewer = QtInteractor(self)
        main_layout.addWidget(self.viewer.interactor, 2)

        # Gráfica
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas, 1)

    def update_plot(self, freq, TL, delta_L, TL_total):
        self.figure.clear()
        ax1 = self.figure.add_subplot(111)
        ax1.plot(freq, TL, label='TL(f)', color='tab:blue')
        ax1.plot(freq, delta_L, label='ΔL(f)', color='tab:red', linestyle='--')
        ax1.plot(freq, TL_total, label='Atenuación total', color='tab:green', linewidth=2)
        ax1.set_xlabel("Frecuencia [Hz]")
        ax1.set_ylabel("Atenuación [dB]")
        ax1.grid(True)
        ax1.legend()
        self.canvas.draw()
