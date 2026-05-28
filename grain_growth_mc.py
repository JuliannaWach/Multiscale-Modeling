# --- Krok 1: Mikrostruktura poczatkowa wygenerowana algorytmem CA (GrainGrowth)
# --- Krok 2: Losowy wybor komorki w przestrzeni (losowanie bez zwracania w ramach jednej iteracji MC)
# --- Krok 3: Obliczenie energii wylosowanej komorki: E = J_gb * sum(1 - delta(S_i, S_j))
#             J_gb < 1.0 --- energia granicy ziarna
#             Delta Kroneckera: delta(S_i, S_j) = 1 jesli S_i == S_j, inaczej 0
# --- Krok 4: Losowy wybor nowego stanu/ID z sasiadow komorki
# --- Krok 5: Obliczenie energii dla nowego stanu i zmiany energii: dE = E_after - E_before
# --- Krok 6: Akceptacja zmiany z prawdopodobienstwem p:
#             p = 1           jesli dE <= 0
#             p = exp(-dE/kt) jesli dE > 0
#             kt --- stala (zakres 0.1 - 6)

import numpy as np
import random
import math

class GrainGrowthMC:
    def __init__(self, grain_growth_ca, j_gb=1.0, kt=0.5, boundary_type=None):
        self.grid = grain_growth_ca.grid.copy()
        self.width = grain_growth_ca.width
        self.height = grain_growth_ca.height
        self.depth = grain_growth_ca.depth
        self.j_gb = j_gb
        self.kt = kt
        self.boundary_type = boundary_type if boundary_type else grain_growth_ca.boundary_type
        self.mc_step_count = 0  # --- Licznik iteracji MC

    # --- Pobierz sasiadow komorki (Moore: 8 w 2D, 26 w 3D)
    def _get_moore_neighbors_ids(self, z, y, x):
        neighbors = []
        is_2d = (self.depth == 1)

        if is_2d:
            deltas = [(dy, dx) for dy in [-1, 0, 1] for dx in [-1, 0, 1] if not (dy == 0 and dx == 0)]
            for dy, dx in deltas:
                ny, nx = y + dy, x + dx
                if self.boundary_type == "periodic":
                    ny %= self.height
                    nx %= self.width
                    neighbors.append(self.grid[z, ny, nx])
                elif 0 <= ny < self.height and 0 <= nx < self.width:
                    neighbors.append(self.grid[z, ny, nx])
        else:
            deltas = [
                (dz, dy, dx)
                for dz in [-1, 0, 1]
                for dy in [-1, 0, 1]
                for dx in [-1, 0, 1]
                if not (dz == 0 and dy == 0 and dx == 0)
            ]
            for dz, dy, dx in deltas:
                nz, ny, nx = z + dz, y + dy, x + dx
                if self.boundary_type == "periodic":
                    nz %= self.depth
                    ny %= self.height
                    nx %= self.width
                    neighbors.append(self.grid[nz, ny, nx])
                elif 0 <= nz < self.depth and 0 <= ny < self.height and 0 <= nx < self.width:
                    neighbors.append(self.grid[nz, ny, nx])

        return neighbors

    # --- Obliczenie energii komorki (Krok 3 algorytmu MC)
    # --- E = J_gb * sum(1 - delta(S_i, S_j)) dla wszystkich sasiadow
    def _compute_energy(self, z, y, x, state):
        neighbors = self._get_moore_neighbors_ids(z, y, x)
        energy = 0.0
        for neighbor_state in neighbors:
            if neighbor_state > 0:  # --- Ignorujemy puste komorki (pory)
                # --- Delta Kroneckera: 1 jesli stany takie same, 0 jesli rozne
                delta = 1 if state == neighbor_state else 0
                energy += self.j_gb * (1 - delta)
        return energy

    # --- 1 iteracja Monte Carlo = losowe przejrzenie WSZYSTKICH komorek (bez zwracania)
    def step(self):
        total_cells = self.width * self.height * self.depth

        # --- Losowa kolejnosc indeksow komorek (bez zwracania)
        indices = list(range(total_cells))
        random.shuffle(indices)

        for idx in indices:
            # --- Zamiana indeksu 1D -> 3D
            x = idx % self.width
            y = (idx // self.width) % self.height
            z = idx // (self.width * self.height)

            current_state = int(self.grid[z, y, x])

            # --- Pomijamy puste komorki (0) i pory (-1)
            if current_state <= 0:
                continue

            # --- Krok 4: Losowy wybor nowego stanu z sasiadow
            neighbors = self._get_moore_neighbors_ids(z, y, x)
            grain_neighbors = [n for n in neighbors if n > 0]

            if not grain_neighbors:
                continue

            new_state = random.choice(grain_neighbors)

            if new_state == current_state:
                continue  # --- Brak zmiany --- pomijamy

            # --- Krok 5: Obliczenie energii przed i po zmianie
            e_before = self._compute_energy(z, y, x, current_state)
            e_after = self._compute_energy(z, y, x, new_state)
            delta_e = e_after - e_before

            # --- Krok 6: Akceptacja zmiany wg kryterium Metropolisa
            if delta_e <= 0:
                # --- Zawsze akceptujemy (energia maleje lub nie zmienia sie)
                self.grid[z, y, x] = new_state
            else:
                # --- Akceptacja z prawdopodobienstwem exp(-dE / kt)
                prob = math.exp(-delta_e / self.kt)
                if random.random() < prob:
                    self.grid[z, y, x] = new_state

        self.mc_step_count += 1

    def get_layer(self, z=0):
        z = max(0, min(z, self.depth - 1))
        return self.grid[z]

    def get_grain_count(self):
        unique = set(int(v) for v in np.unique(self.grid) if v > 0)
        return len(unique)

    def get_unique_ids(self):
        return set(int(v) for v in np.unique(self.grid) if v > 0)

    def get_unique_id_of_grain(self):
        return set(int(v) for v in np.unique(self.grid) if v > 0)

    def get_percent_fill(self):
        total = self.width * self.height * self.depth
        filled = int(np.count_nonzero(self.grid > 0))
        return (filled / total) * 100.0

    def is_complete(self):
        return False

    def has_consolidated_pore(self):
        return bool(np.count_nonzero(self.grid == -1))

    def get_count_pore(self):
        return int(np.count_nonzero(self.grid == -1))

    def consolidate_pore(self):
        self.grid[self.grid == 0] = -1

    def deconsolidate_pore(self):
        self.grid[self.grid == -1] = 0

    def get_grain_at(self, x, y, z=0):
        if 0 <= z < self.depth and 0 <= y < self.height and 0 <= x < self.width:
            return int(self.grid[z, y, x])
        return 0

    def remove_grain_by_id(self, grain_id):
        if grain_id > 0 and grain_id in self.get_unique_id_of_grain():
            new_value = -1 if self.has_consolidated_pore() else 0
            self.grid[self.grid == grain_id] = new_value
            return True
        return False

    def remove_n_random_of_grain(self, number):
        index = list(self.get_unique_id_of_grain())
        if not index:
            return []
        number = min(number, len(index))
        chosen = random.sample(index, number)
        new_value = -1 if self.has_consolidated_pore() else 0
        for grain_id in chosen:
            self.grid[self.grid == grain_id] = new_value
        return chosen

    def step_until_fill(self, percent_target):
        steps = 0
        while self.get_percent_fill() < percent_target and steps < 9999:
            self.step()
            steps += 1
        return steps