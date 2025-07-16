# --------------------------------------------
# models.py
# Modelo físico del silenciador tipo splitter
# --------------------------------------------

import numpy as np
from app.simulation.acoustics import wavenumber_complex, delta_L_additional

class SplitterSilencer:
    def __init__(self, length, width, n_splitters, absorption):
        self.length = length
        self.width = width
        self.n_splitters = n_splitters
        self.absorption = absorption
        self.splitter_width = width / (n_splitters + 1)

    def transmission_loss(self, freq):
        c = 343
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

    def total_attenuation(self, freq):
        TL = self.transmission_loss(freq)
        ΔL = self.delta_L(freq)
        return TL + ΔL
