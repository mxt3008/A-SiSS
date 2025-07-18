# Simulador de Silenciadores Tipo Splitter

Este software permite simular y analizar el desempeño acústico de silenciadores tipo splitter, generando gráficas, modelos 3D y reportes PDF.

## Características

- Simulación de atenuación acústica para silenciadores tipo splitter.
- Visualización de resultados en gráficas y modelo 3D interactivo.
- Exportación de reportes y resultados organizados por tipo de archivo.

## Estructura de carpetas

```
outputs/
  pdf/      # Reportes PDF
  plots/    # Gráficas de simulación
  models/   # Imágenes y archivos del modelo 3D
```

## Requisitos

- Python 3.8+
- PyQt5
- numpy, matplotlib, pyvista, pyvistaqt, fpdf

## Uso

1. Ejecuta `main.py` para la versión por consola, o `app/gui_main.py` para la versión gráfica.
2. Ingresa los parámetros y simula.
3. Visualiza los resultados y exporta archivos desde la interfaz gráfica.

## Créditos

Desarrollado por [Tu Nombre] para la Maestría PUCP.