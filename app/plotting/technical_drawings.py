# --------------------------------------------
# technical_drawings.py
# Generación de planos técnicos con medidas tipo publicación científica
# --------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def generate_technical_drawings(length, width, height, n_baffles, gap, baffle_thickness, wall_thickness, output_dir):
    """
    Genera planos técnicos: vista frontal, lateral y superior con medidas
    """
    # Configuración de estilo técnico
    plt.style.use('default')
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('SILENCIADOR TIPO SPLITTER - PLANOS TÉCNICOS', fontsize=16, fontweight='bold')
    
    # Calcular posiciones de baffles
    interior_width = width - 2 * wall_thickness
    total_thickness = n_baffles * baffle_thickness + (n_baffles - 1) * gap
    start_y = wall_thickness + (interior_width - total_thickness) / 2 + baffle_thickness / 2
    
    baffle_positions = []
    for i in range(n_baffles):
        y = start_y + i * (baffle_thickness + gap)
        baffle_positions.append(y)
    
    # ========== VISTA FRONTAL (A) ==========
    ax1 = axes[0, 0]
    ax1.set_title('VISTA FRONTAL', fontweight='bold')
    ax1.set_aspect('equal')
    
    # Carcasa externa
    rect_outer = patches.Rectangle((0, 0), width, height, linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
    ax1.add_patch(rect_outer)
    
    # Paredes laterales
    rect_left = patches.Rectangle((0, 0), wall_thickness, height, linewidth=1, edgecolor='black', facecolor='gray')
    rect_right = patches.Rectangle((width-wall_thickness, 0), wall_thickness, height, linewidth=1, edgecolor='black', facecolor='gray')
    ax1.add_patch(rect_left)
    ax1.add_patch(rect_right)
    
    # Baffles
    for y_pos in baffle_positions:
        baffle_rect = patches.Rectangle((y_pos - baffle_thickness/2, wall_thickness), 
                                      baffle_thickness, height - 2*wall_thickness, 
                                      linewidth=1, edgecolor='blue', facecolor='lightblue', alpha=0.7)
        ax1.add_patch(baffle_rect)
    
    # Medidas frontales
    # Ancho total
    ax1.annotate('', xy=(0, -0.05), xytext=(width, -0.05), arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax1.text(width/2, -0.08, f'L2 = {width:.3f} m', ha='center', va='top', fontsize=10, color='red', fontweight='bold')
    
    # Altura total
    ax1.annotate('', xy=(-0.05, 0), xytext=(-0.05, height), arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax1.text(-0.08, height/2, f'H = {height:.3f} m', ha='right', va='center', fontsize=10, color='red', fontweight='bold', rotation=90)
    
    # Separación entre baffles
    if len(baffle_positions) > 1:
        y1 = baffle_positions[0] + baffle_thickness/2
        y2 = baffle_positions[1] - baffle_thickness/2
        ax1.annotate('', xy=(y1, height+0.02), xytext=(y2, height+0.02), arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5))
        ax1.text((y1+y2)/2, height+0.04, f'2h = {gap:.3f} m', ha='center', va='bottom', fontsize=9, color='blue', fontweight='bold')
    
    ax1.set_xlim(-0.15, width+0.05)
    ax1.set_ylim(-0.15, height+0.1)
    ax1.grid(True, alpha=0.3)
    
    # ========== VISTA LATERAL (B) ==========
    ax2 = axes[0, 1]
    ax2.set_title('VISTA LATERAL', fontweight='bold')
    ax2.set_aspect('equal')
    
    # Carcasa lateral
    rect_lateral = patches.Rectangle((0, 0), length, height, linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
    ax2.add_patch(rect_lateral)
    
    # Paredes superior e inferior
    rect_bottom = patches.Rectangle((0, 0), length, wall_thickness, linewidth=1, edgecolor='black', facecolor='gray')
    rect_top = patches.Rectangle((0, height-wall_thickness), length, wall_thickness, linewidth=1, edgecolor='black', facecolor='gray')
    ax2.add_patch(rect_bottom)
    ax2.add_patch(rect_top)
    
    # Medidas laterales
    # Longitud total
    ax2.annotate('', xy=(0, -0.05), xytext=(length, -0.05), arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax2.text(length/2, -0.08, f'L1 = {length:.3f} m', ha='center', va='top', fontsize=10, color='red', fontweight='bold')
    
    # Altura total
    ax2.annotate('', xy=(-0.05, 0), xytext=(-0.05, height), arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax2.text(-0.08, height/2, f'H = {height:.3f} m', ha='right', va='center', fontsize=10, color='red', fontweight='bold', rotation=90)
    
    ax2.set_xlim(-0.15, length+0.05)
    ax2.set_ylim(-0.15, height+0.05)
    ax2.grid(True, alpha=0.3)
    
    # ========== VISTA SUPERIOR (C) ==========
    ax3 = axes[1, 0]
    ax3.set_title('VISTA SUPERIOR', fontweight='bold')
    ax3.set_aspect('equal')
    
    # Carcasa superior
    rect_top_view = patches.Rectangle((0, 0), length, width, linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.3)
    ax3.add_patch(rect_top_view)
    
    # Paredes frontal y trasera
    rect_front = patches.Rectangle((0, 0), wall_thickness, width, linewidth=1, edgecolor='black', facecolor='gray')
    rect_back = patches.Rectangle((length-wall_thickness, 0), wall_thickness, width, linewidth=1, edgecolor='black', facecolor='gray')
    ax3.add_patch(rect_front)
    ax3.add_patch(rect_back)
    
    # Baffles vista superior
    for y_pos in baffle_positions:
        baffle_top = patches.Rectangle((wall_thickness, y_pos - baffle_thickness/2), 
                                     length - 2*wall_thickness, baffle_thickness, 
                                     linewidth=1, edgecolor='blue', facecolor='lightblue', alpha=0.7)
        ax3.add_patch(baffle_top)
    
    # Medidas superiores
    ax3.annotate('', xy=(0, -0.05), xytext=(length, -0.05), arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax3.text(length/2, -0.08, f'L1 = {length:.3f} m', ha='center', va='top', fontsize=10, color='red', fontweight='bold')
    
    ax3.annotate('', xy=(-0.05, 0), xytext=(-0.05, width), arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax3.text(-0.08, width/2, f'L2 = {width:.3f} m', ha='right', va='center', fontsize=10, color='red', fontweight='bold', rotation=90)
    
    ax3.set_xlim(-0.15, length+0.05)
    ax3.set_ylim(-0.15, width+0.05)
    ax3.grid(True, alpha=0.3)
    
    # ========== TABLA DE ESPECIFICACIONES ==========
    ax4 = axes[1, 1]
    ax4.set_title('ESPECIFICACIONES TÉCNICAS', fontweight='bold')
    ax4.axis('off')
    
    # Crear tabla de especificaciones
    specs = [
        ['PARÁMETRO', 'VALOR', 'UNIDAD'],
        ['Longitud total (L1)', f'{length:.3f}', 'm'],
        ['Ancho total (L2)', f'{width:.3f}', 'm'],
        ['Altura total (H)', f'{height:.3f}', 'm'],
        ['Número de baffles', f'{n_baffles}', 'unid'],
        ['Espesor de baffle', f'{baffle_thickness:.3f}', 'm'],
        ['Separación (2h)', f'{gap:.3f}', 'm'],
        ['Espesor de pared', f'{wall_thickness:.3f}', 'm'],
        ['Rendijas', f'{n_baffles + 1}', 'unid']
    ]
    
    table = ax4.table(cellText=specs[1:], colLabels=specs[0], loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Estilo de la tabla
    for i in range(len(specs)):
        for j in range(len(specs[0])):
            cell = table[(i, j)]
            if i == 0:  # Header
                cell.set_facecolor('#4472C4')
                cell.set_text_props(weight='bold', color='white')
            else:
                cell.set_facecolor('#F2F2F2' if i % 2 == 0 else 'white')
    
    plt.tight_layout()
    
    # Guardar planos técnicos
    output_path = f"{output_dir}/planos_tecnicos.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return output_path