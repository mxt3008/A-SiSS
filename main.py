# --------------------------------------------
# main.py
# Script principal para simular silenciadores acústicos.
# --------------------------------------------

from app.models import SplitterSilencer
import matplotlib.pyplot as plt
import numpy as np

def main():
    # Definir parámetros básicos
    freq = np.linspace(20, 5000, 1000)  # Hz
    length = 1.5   # metros
    width = 0.5    # ancho total del ducto
    n_splitters = 2
    absorption = 0.6  # coef. de absorción típico

    # Crear el modelo de silenciador tipo splitter
    splitter = SplitterSilencer(
        length=length,
        width=width,
        n_splitters=n_splitters,
        absorption=absorption
    )

    # Calcular la atenuación (Transmission Loss)
    TL = splitter.transmission_loss(freq)

    # Graficar resultado
    plt.plot(freq, TL)
    plt.xlabel('Frecuencia [Hz]')
    plt.ylabel('Transmission Loss [dB]')
    plt.title('Silenciador tipo Splitter')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
