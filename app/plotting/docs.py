# --------------------------------------------
# docs.py
# Generación de reporte PDF automático
# --------------------------------------------

from fpdf import FPDF

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
