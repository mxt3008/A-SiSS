# --------------------------------------------
# acoustics.py
# 
# --------------------------------------------

import numpy as np

def wavenumber_complex(freq, absorption_coeff, c=343):
    """
    Devuelve el número de onda complejo (modo plano) para modelar pérdidas por absorción.
    """
    omega = 2 * np.pi * freq
    alpha = absorption_coeff  # Puede mejorarse con modelo de material
    return omega / c * (1 + 1j * alpha)

def lined_wall_impedance(absorption_coeff, rho0=1.21, c=343):
    """
    Calcula impedancia superficial aproximada de un revestimiento absorbente
    en función de su coeficiente de absorción.
    """
    R = (1 - absorption_coeff) / (1 + absorption_coeff)
    Zs = rho0 * c * (1 + R) / (1 - R)
    return Zs
