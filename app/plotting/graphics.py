# --------------------------------------------
# graphics.py
# Generación y visualización del modelo 3D del silenciador tipo splitter
# --------------------------------------------

import pyvista as pv

# --------------------------------------------
# Genera y muestra el modelo 3D del silenciador tipo splitter
# --------------------------------------------
def generate_3d_model(length, width, height, n_baffles, gap, show_dims=True, plotter=None, img_path=None, html_path=None, baffle_color="#FFD700"):
    # Si no se pasa un plotter, crear uno nuevo
    if plotter is None:
        plotter = pv.Plotter(window_size=[1200, 700])
        plotter.set_background("white")

    # Volumen externo transparente (enclosure)
    enclosure = pv.Cube(
        center=(length/2, width/2, height/2),
        x_length=length,
        y_length=width,
        z_length=height
    )
    plotter.add_mesh(enclosure, color="lightgray", opacity=0.1, show_edges=True)

    # Baffles verticales
    baffle_thickness = 0.02
    total_thickness = n_baffles * baffle_thickness + (n_baffles - 1) * gap
    start_y = (width - total_thickness) / 2 + baffle_thickness / 2

    for i in range(n_baffles):
        y = start_y + i * (baffle_thickness + gap)
        baffle = pv.Cube(
            center=(length/2, y, height/2),
            x_length=length,
            y_length=baffle_thickness,
            z_length=height
        )
        plotter.add_mesh(baffle, color=baffle_color, opacity=0.8, show_edges=True)

    # Guardar imagen y/o HTML si se solicita
    if img_path:
        plotter.screenshot(img_path)
    if html_path:
        plotter.export_html(html_path)

    # Mostrar el modelo si no se está usando en modo embebido
    if plotter is not None and not hasattr(plotter, 'parent'):
        plotter.show()
