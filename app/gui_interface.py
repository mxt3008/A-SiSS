# --------------------------------------------
# gui_interface.py
# Interfaz gráfica principal del simulador tipo splitter
# --------------------------------------------

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QLabel,
    QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit, QCheckBox, QColorDialog
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pyvistaqt import QtInteractor

# --------------------------------------------
# Clase de la interfaz gráfica principal
# --------------------------------------------
class GUIInterface(QWidget):
    def __init__(self, simulate_callback, update_3d_callback):
        super().__init__()
        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        # Panel izquierdo (30%)
        left_panel = QVBoxLayout()
        # Panel superior: formulario de parámetros
        form = QFormLayout()
        self.input_Q = QSpinBox(); self.input_Q.setRange(100, 100000); self.input_Q.setValue(10000)
        self.input_V = QDoubleSpinBox(); self.input_V.setRange(1, 100); self.input_V.setValue(12)
        self.input_H = QDoubleSpinBox(); self.input_H.setRange(0.1, 2); self.input_H.setValue(0.3)
        self.input_L = QDoubleSpinBox(); self.input_L.setRange(0.5, 10); self.input_L.setValue(1.7)
        self.input_material = QComboBox(); self.input_material.addItems(['lana50', 'lana70', 'lana100'])
        form.addRow("Caudal [m3/h]:", self.input_Q)
        form.addRow("Velocidad [m/s]:", self.input_V)
        form.addRow("Altura [m]:", self.input_H)
        form.addRow("Longitud [m]:", self.input_L)
        form.addRow("Material:", self.input_material)
        # Selector de color
        self.baffle_color = "#FFD700"  # Amarillo por defecto
        self.btn_color = QPushButton("Color de baffles")
        self.btn_color.setStyleSheet(f"background-color: {self.baffle_color}")
        form.addRow("Color de baffles:", self.btn_color)
        self.btn_color.clicked.connect(self.select_baffle_color)
        self.btn_simulate = QPushButton("Simular")
        form.addRow(self.btn_simulate)
        left_panel.addLayout(form)
        # Panel inferior: resumen textual
        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        left_panel.addWidget(QLabel("Resumen de parámetros y resultados:"))
        left_panel.addWidget(self.summary_box)
        main_layout.addLayout(left_panel, 3)  # 30%

        # Panel derecho (70%)
        right_panel = QVBoxLayout()
        self.tabs = QTabWidget()
        # Pestaña 1: Gráfica
        self.plot_canvas = FigureCanvas(Figure())
        self.tabs.addTab(self.plot_canvas, "Gráfica")
        # Pestaña 2: Modelo 3D
        self.viewer = QtInteractor(self)
        controls_layout = QHBoxLayout()
        self.btn_front = QPushButton("Vista Frontal")
        self.btn_side = QPushButton("Vista Lateral")
        self.btn_iso = QPushButton("Vista Isométrica")
        self.chk_show_dims = QCheckBox("Mostrar medidas")
        self.chk_show_dims.setChecked(True)
        controls_layout.addWidget(self.btn_front)
        controls_layout.addWidget(self.btn_side)
        controls_layout.addWidget(self.btn_iso)
        controls_layout.addWidget(self.chk_show_dims)
        model3d_widget = QWidget()
        model3d_layout = QVBoxLayout(model3d_widget)
        model3d_layout.addLayout(controls_layout)
        model3d_layout.addWidget(self.viewer.interactor)
        # Cuadro de texto para resumen en 3D
        self.summary_3d_box = QTextEdit()
        self.summary_3d_box.setReadOnly(True)
        model3d_layout.addWidget(self.summary_3d_box)
        self.tabs.addTab(model3d_widget, "Modelo 3D")
        right_panel.addWidget(self.tabs)
        main_layout.addLayout(right_panel, 7)  # 70%

        self.setLayout(main_layout)

        # Conectar botones a callbacks
        self.btn_simulate.clicked.connect(simulate_callback)
        self.btn_front.clicked.connect(lambda: update_3d_callback('front'))
        self.btn_side.clicked.connect(lambda: update_3d_callback('side'))
        self.btn_iso.clicked.connect(lambda: update_3d_callback('iso'))
        self.chk_show_dims.stateChanged.connect(lambda: update_3d_callback('dims'))

    # --------------------------------------------
    # Selector de color para los baffles
    # --------------------------------------------
    def select_baffle_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.baffle_color = color.name()
            self.btn_color.setStyleSheet(f"background-color: {self.baffle_color}")
            # Llama a la actualización del modelo 3D para reflejar el color en tiempo real
            self.parent().actualizar_modelo_3d('update')

    # --------------------------------------------
    # Actualiza la gráfica en la pestaña correspondiente
    # --------------------------------------------
    def update_plot(self, freq, TL, delta_L, TL_total):
        fig = self.plot_canvas.figure
        fig.clear()
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        ax1.plot(freq, TL, label='TL(f)', color='tab:blue')
        ax2.plot(freq, delta_L, label='ΔL(f)', color='tab:red', linestyle='--')
        ax1.plot(freq, TL_total, label='Atenuación total', color='tab:green', linewidth=2)
        ax1.set_xlabel("Frecuencia [Hz]")
        ax1.set_ylabel("Transmission Loss TL [dB]", color='tab:blue')
        ax2.set_ylabel("Atenuación adicional ΔL [dB]", color='tab:red')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        ax2.tick_params(axis='y', labelcolor='tab:red')
        fig.legend(loc='upper right')
        fig.tight_layout()
        self.plot_canvas.draw()

    # --------------------------------------------
    # Actualiza el resumen textual de parámetros/resultados
    # --------------------------------------------
    def update_summary(self, summary_text):
        self.summary_box.setPlainText(summary_text)

    # --------------------------------------------
    # Actualiza el resumen en la pestaña de modelo 3D
    # --------------------------------------------
    def update_3d_summary(self, text):
        self.summary_3d_box.setPlainText(text)
