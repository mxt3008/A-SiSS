# --------------------------------------------
# gui_interface.py
# Interfaz gráfica principal del simulador tipo splitter
# --------------------------------------------

import os
import io
import base64
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton, QLabel,
    QFormLayout, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit, QCheckBox, QColorDialog, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.image import imread
from matplotlib import rcParams
from pyvistaqt import QtInteractor

# --------------------------------------------
# Clase de la interfaz gráfica principal
# --------------------------------------------
class GUIInterface(QWidget):
    def __init__(self, simulate_callback, update_3d_callback, export_txt_callback, export_math_callback):
        super().__init__()
        # Guardar callbacks para usar más tarde
        self._callbacks = [simulate_callback, update_3d_callback, export_txt_callback, export_math_callback]
        
        # Layout principal horizontal
        main_layout = QHBoxLayout(self)
        
        # Panel izquierdo (30%)
        left_panel = QVBoxLayout()
        
        # Panel superior: formulario de parámetros
        form = QFormLayout()
        self.input_Q = QSpinBox(); self.input_Q.setRange(100, 100000); self.input_Q.setValue(10000)
        self.input_V = QDoubleSpinBox(); self.input_V.setRange(1, 100); self.input_V.setValue(12)
        self.input_H = QDoubleSpinBox(); self.input_H.setRange(0.1, 2); self.input_H.setValue(0.3)
        self.input_L = QDoubleSpinBox(); self.input_L.setRange(0.5, 10); self.input_L.setValue(1.7)
        self.input_material = QComboBox(); self.input_material.addItems(['lana50', 'lana70', 'lana100'])
        form.addRow("Caudal [m3/h]:", self.input_Q)
        form.addRow("Velocidad [m/s]:", self.input_V)
        form.addRow("Altura [m]:", self.input_H)
        form.addRow("Longitud [m]:", self.input_L)
        form.addRow("Material:", self.input_material)
        
        # Selector de color
        self.baffle_color = "#C0C0C0"  # Gris metálico por defecto
        self.btn_color = QPushButton("Color de baffles")
        self.btn_color.setStyleSheet(f"background-color: {self.baffle_color}")
        form.addRow("Color de baffles:", self.btn_color)
        self.btn_color.clicked.connect(self.select_baffle_color)
        
        self.btn_simulate = QPushButton("Simular")
        form.addRow(self.btn_simulate)
        
        # Botón para exportar parámetros
        self.btn_export = QPushButton("Exportar Parámetros (.txt)")
        form.addRow(self.btn_export)
        
        left_panel.addLayout(form)
        
        # Panel inferior: resumen textual
        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        # Fuente más legible
        font = QFont("Consolas", 10)
        self.summary_box.setFont(font)
        left_panel.addWidget(QLabel("Resumen de parámetros y resultados:"))
        left_panel.addWidget(self.summary_box)
        main_layout.addLayout(left_panel, 3)  # 30%

        # Panel derecho (70%)
        right_panel = QVBoxLayout()
        self.tabs = QTabWidget()
        
        # Pestaña 1: Gráfica
        self.plot_canvas = FigureCanvas(Figure())
        self.tabs.addTab(self.plot_canvas, "Gráfica")
        
        # Pestaña 2: Modelo 3D
        self.viewer = QtInteractor(self)
        controls_layout = QHBoxLayout()
        self.btn_front = QPushButton("Vista Frontal")
        self.btn_side = QPushButton("Vista Lateral")
        self.btn_iso = QPushButton("Vista Isométrica")
        self.chk_show_dims = QCheckBox("Mostrar medidas")
        self.chk_show_dims.setChecked(True)
        controls_layout.addWidget(self.btn_front)
        controls_layout.addWidget(self.btn_side)
        controls_layout.addWidget(self.btn_iso)
        controls_layout.addWidget(self.chk_show_dims)
        
        model3d_widget = QWidget()
        model3d_layout = QVBoxLayout(model3d_widget)
        model3d_layout.addLayout(controls_layout)
        
        # Contenedor horizontal para modelo 3D y resumen de dimensiones
        model_content_layout = QHBoxLayout()
        
        # Viewer 3D (70% del espacio)
        model_content_layout.addWidget(self.viewer.interactor, 7)
        
        # Panel de dimensiones (30% del espacio)
        dimensions_panel = QVBoxLayout()
        dimensions_label = QLabel("Dimensiones del silenciador:")
        dimensions_label.setAlignment(Qt.AlignTop)
        font_label = QFont("Arial", 11, QFont.Bold)
        dimensions_label.setFont(font_label)
        
        self.summary_3d_box = QTextEdit()
        self.summary_3d_box.setReadOnly(True)
        self.summary_3d_box.setMaximumWidth(300)
        self.summary_3d_box.setMaximumHeight(400)
        # Fuente más grande y legible para las dimensiones
        font_3d = QFont("Consolas", 11)
        self.summary_3d_box.setFont(font_3d)
        
        dimensions_panel.addWidget(dimensions_label)
        dimensions_panel.addWidget(self.summary_3d_box)
        dimensions_panel.addStretch()
        
        model_content_layout.addLayout(dimensions_panel, 3)
        model3d_layout.addLayout(model_content_layout)
        
        self.tabs.addTab(model3d_widget, "Modelo 3D")
        
        # Pestaña 3: Planos Técnicos
        self.technical_canvas = FigureCanvas(Figure(figsize=(16, 12)))
        self.tabs.addTab(self.technical_canvas, "Planos Técnicos")
        
        # Pestaña 4: Fundamentos Matemáticos
        self.math_widget = QWidget()
        math_layout = QVBoxLayout(self.math_widget)
        
        # Crear un scroll area para contener todo el contenido matemático
        math_scroll = QScrollArea()
        math_scroll.setWidgetResizable(True)
        math_content = QWidget()
        math_content_layout = QVBoxLayout(math_content)
        
        # Título principal
        title_label = QLabel("FUNDAMENTOS MATEMÁTICOS Y METODOLOGÍA DE CÁLCULO")
        title_font = QFont("Arial", 14, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        math_content_layout.addWidget(title_label)
        
        # Contenedor para el texto matemático con formato
        self.math_text = QTextEdit()
        self.math_text.setReadOnly(True)
        math_font = QFont("Cambria", 11)
        self.math_text.setFont(math_font)
        math_content_layout.addWidget(self.math_text)
        
        # Botón para exportar matemática como PDF
        self.btn_export_math = QPushButton("Exportar fundamentos matemáticos (PDF)")
        math_content_layout.addWidget(self.btn_export_math)
        
        # Configurar el scroll area
        math_scroll.setWidget(math_content)
        math_layout.addWidget(math_scroll)
        
        self.tabs.addTab(self.math_widget, "Fundamentos Matemáticos")
        
        right_panel.addWidget(self.tabs)
        main_layout.addLayout(right_panel, 7)  # 70%

        self.setLayout(main_layout)

        # Conectar botones a callbacks
        self.btn_simulate.clicked.connect(simulate_callback)
        self.btn_front.clicked.connect(lambda: update_3d_callback('front'))
        self.btn_side.clicked.connect(lambda: update_3d_callback('side'))
        self.btn_iso.clicked.connect(lambda: update_3d_callback('iso'))
        self.chk_show_dims.stateChanged.connect(lambda: update_3d_callback('dims'))
        self.btn_export.clicked.connect(export_txt_callback)
        self.btn_export_math.clicked.connect(export_math_callback)

    # --------------------------------------------
    # Selector de color para los baffles
    # --------------------------------------------
    def select_baffle_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.baffle_color = color.name()
            self.btn_color.setStyleSheet(f"background-color: {self.baffle_color}")

    # --------------------------------------------
    # Actualiza la gráfica en la pestaña correspondiente
    # --------------------------------------------
    def update_plot(self, freq, TL, delta_L, TL_total):
        fig = self.plot_canvas.figure
        fig.clear()
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        ax1.plot(freq, TL, label='TL(f)', color='tab:blue')
        ax2.plot(freq, delta_L, label='ΔL(f)', color='tab:red', linestyle='--')
        ax1.plot(freq, TL_total, label='Atenuación total', color='tab:green', linewidth=2)
        ax1.set_xlabel("Frecuencia [Hz]")
        ax1.set_ylabel("Transmission Loss TL [dB]", color='tab:blue')
        ax2.set_ylabel("Atenuación adicional ΔL [dB]", color='tab:red')
        ax1.tick_params(axis='y', labelcolor='tab:blue')
        ax2.tick_params(axis='y', labelcolor='tab:red')
        ax1.grid(True, alpha=0.3, linestyle='--')  # Agregar grid
        fig.legend(loc='upper right')
        fig.tight_layout()
        self.plot_canvas.draw()

    # --------------------------------------------
    # Actualiza el resumen textual de parámetros/resultados
    # --------------------------------------------
    def update_summary(self, summary_text):
        self.summary_box.setPlainText(summary_text)

    # --------------------------------------------
    # Actualiza el resumen de dimensiones 3D
    # --------------------------------------------
    def update_3d_summary(self, summary_text):
        self.summary_3d_box.setPlainText(summary_text)

    # --------------------------------------------
    # Actualiza los planos técnicos
    # --------------------------------------------
    def update_technical_drawings(self, technical_path):
        """Muestra los planos técnicos en la pestaña correspondiente"""
        fig = self.technical_canvas.figure
        fig.clear()
        
        if os.path.exists(technical_path):
            img = imread(technical_path)
            ax = fig.add_subplot(111)
            ax.imshow(img)
            ax.axis('off')
            fig.tight_layout()
        
        self.technical_canvas.draw()

    # --------------------------------------------
    # Actualiza los fundamentos matemáticos
    # --------------------------------------------
    def update_math_fundamentals(self, params):
        """Muestra los fundamentos matemáticos con ecuaciones LaTeX"""
        if not hasattr(self, 'math_text'):
            # Si no existe la pestaña de matemáticas, la creamos
            self.math_widget = QWidget()
            math_layout = QVBoxLayout(self.math_widget)
            
            # Crear un scroll area para contener todo el contenido matemático
            math_scroll = QScrollArea()
            math_scroll.setWidgetResizable(True)
            math_content = QWidget()
            math_content_layout = QVBoxLayout(math_content)
            
            # Título principal
            title_label = QLabel("FUNDAMENTOS MATEMÁTICOS Y METODOLOGÍA DE CÁLCULO")
            title_font = QFont("Arial", 14, QFont.Bold)
            title_label.setFont(title_font)
            title_label.setAlignment(Qt.AlignCenter)
            math_content_layout.addWidget(title_label)
            
            # Contenedor para el texto matemático con formato
            self.math_text = QTextEdit()
            self.math_text.setReadOnly(True)
            math_font = QFont("Cambria", 11)
            self.math_text.setFont(math_font)
            math_content_layout.addWidget(self.math_text)
            
            # Botón para exportar matemática como PDF
            self.btn_export_math = QPushButton("Exportar fundamentos matemáticos (PDF)")
            math_content_layout.addWidget(self.btn_export_math)
            
            # Configurar el scroll area
            math_scroll.setWidget(math_content)
            math_layout.addWidget(math_scroll)
            
            self.tabs.addTab(self.math_widget, "Fundamentos Matemáticos")
        
        # Importar librerías necesarias para generar imágenes LaTeX
        import matplotlib.pyplot as plt
        from matplotlib import rcParams
        import io
        import base64
        
        # Configurar matplotlib para LaTeX bonito
        rcParams['mathtext.fontset'] = 'cm'
        rcParams['font.family'] = 'serif'
        
        # Función para convertir ecuaciones LaTeX a imágenes base64 embebidas en HTML
        def latex_to_html(formula, fontsize=10):  # Cambiado de 14 a 10
            fig = plt.figure(figsize=(0.01, 0.01))
            fig.text(0, 0, f"${formula}$", fontsize=fontsize)
            
            buffer = io.BytesIO()
            # Reducimos DPI y padding para imágenes más compactas
            plt.savefig(buffer, format='png', dpi=200, bbox_inches='tight', pad_inches=0.03, transparent=True)
            buffer.seek(0)
            img_str = base64.b64encode(buffer.read()).decode('utf-8')
            plt.close(fig)
            
            return f'<img src="data:image/png;base64,{img_str}" style="vertical-align:middle; max-width:90%;">'
        
        # Preparar las fórmulas LaTeX (sin f-strings que contengan backslashes)
        velocidad_sonido = latex_to_html("c = 343 \\ \\text{m/s}")
        conversion_caudal = latex_to_html("Q \\ [\\text{m}^3/\\text{s}] = \\frac{Q \\ [\\text{m}^3/\\text{h}]}{3600}")
        area_paso = latex_to_html("S = \\frac{Q}{V}")
        
        separacion_baffles = latex_to_html("h = \\frac{\\lambda_{max}}{8} = \\frac{c}{8 \\cdot f_{max}} = \\frac{c}{16 \\cdot f_{max}}")
        numero_espacios = latex_to_html("n_{espacios} = \\lceil \\frac{S}{H \\cdot 2h} \\rceil")
        numero_baffles = latex_to_html("n_{baffles} = n_{espacios} - 1")
        
        ancho_interior = latex_to_html("interior\\_width = n_{baffles} \\cdot t_{baffle} + n_{espacios} \\cdot 2h")
        ancho_total = latex_to_html("width = interior\\_width + 2 \\cdot t_{pared}")
        
        numero_onda = latex_to_html("k = \\frac{\\omega}{c} - j\\alpha")
        transmision_loss = latex_to_html("TL = 10 \\cdot \\log_{10}\\left(e^{2\\alpha L}\\right)")
        atenuacion_adicional = latex_to_html("\\Delta L = 1.05 \\cdot \\alpha^{1.4} \\cdot \\frac{a}{h}")
        atenuacion_total = latex_to_html("\\text{Atenuación total} = TL + \\Delta L")
        
        # Ahora usar las variables con las imágenes generadas en el HTML
        html_content = f"""
        <style>
            h2 {{ color: #2C3E50; margin-top: 20px; margin-bottom: 10px; }}
            h3 {{ color: #3498DB; margin-top: 15px; margin-bottom: 5px; }}
            .formula {{ background-color: #F8F9FA; padding: 12px; margin: 10px 0; 
                       border-left: 3px solid #3498DB; text-align: center; }}
            .explanation {{ margin-left: 15px; margin-bottom: 15px; }}
            .section {{ margin-top: 25px; }}
            .subsection {{ margin-top: 15px; }}
            .example {{ background-color: #E8F8F5; padding: 10px; margin: 10px 0; 
                      border: 1px solid #A3E4D7; }}
            .note {{ background-color: #FDEBD0; padding: 8px; margin: 10px 0; 
                   border-left: 3px solid #F39C12; }}
        </style>
        
        <h2>1. Parámetros Fundamentales del Diseño</h2>
        
        <div class="section">
            <h3>1.1 Velocidad del sonido en el aire</h3>
            <div class="formula">
                {velocidad_sonido}
            </div>
            <div class="explanation">
                La velocidad del sonido en aire a temperatura ambiente (20°C) y presión atmosférica estándar.
            </div>
        </div>
        
        <div class="section">
            <h3>1.2 Conversión de caudal</h3>
            <div class="formula">
                {conversion_caudal}
            </div>
            <div class="explanation">
                Conversión del caudal de m³/h a m³/s para cálculos posteriores.<br>
                <strong>Valor actual:</strong> Q = {params["Q"]:.4f} m³/s (equivalente a {params["Q"]*3600:.1f} m³/h)
            </div>
        </div>

        <div class="section">
            <h3>1.3 Área de paso requerida</h3>
            <div class="formula">
                {area_paso}
            </div>
            <div class="explanation">
                Donde:<br>
                S = Área de paso requerida [m²]<br>
                Q = Caudal de aire [m³/s]<br>
                V = Velocidad de paso [m/s]<br><br>
                <strong>Valor calculado:</strong> S = {params["S"]:.4f} m²
            </div>
        </div>

        <h2>2. Dimensionamiento de Baffles</h2>
        
        <div class="section">
            <h3>2.1 Separación entre baffles</h3>
            <div class="formula">
                {separacion_baffles}
            </div>
            <div class="explanation">
                Donde:<br>
                h = Semiseparación entre baffles [m]<br>
                c = Velocidad del sonido [m/s]<br>
                f<sub>max</sub> = Frecuencia máxima de diseño [Hz]<br>
                λ<sub>max</sub> = Longitud de onda correspondiente a la frecuencia máxima [m]<br><br>
                Este cálculo se basa en el criterio de que la separación entre baffles debe ser menor que λ/4,
                donde λ es la longitud de onda correspondiente a la frecuencia máxima de diseño.<br><br>
                <strong>Valor calculado:</strong> h = {params["h"]:.4f} m<br>
                <strong>Separación total (2h):</strong> 2h = {2*params["h"]:.4f} m
            </div>
            <div class="note">
                La fórmula deriva de la necesidad de que la onda sonora experimente múltiples reflexiones 
                dentro del canal formado por baffles adyacentes, maximizando así la absorción.
            </div>
        </div>

        <div class="section">
            <h3>2.2 Número de espacios/rendijas necesarios</h3>
            <div class="formula">
                {numero_espacios}
            </div>
            <div class="explanation">
                Donde:<br>
                n<sub>espacios</sub> = Número de espacios entre baffles<br>
                S = Área de paso requerida [m²]<br>
                H = Altura del silenciador [m]<br>
                h = Semiseparación entre baffles [m]<br><br>
                Se usa la función techo (⌈ ⌉) para garantizar que el área proporcionada sea suficiente.<br><br>
                <strong>Valor calculado:</strong> n<sub>espacios</sub> = {params["n_espacios"]}
            </div>
        </div>

        <div class="section">
            <h3>2.3 Número de baffles</h3>
            <div class="formula">
                {numero_baffles}
            </div>
            <div class="explanation">
                El número de baffles es uno menos que el número de espacios entre ellos.<br><br>
                <strong>Valor calculado:</strong> n<sub>baffles</sub> = {params["n_baffles"]}
            </div>
        </div>

        <h2>3. Dimensiones del Silenciador</h2>
        
        <div class="section">
            <h3>3.1 Ancho interior necesario</h3>
            <div class="formula">
                {ancho_interior}
            </div>
            <div class="explanation">
                Donde:<br>
                interior_width = Ancho interior total necesario [m]<br>
                n<sub>baffles</sub> = Número de baffles<br>
                t<sub>baffle</sub> = Espesor de cada baffle [m]<br>
                n<sub>espacios</sub> = Número de espacios entre baffles<br>
                h = Semiseparación entre baffles [m]<br><br>
                <strong>Valor calculado:</strong> interior_width = {params["interior_width"]:.4f} m
            </div>
        </div>

        <div class="section">
            <h3>3.2 Ancho total del silenciador</h3>
            <div class="formula">
                {ancho_total}
            </div>
            <div class="explanation">
                Donde:<br>
                width = Ancho total del silenciador [m]<br>
                interior_width = Ancho interior [m]<br>
                t<sub>pared</sub> = Espesor de la pared del silenciador [m]<br><br>
                <strong>Valor calculado:</strong> width = {params["width"]:.4f} m
            </div>
        </div>
        
        <h2>4. Cálculos de Atenuación Acústica</h2>
        
        <div class="section">
            <h3>4.1 Número de onda complejo</h3>
            <div class="formula">
                {numero_onda}
            </div>
            <div class="explanation">
                Donde:<br>
                k = Número de onda complejo<br>
                ω = Frecuencia angular = 2πf [rad/s]<br>
                c = Velocidad del sonido [m/s]<br>
                α = Coeficiente de absorción del material<br>
                j = Unidad imaginaria<br><br>
                La parte imaginaria representa la absorción acústica.
            </div>
        </div>
        
        <div class="section">
            <h3>4.2 Pérdida por Transmisión (TL)</h3>
            <div class="formula">
                {transmision_loss}
            </div>
            <div class="explanation">
                Donde:<br>
                TL = Transmission Loss [dB]<br>
                α = 4·α<sub>material</sub>/w<sub>rendija</sub><br>
                L = Longitud del silenciador [m]<br><br>
                Esta fórmula se deriva de la solución de la ecuación de onda con condiciones de absorción.
            </div>
            <div class="note">
                La pérdida por transmisión (TL) representa la diferencia en dB entre la potencia acústica 
                incidente y la transmitida a través del silenciador.
            </div>
        </div>
        
        <div class="section">
            <h3>4.3 Atenuación adicional por efectos de borde</h3>
            <div class="formula">
                {atenuacion_adicional}
            </div>
            <div class="explanation">
                Donde:<br>
                ΔL = Atenuación adicional [dB]<br>
                α = Coeficiente de absorción del material<br>
                a = Ancho de rendija<br>
                h = Semiseparación entre baffles [m]<br><br>
                Esta es una fórmula empírica que considera efectos adicionales no contemplados en el TL básico.
            </div>
        </div>
        
        <div class="section">
            <h3>4.4 Atenuación total</h3>
            <div class="formula">
                {atenuacion_total}
            </div>
            <div class="explanation">
                La atenuación total es la suma de la pérdida por transmisión y la atenuación adicional.<br><br>
                <strong>Atenuación máxima calculada:</strong> {max(params["TL_total"]):.2f} dB
            </div>
        </div>
        
        <h2>5. Referencias Bibliográficas</h2>
        <div class="section">
            <div class="explanation">
                • Bies, D.A. y Hansen, C.H. (2009). <i>Engineering Noise Control: Theory and Practice</i>. CRC Press.<br>
                • Ingard, U. (2009). <i>Noise Reduction Analysis</i>. Jones & Bartlett Learning.<br>
                • Munjal, M.L. (2014). <i>Acoustics of Ducts and Mufflers</i>. John Wiley & Sons.<br>
                • Ver, I.L. y Beranek, L.L. (2005). <i>Noise and Vibration Control Engineering</i>. John Wiley & Sons.
            </div>
        </div>
        """
        
        self.math_text.setHtml(html_content)
        
        # Conectar el botón de exportar si aún no está conectado
        try:
            self.btn_export_math.clicked.disconnect()
        except:
            pass
        self.btn_export_math.clicked.connect(self._callbacks[3])  # El callback exportar_math_pdf
