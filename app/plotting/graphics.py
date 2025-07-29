# --------------------------------------------
# graphics.py
# Generación y visualización del modelo 3D del silenciador tipo splitter
# --------------------------------------------

import pyvista as pv
import numpy as np

# --------------------------------------------
# Genera y muestra el modelo 3D del silenciador tipo splitter
# --------------------------------------------
def generate_3d_model(length, width, height, n_baffles, gap, show_dims=True, plotter=None, img_path=None, html_path=None, baffle_color="#C0C0C0"):
    # Si no se pasa un plotter, crear uno nuevo
    if plotter is None:
        use_offscreen = img_path is not None
        plotter = pv.Plotter(window_size=[1200, 700], off_screen=use_offscreen)
        plotter.set_background("white")

    # Dimensiones del enclosure y baffles
    wall_thickness = 0.005  # 5mm de grosor de paredes
    baffle_thickness = 0.02
    
    # El width ya incluye el espacio necesario para todos los baffles
    interior_width = width - 2 * wall_thickness
    
    # Calcular posiciones de baffles distribuidas uniformemente
    if n_baffles > 1:
        # Distribución uniforme de baffles en el espacio interior
        start_y = wall_thickness + baffle_thickness/2
        end_y = width - wall_thickness - baffle_thickness/2
        baffle_positions = np.linspace(start_y, end_y, n_baffles)
    else:
        # Un solo baffle centrado
        baffle_positions = [width/2]

    # Carcasa externa (caja metálica)
    # Pared frontal
    front_wall = pv.Cube(
        center=(wall_thickness/2, width/2, height/2),
        x_length=wall_thickness, y_length=width, z_length=height
    )
    plotter.add_mesh(front_wall, color="#8C8C8C", opacity=0.8, show_edges=True)
    
    # Pared trasera
    back_wall = pv.Cube(
        center=(length - wall_thickness/2, width/2, height/2),
        x_length=wall_thickness, y_length=width, z_length=height
    )
    plotter.add_mesh(back_wall, color="#8C8C8C", opacity=0.8, show_edges=True)
    
    # Paredes laterales
    left_wall = pv.Cube(
        center=(length/2, wall_thickness/2, height/2),
        x_length=length, y_length=wall_thickness, z_length=height
    )
    plotter.add_mesh(left_wall, color="#8C8C8C", opacity=0.8, show_edges=True)
    
    right_wall = pv.Cube(
        center=(length/2, width - wall_thickness/2, height/2),
        x_length=length, y_length=wall_thickness, z_length=height
    )
    plotter.add_mesh(right_wall, color="#8C8C8C", opacity=0.8, show_edges=True)
    
    # Pared superior
    top_wall = pv.Cube(
        center=(length/2, width/2, height - wall_thickness/2),
        x_length=length, y_length=width, z_length=wall_thickness
    )
    plotter.add_mesh(top_wall, color="#8C8C8C", opacity=0.8, show_edges=True)
    
    # Pared inferior
    bottom_wall = pv.Cube(
        center=(length/2, width/2, wall_thickness/2),
        x_length=length, y_length=width, z_length=wall_thickness
    )
    plotter.add_mesh(bottom_wall, color="#8C8C8C", opacity=0.8, show_edges=True)

    # Baffles internos (usando las posiciones calculadas)
    for i, y_pos in enumerate(baffle_positions):
        baffle = pv.Cube(
            center=(length/2, y_pos, height/2),
            x_length=length - 2*wall_thickness,  # Ajustar al interior
            y_length=baffle_thickness,
            z_length=height - 2*wall_thickness   # Ajustar al interior
        )
        plotter.add_mesh(baffle, color=baffle_color, opacity=0.9, show_edges=True)

    # ========== AGREGAR MEDIDAS AL MODELO 3D ==========
    if show_dims:
        # Configuración de texto
        text_color = 'red'
        text_size = 12
        
        # Longitud total (L1)
        plotter.add_text(f'L1 = {length:.3f} m', 
                        position=(length/2, -width*0.1, -height*0.1), 
                        font_size=text_size, color=text_color)
        
        # Ancho total (L2)
        plotter.add_text(f'L2 = {width:.3f} m', 
                        position=(-length*0.1, width/2, -height*0.1), 
                        font_size=text_size, color=text_color)
        
        # Altura total (H)
        plotter.add_text(f'H = {height:.3f} m', 
                        position=(-length*0.1, -width*0.1, height/2), 
                        font_size=text_size, color=text_color)
        
        # Número de baffles
        plotter.add_text(f'Baffles: {n_baffles}', 
                        position=(length*0.8, width*1.1, height*0.8), 
                        font_size=text_size, color='blue')
        
        # Espesor de baffle
        plotter.add_text(f'Espesor: {baffle_thickness:.3f} m', 
                        position=(length*0.8, width*1.1, height*0.6), 
                        font_size=text_size, color='blue')
        
        # Separación entre baffles
        if len(baffle_positions) > 1:
            separation = gap
            plotter.add_text(f'Gap: {separation:.3f} m', 
                            position=(length*0.8, width*1.1, height*0.4), 
                            font_size=text_size, color='blue')
        
        # Agregar líneas de cota (líneas que muestran las dimensiones)
        # Línea de cota para longitud
        line_length = pv.Line(pointa=(0, -width*0.05, -height*0.05), 
                             pointb=(length, -width*0.05, -height*0.05))
        plotter.add_mesh(line_length, color=text_color, line_width=3)
        
        # Línea de cota para ancho
        line_width = pv.Line(pointa=(-length*0.05, 0, -height*0.05), 
                            pointb=(-length*0.05, width, -height*0.05))
        plotter.add_mesh(line_width, color=text_color, line_width=3)
        
        # Línea de cota para altura
        line_height = pv.Line(pointa=(-length*0.05, -width*0.05, 0), 
                             pointb=(-length*0.05, -width*0.05, height))
        plotter.add_mesh(line_height, color=text_color, line_width=3)

    # Guardar imagen si se solicita
    if img_path:
        plotter.view_isometric()
        plotter.screenshot(img_path)
    
    # Exportar HTML si se solicita
    if html_path:
        plotter.export_html(html_path)

    # Mostrar el modelo si no se está usando en modo embebido y no es off_screen
    if plotter is not None and not hasattr(plotter, 'parent') and not plotter.off_screen:
        plotter.show()
