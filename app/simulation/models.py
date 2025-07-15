# --------------------------------------------
# models.py
# 
# --------------------------------------------

from app.acoustics import lined_wall_impedance, wavenumber_complex
import numpy as np

class SplitterSilencer:
    def __init__(self, length, width, n_splitters, absorption):
        self.length = length
        self.width = width
        self.n_splitters = n_splitters
        self.absorption = absorption

        self.splitter_width = width / (n_splitters + 1)

    def transmission_loss(self, freq):
        """
        Calcula la pérdida por transmisión (TL) en dB para un rango de frecuencias
        usando una aproximación de propagación en modo plano y pérdidas por absorción.
        """
        c = 343  # velocidad del sonido [m/s]
        rho0 = 1.21  # densidad del aire [kg/m^3]

        k = wavenumber_complex(freq, self.absorption)
        Zc = rho0 * c  # impedancia característica

        TL = []

        for f, ki in zip(freq, k):
            # Modelo simplificado tipo ducto + splitter:
            # Atenuación = función de la longitud, número de splitters, pérdidas
            alpha = 4 * self.absorption / (self.splitter_width)
            TLf = 10 * np.log10(np.exp(2 * alpha * self.length))  # fórmula empírica
            TL.append(TLf)

        return np.array(TL)
