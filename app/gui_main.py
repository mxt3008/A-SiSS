# gui_main.py
# Aplicación principal con GUI basada en PyQt5

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow
from gui_interface import GUIInterface
from app.simulation.models import SplitterSilencer
from app.plotting.docs import export_pdf
from app.plotting.graphics import generate_3d_model  # NUEVO

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Silenciadores Tipo Splitter")
        self.setGeometry(100, 100, 1400, 800)

        self.interface = GUIInterface(self.simular, self.exportar_pdf, self.mostrar_modelo_3d)  # 3er callback
        self.setCentralWidget(self.interface)
        self.data = {}

    def simular(self):
        Q_m3h = 10000
        V = 12
        H = 0.3
        fmin, fmax = 100, 500
        L = 1.7
        material = 'lana100'

        Q = Q_m3h / 3600
        c = 343
        h = (c / fmax) / 8 / 2
        a = H
        S = Q / V
        n_espacios = int(np.floor(S / (a * 2 * h)))
        n_baffles = n_espacios + 1
        width = n_espacios * h + n_baffles * 0.02
        freq = np.linspace(fmin, fmax, 300)

        freqs_material = np.array([125, 250, 500])
        alphas_dict = {
            'lana50': np.array([0.19, 0.43, 0.77]),
            'lana70': np.array([0.33, 0.65, 0.88]),
            'lana100': np.array([0.54, 0.87, 1.00])
        }
        alpha_interp = np.interp(freq, freqs_material, alphas_dict[material])

        splitter = SplitterSilencer(L, width, n_baffles, alpha_interp)
        TL = splitter.transmission_loss(freq)
        delta_L = splitter.delta_L(freq)
        TL_total = TL + delta_L

        # Guardar para PDF y modelo
        self.data = {
            "S": S,
            "h": h,
            "n_espacios": n_espacios,
            "n_baffles": n_baffles,
            "width": width,
            "L": L,
            "H": H,
            "gap": h,
            "freq": freq,
            "TL": TL,
            "delta_L": delta_L,
            "TL_total": TL_total
        }

        self.interface.update_plot(freq, TL, delta_L, TL_total)

    def exportar_pdf(self):
        if not self.data:
            return

        S = self.data["S"]
        h = self.data["h"]
        n_espacios = self.data["n_espacios"]
        n_baffles = self.data["n_baffles"]
        width = self.data["width"]
        freq = self.data["freq"]
        TL = self.data["TL"]
        delta_L = self.data["delta_L"]
        TL_total = self.data["TL_total"]

        import matplotlib.pyplot as plt
        plot_path = "TL_export.png"
        fig, ax = plt.subplots()
        ax.plot(freq, TL, label="TL(f)")
        ax.plot(freq, delta_L, label="ΔL(f)")
        ax.plot(freq, TL_total, label="Total")
        ax.legend()
        ax.set_xlabel("Frecuencia [Hz]")
        ax.set_ylabel("Atenuación [dB]")
        ax.grid(True)
        plt.savefig(plot_path, dpi=300)
        plt.close()

        screenshot_path = "modelo_temp.png"
        self.interface.viewer.screenshot(screenshot_path)

        export_pdf(S, h, n_espacios, n_baffles, width, screenshot_path, plot_path)

    def mostrar_modelo_3d(self):
        if not self.data:
            return
        generate_3d_model(
            length=self.data["L"],
            width=self.data["width"],
            height=self.data["H"],
            n_baffles=self.data["n_baffles"],
            gap=self.data["gap"]
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
