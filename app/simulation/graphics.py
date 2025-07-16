# --------------------------------------------
# graphics.py
# Funciones gráficas y generación de reporte
# --------------------------------------------

import pyvista as pv
from fpdf import FPDF

def generate_3d_model(width, height, length, n_baffles, gap):
    plotter = pv.Plotter(off_screen=True)
    duct = pv.Cube(center=(length/2, width/2, height/2), x_length=length, y_length=width, z_length=height)
    plotter.add_mesh(duct, color='lightgrey', opacity=0.1)

    for i in range(n_baffles):
        pos = (i + 1) * gap
        baffle = pv.Cube(center=(pos, width / 2, height / 2), x_length=0.02, y_length=width, z_length=height)
        plotter.add_mesh(baffle, color='blue')

    plotter.camera_position = 'xy'
    screenshot_path = "silenciador_3d.png"
    plotter.show(screenshot=screenshot_path)
    return screenshot_path

def export_pdf(S, h, n_espacios, n_baffles, width, img_path, graph_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Reporte de Simulación - Silenciador tipo Splitter", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, f"Área requerida: {S:.4f} m²", ln=True)
    pdf.cell(0, 10, f"Separación entre baffles (2h): {2*h:.4f} m", ln=True)
    pdf.cell(0, 10, f"Número de rendijas: {n_espacios}", ln=True)
    pdf.cell(0, 10, f"Total de baffles: {n_baffles}", ln=True)
    pdf.cell(0, 10, f"Ancho total estimado: {width:.4f} m", ln=True)

    pdf.ln(5)
    pdf.image(graph_path, w=180)
    pdf.ln(5)
    pdf.image(img_path, w=150)
    pdf.output("reporte_silenciador.pdf")
