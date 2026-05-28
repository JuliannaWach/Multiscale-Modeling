import numpy as np
import time
import tracemalloc
from collections import Counter

class MicrostructureStats:
    def __init__(self):
        self.reset()

    def reset(self):
        # --- Dane o generacji
        self.initial_grain_count = 0 # --- Liczba ziaren na poczatku (po zarodkowaniu)
        self.removed_grain_count = 0 # --- Liczba ziaren usunietych
        self.final_grain_count = 0 # --- Liczba ziaren finalnie (na koncu)
        self.removal_ratio = 0.0 # --- Stosunek usunietych ziaren / ziaren na poczatku

        # --- Porowatosc
        self.percent_porosity = 0.0 # --- Porowatosc w %
        self.pore_cell_count = 0 # --- Liczba komorek porow
        self.pore_sizes = [] # --- Rozmiar poszczegolnych porow (jezeli OSOBNE ID)

        # --- Czas trwania symulacji
        self.cellular_automata_time_in_seconds = 0.0
        self.monte_carlo_time_in_seconds = 0.0
        self.cellular_automata_steps = 0
        self.monte_carlo_steps = 0

        # --- Zuzycie pamieci
        self.memory_kb = 0.0
        self.grid_memory_kb = 0.0

        # --- Rozmiary ziaren (liczba komorek na ziarno)
        self.grain_sizes = []
        self.mean_grain_size = 0.0
        self.std_grain_size = 0.0
        self.min_grain_size = 0.0
        self.max_grain_size = 0.0
        self.median_grain_size = 0.0

        # --- Wspolczynniki ksztaltu (na wybranej warstwie dla KAZDEGO ziarna)
        self.shape_stats = {}

        # --- Tryb symulacji
        self.mode = "Cellular Automata"
        self.seeding_mode = "random"
        self.neighborhood_type = "von_neumann"
        self.boundary_type = "periodic"
        self.grid_dimensions = (0, 0, 1)

        # --- Markery czasu
        self.cellular_automata_start = None
        self.monte_carlo_start = None
        self.tracemalloc_started = False

    # --- Timery
    def start_cellular_automata_timer(self):
        self.cellular_automata_start = time.perf_counter()
        self.start_memory_tracking()

    def stop_cellular_automata_timer(self, steps):
        if self.cellular_automata_start:
            self.cellular_automata_time_in_seconds = time.perf_counter() - self.cellular_automata_start
            self.cellular_automata_start = None
        self.cellular_automata_steps = steps
        self.stop_memory_tracking()

    def start_monte_carlo_timer(self):
        self.monte_carlo_start = time.perf_counter()

    def stop_monte_carlo_timer(self, steps):
        if self.monte_carlo_start:
            self.monte_carlo_time_in_seconds = time.perf_counter() - self.monte_carlo_start
            self.monte_carlo_start = None
        self.monte_carlo_steps = steps

    def start_memory_tracking(self):
        try:
            if not self.tracemalloc_started:
                tracemalloc.start()
                self.tracemalloc_started = True
        except Exception:
            pass

    def stop_memory_tracking(self):
        try:
            if self.tracemalloc_started:
                _, peak = tracemalloc.get_traced_memory()
                self.memory_kb = peak / 1024
                tracemalloc.stop()
                self.tracemalloc_started = False
        except Exception:
            pass

    # --- Zbieranie danych
    def record_initial_state(self, simulation, parameters):
        self.initial_grain_count = len(simulation.get_unique_id_of_grain())
        self.removed_grain_count = 0
        self.seeding_mode = parameters.get("seeding_mode", "random")
        self.neighborhood_type = parameters.get("neighborhood_type", "von_neumann")
        self.boundary_type = parameters.get("boundary_type", "periodic")
        self.grid_dims = (parameters.get("width", 0), parameters.get("height", 0), parameters.get("depth", 1))

    def record_removal(self, n_removed):
        self.removed_grain_count += n_removed

    def update_from_simulation(self, simulation):
        grid = simulation.grid
        depth, heigth, width = grid.shape

        self.grid_memory_kb = grid.nbytes / 1024

        # --- Finalna liczba ziaren
        grain_indexes = set(int(value) for value in np.unique(grid) if value > 0)
        self.final_grain_count = len(grain_indexes)
        self.removal_ratio = (
            self.removed_grain_count / self.initial_grain_count
            if self.initial_grain_count > 0 else 0.0
        )

        # --- Porowatosc
        pore_mask = (grid == 0) | (grid == -1)
        self.pore_cell_count = int(np.count_nonzero(pore_mask))
        total = width * heigth * depth
        self.percent_porosity = (self.pore_cell_count / total) * 100.0

        # --- Rozmiary ziaren
        if grain_indexes:
            counts = Counter(int(value) for value in grid.flat if value > 0)
            self.grain_sizes = sorted(counts.values())
            array = np.array(self.grain_sizes, dtype=float)
            self.mean_grain_size = float(np.mean(array))
            self.std_grain_size = float(np.std(array))
            self.min_grain_size = int(np.min(array))
            self.max_grain_size = int(np.max(array))
            self.median_grain_size = float(np.median(array))
        else:
            self.grain_sizes = []
            self.mean_grain_size = self.std_grain_size = 0.0
            self.min_grain_size = self.max_grain_size = 0
            self.median_grain_size = 0.0

        # --- Wspolczynniki ksztaltu (wylacznie dla warstwy Z=0, czyli dla 2D slice)
        z_layer = grid[0]
        self.compute_shape_factor(z_layer)

    def compute_shape_factor(self, layer2d):
        height, width = layer2d.shape
        grain_indexes = set(int(value) for value in np.unique(layer2d) if value > 0)

        self.shape_stats = {}

        for grain_id in grain_indexes:
            mask = (layer2d == grain_id)
            cells = np.argwhere(mask) # --- (y, x)
            area = len(cells)
            if area < 4:
                continue

            # --- Obwod (liczba komorek granicznych)
            perimeter = self.compute_perimeter(mask, height, width)
            if perimeter == 0:
                continue

            # --- Bounding box
            ys, xs = cells[:, 0], cells[:, 1]
            y_minimal, y_maximal = int(ys.min()), int(ys.max())
            x_minimal, x_maximal = int(xs.min()), int(xs.max())
            bounding_box_width = x_maximal - x_minimal + 1
            bounding_box_height = y_maximal - y_minimal + 1

            # --- Srodek ciezkosci
            cy = float(np.mean(ys))
            cx = float(np.mean(xs))

            # --- Odelglosci od srodka ciezkosci do komorek konturu
            contour_of_cells = self.get_contour(mask, height, width)
            if len(contour_of_cells) < 2:
                continue
            distance = [np.sqrt((y - cy)**2 + (x - cx)**2) for y, x in contour_of_cells]
            distance_minimal = min(distance)
            distance_maximal = max(distance)

            # --- Wskaznik krawedziowy = obwod_prostokata / obwod_ziarna
            perimeter_bounding_box = 2 * (bounding_box_width + bounding_box_height)
            zeta1 = perimeter_bounding_box / perimeter if perimeter > 0 else 0

            # --- Wskaznik ksztaltu = obwod / (4 * sqrt(pole))
            zeta2 = perimeter / (4 * np.sqrt(area)) if area > 0 else 0

            # --- Malinowska = 2 * sqrt(pi * pole) / obwod ( = 1 dla kola)
            zeta6 = (2 * np.sqrt(np.pi * area)) / perimeter if perimeter > 0 else 0

            # --- Feret = max_szerokosc / max_wysokosc
            zeta7 = bounding_box_width / bounding_box_height if bounding_box_height > 0 else 0

            # --- d_min / d_max ( = 1 dla kola)
            zeta10 = distance_minimal / distance_maximal if distance_maximal > 0 else 0

            self.shape_stats[grain_id] = {
                "area": area,
                "perimeter": perimeter,
                "zeta1": zeta1,
                "zeta2": zeta2,
                "zeta6": zeta6,
                "zeta7": zeta7,
                "zeta10": zeta10,
            }

    def compute_perimeter(self, mask, height, width):
        count = 0
        ys, xs = np.where(mask)
        for y, x in zip(ys, xs):
            for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                ny, nx = y + dy, x + dx
                if ny < 0 or ny >= height or nx < 0 or nx >= width or not mask[ny, nx]:
                    count += 1
        return count

    def get_contour(self, mask, height, width):
        contour = []
        ys, xs = np.where(mask)
        for y, x in zip(ys, xs):
            for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
                ny, nx = y + dy, x + dx
                if ny < 0 or ny >= height or nx < 0 or nx >= width or not mask[ny, nx]:
                    contour.append((y, x))
                    break
        return contour

    # --- Metody pomocnicze i histogramy
    def get_grain_size_histogram(self, bins=10):
        if not self.grain_sizes:
            return [], []
        array = np.array(self.grain_sizes)
        counts, edges = np.histogram(array, bins=bins)
        return counts.tolist(), edges.tolist()

    def get_shape_distribution_of_factor(self, factor="zeta6"):
        values = [s[factor] for s in self.shape_stats.values() if factor in s]
        return values

    def get_count_of_small_grains(self, threshold=None):
        if not self.grain_sizes:
            return 0
        if threshold is None:
            threshold = self.mean_grain_size * 0.5
        return sum(1 for s in self.grain_sizes if s < threshold)

    def get_count_of_large_grains(self, threshold=None):
        if not self.grain_sizes:
            return 0
        if threshold is None:
            threshold = self.mean_grain_size * 1.5
        return sum(1 for s in self.grain_sizes if s > threshold)

    def summary_dictionary(self):
        return {
            "Poczatkowe ziarna": self.initial_grain_count,
            "Usuniete ziarna": self.removed_grain_count,
            "Finalne ziarna": self.final_grain_count,
            "Stosunek usuniecia": f"{self.removal_ratio:.1%}",
            "Porowatosc [%]": f"{self.percent_porosity:.2f}",
            "Sredni rozmiar ziarna": f"{self.mean_grain_size:.1f}",
            "Mediana rozmiaru ziarna": f"{self.median_grain_size:.1f}",
            "Odchylenie standardowe": f"{self.std_grain_size:.1f}",
            "Minimalny rozmiar ziarna": self.min_grain_size,
            "Maksymalny rozmiar ziarna": self.max_grain_size,
            "Czas Cellular Automata [s]": f"{self.cellular_automata_time_in_seconds:.3f}",
            "Czas Monte Carlo [s]": f"{self.monte_carlo_time_in_seconds:.3f}",
            "Pamiec szczytowa [kB]": f"{self.memory_kb:.1f}",
            "Pamiec siatki [kB]": f"{self.grid_memory_kb:.1f}",
        }