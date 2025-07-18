# --------------------------------------------
# gui_main.py
# Aplicación principal con GUI basada en PyQt5
# --------------------------------------------

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from gui_interface import GUIInterface
from app.simulation.solver import calcular_parametros
from app.simulation.models import SplitterSilencer
from app.plotting.plots import plot_attenuation_curves
from app.plotting.graphics import generate_3d_model
from app.plotting.docs import export_pdf

OUTPUT_DIR = "outputs"
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")
PDF_DIR = os.path.join(OUTPUT_DIR, "pdf")
os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

# --------------------------------------------
# Clase principal de la aplicación GUI
# --------------------------------------------
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Silenciadores Tipo Splitter")
        self.setGeometry(100, 100, 1400, 800)
        self.interface = GUIInterface(self.simular, self.actualizar_modelo_3d)
        self.setCentralWidget(self.interface)
        self.data = {}
        self.show_dims = True

    # --------------------------------------------
    # Ejecuta la simulación y actualiza la GUI
    # --------------------------------------------
    def simular(self):
        # Lee parámetros desde la interfaz
        Q_m3h = self.interface.input_Q.value()
        V = self.interface.input_V.value()
        H = self.interface.input_H.value()
        L = self.interface.input_L.value()
        material = self.interface.input_material.currentText()
        fmin, fmax = 100, 500

        # Calcula parámetros geométricos y acústicos
        params = calcular_parametros(Q_m3h, V, H, fmin, fmax, L, material)
        splitter = SplitterSilencer(params["L"], params["width"], params["n_baffles"], params["alpha_interp"])
        TL = splitter.transmission_loss(params["freq"])
        delta_L = splitter.delta_L(params["freq"])
        TL_total = TL + delta_L

        # Guarda los datos para exportar/modelar
        self.data = {
            **params,
            "TL": TL, "delta_L": delta_L, "TL_total": TL_total,
            "img_path": os.path.join(MODELS_DIR, "modelo_3d.png"),
            "graph_path": os.path.join(PLOTS_DIR, "TL_vs_freq.png"),
            "pdf_path": os.path.join(PDF_DIR, "reporte_silenciador.pdf"),
        }

        # Actualiza la gráfica en la GUI
        self.interface.update_plot(params["freq"], TL, delta_L, TL_total)

        # Actualiza el resumen textual
        resumen = (
            f"Caudal: {Q_m3h} m³/h\n"
            f"Velocidad: {V} m/s\n"
            f"Altura: {H} m\n"
            f"Longitud: {L} m\n"
            f"Material: {material}\n"
            f"Área requerida: {params['S']:.4f} m²\n"
            f"Separación entre baffles (2h): {2*params['h']:.4f} m\n"
            f"Número de rendijas: {params['n_espacios']}\n"
            f"Total de baffles: {params['n_baffles']}\n"
            f"Ancho total estimado: {params['width']:.4f} m"
        )
        self.interface.update_summary(resumen)

        # Parámetros para el modelo 3D
        baffle_thickness = 0.02
        gap = params['h'] + 0.02
        n_baffles = params['n_baffles']
        n_espacios = params['n_espacios']
        rendija_ancho = params['h']
        summary_3d = (
            f"Dimensiones del silenciador:\n"
            f"- Largo total (L): {params['L']:.2f} m\n"
            f"- Altura total (a): {params['H']:.2f} m\n"
            f"- Ancho total (b): {params['width']:.2f} m\n"
            f"- Número de baffles: {n_baffles}\n"
            f"- Espesor de cada baffle: {baffle_thickness:.2f} m\n"
            f"- Separación entre baffles (gap): {gap:.2f} m\n"
            f"- Ancho de cada rendija: {rendija_ancho:.2f} m\n"
            f"- Número de rendijas: {n_espacios}\n"
        )
        self.interface.update_3d_summary(summary_3d)

        # Actualiza el modelo 3D
        self.actualizar_modelo_3d('update')

    # --------------------------------------------
    # Actualiza el modelo 3D interactivo según controles
    # --------------------------------------------
    def actualizar_modelo_3d(self, action):
        if not self.data:
            return
        viewer = self.interface.viewer
        viewer.clear()
        # Genera el modelo 3D en el viewer embebido, pasando el color seleccionado
        generate_3d_model(
            self.data["L"], self.data["width"], self.data["H"], self.data["n_baffles"],
            gap=self.data["h"] + 0.02, show_dims=self.show_dims, plotter=viewer,
            baffle_color=self.interface.baffle_color
        )
        # Control de cámara
        if action == 'front':
            viewer.view_xy()
        elif action == 'side':
            viewer.view_yz()
        elif action == 'iso':
            viewer.view_isometric()
        elif action == 'dims':
            self.show_dims = self.interface.chk_show_dims.isChecked()
            self.actualizar_modelo_3d('update')
        elif action == 'update':
            # Vista por defecto: isométrica
            viewer.view_isometric()

    # --------------------------------------------
    # Exporta el reporte PDF (puedes agregar un botón para esto)
    # --------------------------------------------
    def exportar_pdf(self):
        if not self.data:
            QMessageBox.warning(self, "Advertencia", "Primero realiza una simulación.")
            return
        plot_attenuation_curves(
            self.data["freq"], self.data["TL"], self.data["delta_L"], self.data["TL_total"], self.data["graph_path"]
        )
        generate_3d_model(
            self.data["L"], self.data["width"], self.data["H"], self.data["n_baffles"],
            gap=self.data["h"] + 0.02, show_dims=True, img_path=self.data["img_path"]
        )
        export_pdf(
            self.data["S"], self.data["h"], self.data["n_espacios"], self.data["n_baffles"], self.data["width"],
            self.data["img_path"], self.data["graph_path"], self.data["pdf_path"]
        )
        QMessageBox.information(self, "Éxito", f"PDF exportado en:\n{self.data['pdf_path']}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
