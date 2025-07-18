# --------------------------------------------
# main.py
# Script principal para simular silenciadores tipo splitter
# --------------------------------------------

import numpy as np
import os
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

def main():
    # Parámetros de entrada
    Q_m3h = 10000
    V = 12
    H = 0.3
    fmin, fmax = 100, 500
    L = 1.7
    material = 'lana100'

    # Cálculos
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

    # Simulación
    splitter = SplitterSilencer(L, width, n_baffles, alpha_interp)
    TL = splitter.transmission_loss(freq)
    delta_L = splitter.delta_L(freq)
    TL_total = TL + delta_L

    # Gráfica
    graph_path = os.path.join(PLOTS_DIR, "TL_vs_freq.png")
    plot_attenuation_curves(freq, TL, delta_L, TL_total, graph_path)

    img_path = os.path.join(MODELS_DIR, "modelo_3d.png")
    html_path = os.path.join(MODELS_DIR, "modelo_3d.html")
    generate_3d_model(width, H, L, n_baffles, gap=h + 0.02, img_path=img_path, html_path=html_path)

    pdf_path = os.path.join(PDF_DIR, "reporte_silenciador.pdf")
    export_pdf(S, h, n_espacios, n_baffles, width, img_path, graph_path, pdf_path)


if __name__ == '__main__':
    main()
