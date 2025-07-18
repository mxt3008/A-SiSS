# --------------------------------------------
# models.py
# Modelo físico del silenciador tipo splitter
# --------------------------------------------

#====================================================================================================================================
#====================================================================================================================================
#====================================================================================================================================

# --------------------------------------------
# Importar librerías necesarias
# --------------------------------------------

import numpy as np
from app.simulation.acoustics import wavenumber_complex, delta_L_additional

# --------------------------------------------
# Clase para el modelo físico del silenciador tipo splitter
# --------------------------------------------
class SplitterSilencer:
    # --------------------------------------------
    # Inicializa el modelo con dimensiones y absorción
    # --------------------------------------------
    def __init__(self, length, width, n_splitters, absorption):
        self.length = length  # Longitud del silenciador [m]
        self.width = width    # Ancho total del silenciador [m]
        self.n_splitters = n_splitters  # Número de baffles
        self.absorption = absorption    # Vector de coeficiente de absorción
        self.splitter_width = width / (n_splitters + 1)  # Ancho de cada rendija

    # --------------------------------------------
    # Calcula la pérdida de transmisión (TL) en función de la frecuencia
    # --------------------------------------------
    def transmission_loss(self, freq):
        c = 343  # Velocidad del sonido en aire [m/s]
        if np.isscalar(self.absorption):
            alpha_vec = np.full_like(freq, self.absorption)
        else:
            alpha_vec = self.absorption

        k = wavenumber_complex(freq, alpha_vec)
        TL = []
        for alpha_i in alpha_vec:
            alpha = 4 * alpha_i / self.splitter_width
            TLf = 10 * np.log10(np.exp(2 * alpha * self.length))
            TL.append(TLf)
        return np.array(TL)

    # --------------------------------------------
    # Calcula la atenuación adicional por absorción lateral
    # --------------------------------------------
    def delta_L(self, freq):
        if np.isscalar(self.absorption):
            alpha_vec = np.full_like(freq, self.absorption)
        else:
            alpha_vec = self.absorption

        a = self.splitter_width
        h = a / 2
        return np.array([
            delta_L_additional(alpha_i, a, h) for alpha_i in alpha_vec
        ])

    # --------------------------------------------
    # Calcula la atenuación total (TL + ΔL)
    # --------------------------------------------
    def total_attenuation(self, freq):
        TL = self.transmission_loss(freq)
        ΔL = self.delta_L(freq)
        return TL + ΔL
