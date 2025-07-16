# --------------------------------------------
# main.py
# Script principal para simular silenciadores acústicos tipo splitter
# --------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
from app.simulation.models import SplitterSilencer
from app.simulation.graphics import generate_3d_model, export_pdf

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

    splitter = SplitterSilencer(L, width, n_baffles, alpha_interp)
    TL = splitter.transmission_loss(freq)
    delta_L = splitter.delta_L(freq)
    TL_total = TL + delta_L

    # Gráfica con doble eje
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()

    ax1.plot(freq, TL, label='TL(f)', color='tab:blue')
    ax2.plot(freq, delta_L, label='ΔL(f)', color='tab:red', linestyle='--')
    ax1.plot(freq, TL_total, label='Atenuación total', color='tab:green', linewidth=2)

    ax1.set_xlabel("Frecuencia [Hz]")
    ax1.set_ylabel("Transmission Loss TL [dB]", color='tab:blue')
    ax2.set_ylabel("Atenuación adicional ΔL [dB]", color='tab:red')

    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax2.tick_params(axis='y', labelcolor='tab:red')
    ax1.grid(True)
    fig.tight_layout()
    fig.legend(loc='upper right')
    graph_path = "TL_vs_freq.png"
    plt.savefig(graph_path, dpi=300)
    plt.close()

    # Modelo 3D y PDF
    model_path = generate_3d_model(width, H, L, n_baffles, gap=h + 0.02)
    export_pdf(S, h, n_espacios, n_baffles, width, model_path, graph_path)
    print("✅ Reporte generado: reporte_silenciador.pdf")

if __name__ == '__main__':
    main()
