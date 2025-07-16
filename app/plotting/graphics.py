# graphics.py
import pyvista as pv
import numpy as np

def generate_3d_model(length, width, height, n_baffles, gap):
    plotter = pv.Plotter(window_size=[1200, 700])
    plotter.set_background("white")

    # Volumen externo transparente (L × b × a)
    enclosure = pv.Cube(
        center=(length/2, width/2, height/2),
        x_length=length,
        y_length=width,
        z_length=height
    )
    plotter.add_mesh(enclosure, color="lightgray", opacity=0.1, show_edges=True)

    # Baffles amarillos verticales (de frente)
    baffle_thickness = 0.02
    total_thickness = n_baffles * baffle_thickness + (n_baffles - 1) * gap
    start_y = (width - total_thickness) / 2 + baffle_thickness / 2

    for i in range(n_baffles):
        y = start_y + i * (gap + baffle_thickness)
        baffle = pv.Cube(
            center=(length/2, y, height/2),
            x_length=length,
            y_length=baffle_thickness,
            z_length=height
        )
        plotter.add_mesh(baffle, color="yellow", show_edges=True)

    # Añadir cotas con líneas y texto 3D
    def add_dimension(p1, p2, label, z_offset=0.02):
        line = pv.Line(p1, p2)
        plotter.add_mesh(line, color="black", line_width=2)
        mid = [(a + b) / 2 for a, b in zip(p1, p2)]
        mid[2] += z_offset
        plotter.add_point_labels([mid], [label], font_size=12, text_color="black")

    add_dimension((0, 0, 0), (length, 0, 0), f"L = {length:.2f} m")
    add_dimension((0, 0, 0), (0, width, 0), f"b = {width:.2f} m")
    add_dimension((0, 0, 0), (0, 0, height), f"a = {height:.2f} m")

    plotter.add_text("Presiona X / Y / I para vista frontal/lateral/isométrica", position=(10, 10), font_size=10)
    plotter.add_key_event("x", lambda: plotter.view_xy())
    plotter.add_key_event("y", lambda: plotter.view_yz())
    plotter.add_key_event("i", lambda: plotter.view_isometric())

    plotter.show()
