# --------------------------------------------
# solver.py
# Funciones de cálculo geométrico y de parámetros para silenciadores tipo splitter
# --------------------------------------------

import numpy as np

# --------------------------------------------
# Calcula todos los parámetros geométricos y acústicos necesarios para el silenciador tipo splitter
# --------------------------------------------
def calcular_parametros(Q_m3h, V, H, fmin, fmax, L, material):
    # Conversión de caudal de m3/h a m3/s
    Q = Q_m3h / 3600
    # Velocidad del sonido en aire (m/s)
    c = 343
    # Altura de rendija (criterio empírico para evitar modos superiores)
    h = (c / fmax) / 8 / 2
    # Altura total del canal
    a = H
    # Área requerida para el flujo
    S = Q / V
    # Número de espacios (rendijas) y baffles
    n_espacios = int(np.floor(S / (a * 2 * h)))
    n_baffles = n_espacios + 1
    # Ancho total estimado del silenciador
    width = n_espacios * h + n_baffles * 0.02
    # Vector de frecuencias de análisis
    freq = np.linspace(fmin, fmax, 300)
    # Coeficientes de absorción por material (interpolados)
    freqs_material = np.array([125, 250, 500])
    alphas_dict = {
        'lana50': np.array([0.19, 0.43, 0.77]),
        'lana70': np.array([0.33, 0.65, 0.88]),
        'lana100': np.array([0.54, 0.87, 1.00])
    }
    alpha_interp = np.interp(freq, freqs_material, alphas_dict[material])
    # Devuelve todos los parámetros en un diccionario
    return {
        "Q": Q, "c": c, "h": h, "a": a, "S": S, "n_espacios": n_espacios, "n_baffles": n_baffles,
        "width": width, "freq": freq, "alpha_interp": alpha_interp, "L": L, "H": H
    }