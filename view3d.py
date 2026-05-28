import multiprocessing
import numpy as np

def worker_function(grid, color_map):
    try:
        import matplotlib
        matplotlib.use('TkAgg') # --- Backend GUI
    except Exception:
        try:
            import matplotlib
            matplotlib.use('Qt5Agg')
        except Exception:
            pass

    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D

    except ImportError:
        print("[3D] Brak biblioteki matplotlib. Zainstaluj poleceniem: pip install matplotlib")
        return

    depth, height, width = grid.shape

    step = max(1, max(depth, height, width) // 25)

    grid_g = grid[::step, ::step, ::step]
    depth_d, height_h, width_w = grid_g.shape

    # --- Macierz bool --- True = komorka zajeta (zostanie narysowana jako voxel)
    filled = grid_g > 0

    # --- Macierz kolorow RGBA (float 0 - 1) dla matplotlib
    colors = np.zeros((*filled.shape, 4), dtype=float)
    for z in range(depth_d):
        for y in range(height_h):
            for x in range(width_w):
                gid = grid_g[z, y, x]
                if gid > 0:
                    red, green, blue = color_map.get(gid, (150, 150, 150))
                    colors[z, y, x] = (red/255.0, green/255.0, blue/255.0, 0.95)

    fig = plt.figure(figsize=(8, 7))
    fig.patch.set_facecolor('#1a1a2e')
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor('#1a1a2e')

    ax.voxels(filled, facecolors=colors, edgecolors=None)

    ax.set_title("Rozrost Ziaren - Widok 3D", color='white', fontsize=12, pad=10)
    ax.set_xlabel('X', color='white')
    ax.set_ylabel('Y', color='white')
    ax.set_zlabel('Z', color='white')
    ax.tick_params(colors='white')

    plt.tight_layout()
    plt.show()

def show3dwindow(grid, color_map):
    # --- Multiprocessing wymaga, aby dane byly serializowane --- numpy array oraz dict sa OK
    # --- daemon=True --- proces zamknie sie razem z programem (nie czekamy na zakonczenie)
    process = multiprocessing.Process(target=worker_function, args=(grid, color_map), daemon=True)
    process.start()