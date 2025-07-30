# --------------------------------------------
# gui_main.py
# Aplicación principal con GUI basada en PyQt5
# --------------------------------------------

import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from gui_interface import GUIInterface
from app.simulation.solver import calcular_parametros, calcular_parametros_custom
from app.simulation.models import SplitterSilencer
from app.plotting.plots import plot_attenuation_curves
from app.plotting.graphics import generate_3d_model
from app.plotting.docs import export_pdf
from app.plotting.technical_drawings import generate_technical_drawings

OUTPUT_DIR = "outputs"
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")
PDF_DIR = os.path.join(OUTPUT_DIR, "pdf")
TEMP_DIR = os.path.join(OUTPUT_DIR, "temp")
os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# --------------------------------------------
# Clase principal de la aplicación GUI
# --------------------------------------------
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de Silenciadores Tipo Splitter")
        self.setGeometry(100, 100, 1400, 800)
        self.interface = GUIInterface(
            self.simular, 
            self.actualizar_modelo_3d, 
            self.exportar_txt,
            self.exportar_math_pdf
        )
        self.setCentralWidget(self.interface)
        self.data = {}
        self.show_dims = True

    # --------------------------------------------
    # Ejecuta la simulación y actualiza la GUI
    # --------------------------------------------
    def simular(self):
        """Realiza la simulación del silenciador a partir de los parámetros ingresados"""
        # Obtener valores de entrada
        Q_m3h = self.interface.input_Q.value()
        V = self.interface.input_V.value()
        H = self.interface.input_H.value()
        L = self.interface.input_L.value()
        material = self.interface.input_material.currentText()
        fmin, fmax = 100, 500
        
        # Verificar si es material personalizado
        is_custom = False
        if "personal" in material:
            is_custom = True
            custom_freqs = self.interface.custom_material['freqs']
            custom_alphas = self.interface.custom_material['alphas']
            
            # Actualizar límites de frecuencia según material personalizado
            fmin = min(custom_freqs)
            fmax = max(custom_freqs)
        
        # Usa la función de cálculo corregida con el material
        if is_custom:
            params = calcular_parametros_custom(Q_m3h, V, H, L, fmin, fmax, 
                                              custom_freqs, custom_alphas)
        else:
            params = calcular_parametros(Q_m3h, V, H, L, fmin, fmax, material)
        splitter = SplitterSilencer(params["L"], params["width"], params["n_baffles"], params["alpha_interp"])
        TL = splitter.transmission_loss(params["freq"])
        delta_L = splitter.delta_L(params["freq"])
        TL_total = TL + delta_L

        # Guarda los datos para exportar/modelar
        self.data = {
            **params,
            "TL": TL, "delta_L": delta_L, "TL_total": TL_total,
            "img_path": os.path.join(MODELS_DIR, "modelo_3d.png"),
            "graph_path": os.path.join(PLOTS_DIR, "TL_vs_freq.png"),
            "pdf_path": os.path.join(PDF_DIR, "reporte_silenciador.pdf"),
        }

        # Generar planos técnicos
        technical_drawings_path = generate_technical_drawings(
            params["L"], params["width"], params["H"], params["n_baffles"], 
            params["h"] + 0.02, 0.02, 0.005, MODELS_DIR
        )
        
        # Agregar a los datos
        self.data["technical_drawings_path"] = technical_drawings_path

        # Actualiza la gráfica en la GUI
        self.interface.update_plot(params["freq"], TL, delta_L, TL_total)

        # Actualiza el resumen textual
        resumen = (
            f"Caudal: {Q_m3h} m³/h\n"
            f"Velocidad: {V} m/s\n"
            f"Altura: {H} m\n"
            f"Longitud: {L} m\n"
            f"Material: {material}\n"
            f"Área requerida: {params['S']:.4f} m²\n"
            f"Separación entre baffles (2h): {2*params['h']:.4f} m\n"
            f"Número de rendijas: {params['n_espacios']}\n"
            f"Total de baffles: {params['n_baffles']}\n"
            f"Ancho total estimado: {params['width']:.4f} m"
        )
        self.interface.update_summary(resumen)

        # Construir resumen con HTML para mejor apariencia
        html_summary = f"""
        <style>
            h2 {{ color: #2C3E50; font-size: 14px; margin-top: 10px; margin-bottom: 5px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 5px 0; }}
            td {{ padding: 3px 5px; }}
            .label {{ color: #7F8C8D; width: 45%; }}
            .value {{ color: #2C3E50; font-weight: bold; }}
            .section {{ background-color: #EBF5FB; border-left: 4px solid #3498DB; 
                      margin: 8px 0; padding: 5px 8px; border-radius: 3px; }}
            .highlight {{ color: #E74C3C; }}
        </style>

        <h2>📊 PARÁMETROS DE ENTRADA</h2>
        <div class="section">
            <table>
                <tr><td class="label">Caudal:</td><td class="value">{Q_m3h} m³/h</td></tr>
                <tr><td class="label">Velocidad:</td><td class="value">{V} m/s</td></tr>
                <tr><td class="label">Altura:</td><td class="value">{H} m</td></tr>
                <tr><td class="label">Longitud:</td><td class="value">{L} m</td></tr>
                <tr><td class="label">Material:</td><td class="value">{material}</td></tr>
            </table>
        </div>

        <h2>📈 RESULTADOS DEL CÁLCULO</h2>
        <div class="section">
            <table>
                <tr><td class="label">Área requerida:</td><td class="value">{params['S']:.4f} m²</td></tr>
                <tr><td class="label">Separación entre baffles:</td><td class="value">{2*params['h']:.4f} m</td></tr>
                <tr><td class="label">Número de rendijas:</td><td class="value">{params['n_espacios']}</td></tr>
                <tr><td class="label">Total de baffles:</td><td class="value">{params['n_baffles']}</td></tr>
                <tr><td class="label">Ancho total estimado:</td><td class="value highlight">{params['width']:.4f} m</td></tr>
            </table>
        </div>

        <h2>🔊 ATENUACIÓN ACÚSTICA</h2>
        <div class="section">
            <table>
                <tr><td class="label">Rango de frecuencias:</td><td class="value">{min(params['freq']):.0f} - {max(params['freq']):.0f} Hz</td></tr>
                <tr><td class="label">Atenuación máxima:</td><td class="value highlight">{max(TL_total):.2f} dB</td></tr>
            </table>
        </div>
        """

        # Actualizar el resumen de atenuación con HTML
        self.interface.update_summary(html_summary)

        # Parámetros para el modelo 3D
        baffle_thickness = 0.02
        gap = params['h'] + 0.02
        n_baffles = params['n_baffles']
        n_espacios = params['n_espacios']
        rendija_ancho = params['h']
        summary_3d = (
            f"Dimensiones del silenciador:\n"
            f"- Largo total (L): {params['L']:.2f} m\n"
            f"- Altura total (a): {params['H']:.2f} m\n"
            f"- Ancho total (b): {params['width']:.2f} m\n"
            f"- Número de baffles: {n_baffles}\n"
            f"- Espesor de cada baffle: {baffle_thickness:.2f} m\n"
            f"- Separación entre baffles (gap): {gap:.2f} m\n"
            f"- Ancho de cada rendija: {rendija_ancho:.2f} m\n"
            f"- Número de rendijas: {n_espacios}\n"
        )
        self.interface.update_3d_summary(summary_3d)

        # Actualiza el modelo 3D
        self.actualizar_modelo_3d('update')
        
        # Actualizar las gráficas
        self.interface.update_plot(params["freq"], TL, delta_L, TL_total)
        
        # Actualizar el resumen de atenuación
        self.interface.update_summary(resumen)
        
        # Actualizar los planos técnicos
        if "technical_drawings_path" in self.data:
            self.interface.update_technical_drawings(self.data["technical_drawings_path"])
        
        # ASEGURARSE de llamar a la actualización de fundamentos matemáticos
        # con todos los parámetros correctos
        self.interface.update_math_fundamentals(self.data)
        
        # Mostrar la pestaña de modelo 3D como predeterminada al terminar
        self.interface.tabs.setCurrentIndex(0)  # Mostrar la pestaña del modelo 3D

    # --------------------------------------------
    # Actualiza el modelo 3D interactivo según controles
    # --------------------------------------------
    def actualizar_modelo_3d(self, event_type='update'):
        """Actualiza el modelo 3D del silenciador"""
        if not self.data:
            return
        
        # Limpiar visualizador existente
        plotter = self.interface.plotter  # Usar plotter en lugar de viewer
        plotter.clear()
        
        # Obtener datos del silenciador
        L = self.data['L']
        width = self.data['width']
        H = self.data['H']
        n_baffles = self.data['n_baffles']
        h = self.data['h']
        baffle_color = self.interface.baffle_color
        
        # Generar modelo 3D
        generate_3d_model(
            L, width, H, n_baffles, h,
            plotter=plotter,  # Usar plotter en lugar de viewer
            baffle_color=baffle_color
        )
        
        # Actualizar la vista
        plotter.reset_camera()
        plotter.update()
        
        # Actualizar resumen de dimensiones
        self.update_3d_summary()

    # --------------------------------------------
    # Exporta el reporte PDF (puedes agregar un botón para esto)
    # --------------------------------------------
    def exportar_pdf(self):
        if not self.data:
            QMessageBox.warning(self, "Advertencia", "Primero realiza una simulación.")
            return
        plot_attenuation_curves(
            self.data["freq"], self.data["TL"], self.data["delta_L"], self.data["TL_total"], self.data["graph_path"]
        )
        generate_3d_model(
            self.data["L"], self.data["width"], self.data["H"], self.data["n_baffles"],
            gap=self.data["h"] + 0.02, show_dims=True, img_path=self.data["img_path"]
        )
        export_pdf(
            self.data["S"], self.data["h"], self.data["n_espacios"], self.data["n_baffles"], self.data["width"],
            self.data["img_path"], self.data["graph_path"], self.data["pdf_path"]
        )
        QMessageBox.information(self, "Éxito", f"PDF exportado en:\n{self.data['pdf_path']}")

    def exportar_txt(self):
        """Exporta los parámetros a un archivo de texto"""
        if not self.data:
            QMessageBox.warning(self, "Advertencia", "Primero realiza una simulación.")
            return
            
        txt_path = os.path.join(OUTPUT_DIR, "parametros_silenciador.txt")
        
        with open(txt_path, 'w') as f:
            f.write("PARÁMETROS DEL SILENCIADOR TIPO SPLITTER\n")
            f.write("========================================\n\n")
            f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
            f.write("PARÁMETROS DE ENTRADA:\n")
            f.write(f"- Caudal: {self.interface.input_Q.value()} m³/h\n")
            f.write(f"- Velocidad: {self.interface.input_V.value()} m/s\n")
            f.write(f"- Altura: {self.interface.input_H.value()} m\n")
            f.write(f"- Longitud: {self.interface.input_L.value()} m\n")
            f.write(f"- Material: {self.interface.input_material.currentText()}\n\n")
            f.write("RESULTADOS DEL CÁLCULO:\n")
            f.write(f"- Área requerida: {self.data['S']:.4f} m²\n")
            f.write(f"- Separación entre baffles (2h): {2*self.data['h']:.4f} m\n")
            f.write(f"- Número de rendijas: {self.data['n_espacios']}\n")
            f.write(f"- Total de baffles: {self.data['n_baffles']}\n")
            f.write(f"- Ancho total estimado: {self.data['width']:.4f} m\n\n")
            f.write("DIMENSIONES DEL SILENCIADOR:\n")
            f.write(f"- Largo total (L1): {self.data['L']:.3f} m\n")
            f.write(f"- Ancho total (L2): {self.data['width']:.3f} m\n")
            f.write(f"- Altura (H): {self.data['H']:.3f} m\n")
            f.write(f"- Espesor de cada baffle: {0.02:.3f} m\n")
            f.write(f"- Separación entre baffles: {self.data['h'] + 0.02:.3f} m\n\n")
            f.write("ATENUACIÓN ACÚSTICA:\n")
            f.write(f"- Rango de frecuencias: {min(self.data['freq']):.0f} - {max(self.data['freq']):.0f} Hz\n")
            f.write(f"- Atenuación máxima: {max(self.data['TL_total']):.2f} dB\n")
            
        QMessageBox.information(self, "Éxito", f"Parámetros exportados en:\n{txt_path}")

    def exportar_math_pdf(self):
        """Exporta los fundamentos matemáticos a un archivo PDF con ecuaciones LaTeX"""
        if not self.data:
            QMessageBox.warning(self, "Advertencia", "Primero realiza una simulación.")
            return
        
        # Verificar si las bibliotecas necesarias están instaladas
        try:
            import reportlab
            import matplotlib
            from PIL import Image
        except ImportError:
            QMessageBox.warning(
                self, 
                "Error - Bibliotecas faltantes", 
                "Para generar el PDF con fundamentos matemáticos, necesitas instalar:\n\n"
                "pip install reportlab matplotlib pillow\n\n"
                "Ejecuta este comando en tu terminal y vuelve a intentarlo."
            )
            return
            
        try:
            # Usar ReportLab para un PDF avanzado con ecuaciones
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            
            # Generar imágenes de ecuaciones con matplotlib
            import matplotlib.pyplot as plt
            from matplotlib import rcParams
            import io
            from PIL import Image as PILImage
            
            # Configurar matplotlib para LaTeX bonito
            rcParams['mathtext.fontset'] = 'cm'
            rcParams['font.family'] = 'serif'
            
            pdf_path = os.path.join(PDF_DIR, "fundamentos_matematicos.pdf")
            
            # Crear documento y estilos
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Crear estilos personalizados
            title_style = ParagraphStyle(
                'TitleStyle', 
                parent=styles['Heading1'],
                fontSize=16,
                alignment=1,  # Centrado
                spaceAfter=20
            )
            
            heading1_style = ParagraphStyle(
                'Heading1Style',
                parent=styles['Heading1'],
                fontSize=14,
                spaceAfter=10
            )
            
            heading2_style = ParagraphStyle(
                'Heading2Style',
                parent=styles['Heading2'],
                fontSize=12,
                textColor=colors.blue,
                spaceAfter=5
            )
            
            normal_style = ParagraphStyle(
                'NormalStyle',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=8
            )
            
            formula_style = ParagraphStyle(
                'FormulaStyle',
                parent=styles['Normal'],
                alignment=1,  # Centrado
                spaceAfter=10
            )
            
            # Función para generar imagen de fórmula LaTeX
            def latex_to_image(formula, filename, fontsize=14):
                fig = plt.figure(figsize=(8, 1))
                fig.text(0.5, 0.5, f"${formula}$", fontsize=fontsize, ha='center', va='center')
                
                buffer = io.BytesIO()
                plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', transparent=True)
                buffer.seek(0)
                
                img_path = os.path.join(TEMP_DIR, filename)
                if not os.path.exists(TEMP_DIR):
                    os.makedirs(TEMP_DIR)
                    
                img = PILImage.open(buffer)
                img.save(img_path)
                plt.close(fig)
                
                return img_path
            
            # Crear contenido
            story = []
            
            # Título principal
            story.append(Paragraph("FUNDAMENTOS MATEMÁTICOS Y METODOLOGÍA DE CÁLCULO", title_style))
            story.append(Spacer(1, 0.2*inch))
            
            # 1. Parámetros Fundamentales
            story.append(Paragraph("1. Parámetros Fundamentales del Diseño", heading1_style))
            
            # 1.1 Velocidad del sonido
            story.append(Paragraph("1.1 Velocidad del sonido en el aire", heading2_style))
            formula_img = latex_to_image("c = 343 \\ \\text{m/s}", "formula_c.png")
            story.append(Image(formula_img, width=3*inch, height=0.7*inch))
            story.append(Paragraph("La velocidad del sonido en aire a temperatura ambiente (20°C) y presión atmosférica estándar.", normal_style))
            
            # 1.2 Conversión de caudal
            story.append(Paragraph("1.2 Conversión de caudal", heading2_style))
            formula_img = latex_to_image("Q \\ [\\text{m}^3/\\text{s}] = \\frac{Q \\ [\\text{m}^3/\\text{h}]}{3600}", "formula_q.png")
            story.append(Image(formula_img, width=4*inch, height=inch))
            story.append(Paragraph(f"Valor actual: Q = {self.data['Q']:.4f} m³/s (equivalente a {self.data['Q']*3600:.1f} m³/h)", normal_style))
            
            # 1.3 Área de paso
            story.append(Paragraph("1.3 Área de paso requerida", heading2_style))
            formula_img = latex_to_image("S = \\frac{Q}{V}", "formula_s.png")
            story.append(Image(formula_img, width=2*inch, height=0.7*inch))
            story.append(Paragraph(f"Valor calculado: S = {self.data['S']:.4f} m²", normal_style))
            
            # 2. Dimensionamiento de Baffles
            story.append(Paragraph("2. Dimensionamiento de Baffles", heading1_style))
            
            # 2.1 Separación entre baffles
            story.append(Paragraph("2.1 Separación entre baffles", heading2_style))
            formula_img = latex_to_image("h = \\frac{\\lambda_{max}}{8} = \\frac{c}{8·f_{max}}", "formula_h.png")
            story.append(Image(formula_img, width=3*inch, height=0.7*inch))
            story.append(Paragraph(f"Valor calculado: h = {self.data['h']:.4f} m", normal_style))
            story.append(Paragraph(f"Separación total (2h): 2h = {2*self.data['h']:.4f} m", normal_style))
            story.append(Paragraph("Donde λ es la longitud de onda máxima en el silenciador.", normal_style))
            
            # 2.2 Número de espacios/rendijas necesarios
            story.append(Paragraph("2.2 Número de espacios/rendijas necesarios", heading2_style))
            formula_img = latex_to_image("n_espacios = \\lceil \\frac{S}{H · 2h} \\rceil", "formula_n_espacios.png")
            story.append(Image(formula_img, width=3*inch, height=0.7*inch))
            story.append(Paragraph(f"Valor calculado: n_espacios = {self.data['n_espacios']}", normal_style))
            story.append(Paragraph("Donde ceil() es la función techo que redondea al entero superior.", normal_style))
            
            # 2.3 Número de baffles
            story.append(Paragraph("2.3 Número de baffles", heading2_style))
            formula_img = latex_to_image("n_baffles = n_espacios - 1", "formula_n_baffles.png")
            story.append(Image(formula_img, width=3*inch, height=0.7*inch))
            story.append(Paragraph(f"Valor calculado: n_baffles = {self.data['n_baffles']}", normal_style))
            
            # 3. Dimensiones del Silenciador
            story.append(Paragraph("3. Dimensiones del Silenciador", heading1_style))
            
            # 3.1 Ancho interior necesario
            story.append(Paragraph("3.1 Ancho interior necesario", heading2_style))
            formula_img = latex_to_image("interior_width = n_baffles · t_baffle + n_espacios · 2h", "formula_interior_width.png")
            story.append(Image(formula_img, width=4*inch, height=0.7*inch))
            story.append(Paragraph(f"Valor calculado: interior_width = {self.data['interior_width']:.4f} m", normal_style))
            
            # 3.2 Ancho total del silenciador
            story.append(Paragraph("3.2 Ancho total del silenciador", heading2_style))
            formula_img = latex_to_image("width = interior_width + 2 · t_pared", "formula_width.png")
            story.append(Image(formula_img, width=3*inch, height=0.7*inch))
            story.append(Paragraph(f"Valor calculado: width = {self.data['width']:.4f} m", normal_style))
            
            # 4. Cálculos de Atenuación Acústica
            story.append(Paragraph("4. Cálculos de Atenuación Acústica", heading1_style))
            
            # 4.1 Pérdida por Transmisión (TL)
            story.append(Paragraph("4.1 Pérdida por Transmisión (TL)", heading2_style))
            formula_img = latex_to_image("TL = 10·log(e^(2·α·L))", "formula_tl.png")
            story.append(Image(formula_img, width=3*inch, height=0.7*inch))
            story.append(Paragraph("Donde α es el coeficiente de absorción del material.", normal_style))
            
            # 4.2 Atenuación adicional por efectos de borde
            story.append(Paragraph("4.2 Atenuación adicional por efectos de borde", heading2_style))
            formula_img = latex_to_image("ΔL = 1.05·(α^1.4)·(a/h)", "formula_delta_L.png")
            story.append(Image(formula_img, width=3*inch, height=0.7*inch))
            story.append(Paragraph("Donde a es la altura del silenciador.", normal_style))
            
            # 4.3 Atenuación total
            story.append(Paragraph("4.3 Atenuación total", heading2_style))
            formula_img = latex_to_image("Atenuación total = TL + ΔL", "formula_atenuacion_total.png")
            story.append(Image(formula_img, width=3*inch, height=0.7*inch))
            story.append(Paragraph(f"Atenuación máxima calculada: {max(self.data['TL_total']):.2f} dB", normal_style))
            
            # 5. Referencias Bibliográficas
            story.append(Paragraph("5. Referencias Bibliográficas", heading1_style))
            
            story.append(Paragraph("• Bies, D.A. y Hansen, C.H. (2009). Engineering Noise Control: Theory and Practice.", normal_style))
            story.append(Paragraph("• Ingard, U. (2009). Noise Reduction Analysis.", normal_style))
            story.append(Paragraph("• Munjal, M.L. (2014). Acoustics of Ducts and Mufflers.", normal_style))
            story.append(Paragraph("• Ver, I.L. y Beranek, L.L. (2005). Noise and Vibration Control Engineering.", normal_style))
            
            # Construir documento PDF
            doc.build(story)
            QMessageBox.information(self, "Éxito", f"Fundamentos matemáticos exportados en:\n{pdf_path}")
        
        except ImportError:
            QMessageBox.warning(self, "Error", "Necesitas instalar las librerías reportlab, matplotlib y Pillow:\npip install reportlab matplotlib Pillow")

    def update_3d_summary(self):
        """Actualiza el resumen de dimensiones 3D"""
        if not self.data:
            return
            
        baffle_thickness = 0.02  # m
        wall_thickness = 0.02  # m
        
        # Generar contenido HTML con mejor formato y estilos
        html_content = f"""
        <style>
            h2 {{ color: #2C3E50; font-size: 14px; margin-top: 10px; margin-bottom: 5px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 5px 0; }}
            td {{ padding: 3px 5px; }}
            .label {{ color: #7F8C8D; width: 55%; }}
            .value {{ color: #2C3E50; font-weight: bold; }}
            .section {{ background-color: #EBF5FB; border-left: 4px solid #3498DB; 
                      margin: 8px 0; padding: 5px 8px; border-radius: 3px; }}
            .highlight {{ color: #E74C3C; }}
        </style>
        
        <h2>📐 DIMENSIONES PRINCIPALES</h2>
        <div class="section">
            <table>
                <tr><td class="label">Longitud total:</td><td class="value">{self.data['L']:.2f} m</td></tr>
                <tr><td class="label">Altura total:</td><td class="value">{self.data['H']:.2f} m</td></tr>
                <tr><td class="label">Ancho total:</td><td class="value">{self.data['width']:.2f} m</td></tr>
            </table>
        </div>
        
        <h2>🔳 DATOS DE LOS BAFFLES</h2>
        <div class="section">
            <table>
                <tr><td class="label">Número de baffles:</td><td class="value">{self.data['n_baffles']}</td></tr>
                <tr><td class="label">Espesor de cada baffle:</td><td class="value">{baffle_thickness:.2f} m</td></tr>
                <tr><td class="label">Separación entre baffles:</td><td class="value">{self.data['h']*2:.3f} m</td></tr>
                <tr><td class="label">Material absorbente:</td><td class="value">{self.data['material']}</td></tr>
            </table>
        </div>
        
        <h2>↕️ RENDIJAS</h2>
        <div class="section">
            <table>
                <tr><td class="label">Número de rendijas:</td><td class="value">{self.data['n_espacios']}</td></tr>
                <tr><td class="label">Ancho de cada rendija:</td><td class="value">{self.data['h']*2:.3f} m</td></tr>
            </table>
        </div>
        
        <h2>⚙️ CARACTERÍSTICAS CONSTRUCTIVAS</h2>
        <div class="section">
            <table>
                <tr><td class="label">Espesor de las paredes:</td><td class="value">{wall_thickness:.2f} m</td></tr>
                <tr><td class="label">Área de paso:</td><td class="value class="highlight">{self.data['S']:.3f} m²</td></tr>
            </table>
        </div>
        """
        
        # Actualizar el cuadro de resumen en la interfaz
        self.interface.update_3d_summary(html_content)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
