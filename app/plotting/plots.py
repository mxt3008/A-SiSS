# --------------------------------------------
# plots.py
# Gráficas 2D de la simulación acústica
# --------------------------------------------

import matplotlib.pyplot as plt

# --------------------------------------------
# Genera y guarda la curva de atenuación del silenciador
# --------------------------------------------
def plot_attenuation_curves(freq, TL, delta_L, TL_total, output_path="TL_vs_freq.png"):
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

    fig.legend(loc='upper right')
    fig.tight_layout()
    plt.savefig(output_path)
    plt.close(fig)
