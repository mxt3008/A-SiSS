# --------------------------------------------
# acoustics.py
# Funciones acústicas auxiliares para simulación de silenciadores
# --------------------------------------------

import numpy as np

def wavenumber_complex(freq, absorption_coeff, c=343):
    """
    Devuelve el número de onda complejo (modo plano) para modelar pérdidas por absorción.
    """
    omega = 2 * np.pi * freq
    alpha = absorption_coeff  # puede ser array o escalar
    return omega / c * (1 + 1j * alpha)

def lined_wall_impedance(absorption_coeff, rho0=1.21, c=343):
    """
    Calcula impedancia superficial aproximada de un revestimiento absorbente
    en función de su coeficiente de absorción.
    """
    R = (1 - absorption_coeff) / (1 + absorption_coeff)
    Zs = rho0 * c * (1 + R) / (1 - R)
    return Zs

def delta_L_additional(alpha, a, h):
    """
    Calcula la atenuación adicional ΔL por rendijas, según fórmula:
    ΔL(f) = 1.05 * α(f)^1.4 * (P/S)
    Donde:
    - P = 2(a + 2h)
    - S = a * 2h
    """
    P = 2 * (a + 2 * h)
    S = a * 2 * h
    deltaL = 1.05 * (alpha ** 1.4) * (P / S)
    return deltaL
