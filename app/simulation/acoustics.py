# --------------------------------------------
# acoustics.py
# Funciones acústicas auxiliares para simulación de silenciadores
# --------------------------------------------

# --------------------------------------------
# Importar librerías necesarias
# --------------------------------------------

import numpy as np

# --------------------------------------------
# Calcula el número de onda complejo para cada frecuencia y absorción
# --------------------------------------------
def wavenumber_complex(freq, alpha):
    c = 343  # Velocidad del sonido en aire [m/s]
    omega = 2 * np.pi * freq
    # Número de onda complejo considerando la absorción
    return omega / c - 1j * alpha

# --------------------------------------------
# Calcula la atenuación adicional empírica
# --------------------------------------------
def delta_L_additional(alpha, a, h):
    # Fórmula empírica para atenuación adicional (ajusta según bibliografía)
    return 1.05 * (alpha ** 1.4) * (a / h)
