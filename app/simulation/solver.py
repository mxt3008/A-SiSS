# --------------------------------------------
# solver.py
# Funciones de cálculo geométrico y de parámetros para silenciadores tipo splitter
# --------------------------------------------

import numpy as np

# --------------------------------------------
# Calcula todos los parámetros geométricos y acústicos necesarios para el silenciador tipo splitter
# --------------------------------------------
def calcular_parametros(Q_m3h, V, H, L, fmin=100, fmax=500, material='lana100'):
    """
    Calcula todos los parámetros geométricos del silenciador
    """
    # Conversiones básicas
    Q = Q_m3h / 3600  # m³/s
    c = 343  # m/s velocidad del sonido
    
    # Cálculo de separación entre baffles
    h = (c / fmax) / 8 / 2  # separación mínima
    
    # Área de paso requerida
    S = Q / V
    
    # Número de espacios (rendijas) necesarios
    n_espacios = int(np.ceil(S / (H * 2 * h)))  # usar ceil para asegurar área suficiente
    
    # Número de baffles
    n_baffles = n_espacios - 1  # Corregir: n espacios requiere n-1 baffles
    
    # Espesor de cada baffle
    baffle_thickness = 0.02  # 2 cm
    
    # Ancho total del enclosure (incluyendo paredes)
    wall_thickness = 0.005  # 5 mm de pared
    
    # Ancho interior necesario para baffles y espacios
    interior_width_needed = n_baffles * baffle_thickness + n_espacios * (2 * h)
    
    # Ancho total del enclosure
    width = interior_width_needed + 2 * wall_thickness
    
    # Frecuencias para la simulación
    freq = np.linspace(fmin, fmax, 300)
    
    # Coeficientes de absorción del material
    freqs_material = np.array([125, 250, 500])
    alphas_dict = {
        'lana50': np.array([0.19, 0.43, 0.77]),
        'lana70': np.array([0.33, 0.65, 0.88]),
        'lana100': np.array([0.54, 0.87, 1.00])
    }
    alpha_interp = np.interp(freq, freqs_material, alphas_dict[material])
    
    return {
        'Q': Q,
        'S': S,
        'h': h,
        'n_espacios': n_espacios,
        'n_baffles': n_baffles,
        'width': width,
        'L': L,
        'H': H,
        'baffle_thickness': baffle_thickness,
        'wall_thickness': wall_thickness,
        'interior_width': interior_width_needed,
        'freq': freq,
        'alpha_interp': alpha_interp,
        'material': material
    }

def calcular_parametros_custom(Q_m3h, V, H, L, fmin, fmax, custom_freqs, custom_alphas):
    """
    Calcula todos los parámetros geométricos del silenciador con un material personalizado
    """
    # Realizar los mismos cálculos básicos
    params = calcular_parametros(Q_m3h, V, H, L, fmin, fmax, 'lana50')  # Base con un material cualquiera
    
    # Reemplazar la interpolación de coeficientes con los valores personalizados
    freq = params['freq']
    params['alpha_interp'] = np.interp(freq, custom_freqs, custom_alphas)
    params['material'] = 'Personalizado'
    
    return params