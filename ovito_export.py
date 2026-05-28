# --- Zapis mikrostruktury (material porowaty) do pliku TXT w formacie OVITO XYZ
# --- Format OVITO (Extended XYZ / kolumnowy):
# --- Linia 1: liczba czastek (atomow / komorek)
# --- Linia 2: pusta (lub komentarz)
# --- Kolejne linie: X Y Z ParticleIdentifier
# --- Zapis dotyczy TYLKO ziaren (ID > 0).
# --- Pory (ID = 0 lub ID = -1) sa POMIJANE --- material porowaty = brak atomow w porach

import numpy as np
from datetime import datetime

def save_to_ovito(grid, filename=None, only_grains=True):
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"porous_material_{timestamp}_ovito.txt"
    depth, height, width = grid.shape

    # --- Zbieranie komorek do zapisu
    particles = []
    for z in range(depth):
        for y in range(height):
            for x in range(width):
                grain_id = int(grid[z, y, x])

                if only_grains:
                    # --- Material porowaty: zapisujemy TYLKO ziarna (ID > 0)
                    if grain_id > 0:
                        particles.append((x, y, z, grain_id))
                else:
                    # --- Pelny zapis: wszystkie komorki
                    # --- Pory (0 i -1) dostaja ID = 0 w pliku
                    out_id = grain_id if grain_id > 0 else 0
                    particles.append((x, y, z, out_id))

    num_particles = len(particles)

    with open(filename, 'w') as f:
        # --- Linia 1: liczba czastek
        f.write(f"{num_particles}\n")
        # --- Linia 2: pusta (komentarz opcjonalny)
        f.write(f"\n")
        # --- Dane: X Y Z ParticleIdentifier
        for (x, y, z, pid) in particles:
            f.write(f"{x} {y} {z} {pid}\n")

    return filename

def save_porous_material(grain_growth_obj, filename=None):

    grid = grain_growth_obj.grid
    depth, height, width = grid.shape
    total = width * height * depth

    num_grains_cells = int(np.count_nonzero(grid > 0))
    num_pore_cells = total - num_grains_cells
    porosity = (num_pore_cells / total) * 100.0

    saved_file = save_to_ovito(grid, filename=filename, only_grains=True)

    return saved_file, num_grains_cells, num_pore_cells, porosity