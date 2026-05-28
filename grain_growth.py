# --- Przestrzen 2D (depth=1), przestrzen 3D (depth>1)
# --- Typy zarodkowania:
# --- 1) "random" --- LOSOWE rozmieszczenie zarodkow
# --- 2) "uniform" --- ROWNOMIERNE rozmieszczenie w siatce rows x cols
# --- 3) "manual" --- PUSTA siatka, to znaczy ziarna sa dodawane PRZEZ UZYTKOWNIKA (myszka)
# --- Typy sasiedztw:
# --- 1) "von_neumann" --- 4 kierunki (w 2D) / 6 kierunków (w 3D)
# --- 2) "moore" --- 8 kierunkow (w 2D) / 26 kierunkow (w 3D)
# --- 3) "pentagonal_random" --- LOSOWO wybrany wzorzec 5-cio elementowy (w 2D)
# --- 4) "hexagonal_random" --- LOSOWO wybrany wzorzec 6-cio elementowy (w 2D)
# --- Warunki brzegowe:
# --- 1) "periodic" --- siatka "zawija sie" (z polskiego na nasze: lewa-prawa, gora-dol lacza sie)
# --- 2) "absorbing" --- komorki, ktore sa poza obszarem siatki --- sa ignorowane

import numpy as np
import random
from collections import Counter

class GrainGrowth:
    def __init__(self, width, height, depth=1,
                 num_seeds=15,
                 seeding_mode="random",
                 boundary_type="periodic",
                 neighborhood_type="von_neumann",
                 rows=3,
                 cols=3):
        self.width = width
        self.height = height
        self.depth = depth
        self.boundary_type = boundary_type
        self.neighborhood_type = neighborhood_type

        # --- Siatka w 3D: shape (depth, height, width), gdzie 0 = pusta komorka
        self.grid = np.zeros((depth, height, width), dtype=int)
        self.next_grain_id=1

        # --- Zarodkowanie zgodnie z wybranym typem: "random" lub "uniform"
        if seeding_mode == "random":
            self.seed_randomly(num_seeds)
        elif seeding_mode == "uniform":
            self.seed_uniformly(rows,cols)
        # "manual": pusta siatka, ziarna dodawane poprzez metode add_manual_seed()

    # --- Zarodkowanie
    def seed_randomly(self, num_seeds):
        # --- "randomly" zwiazane z LOSOWYM rozmieszczeniem zarodkow w CALEJ PRZESTRZENI
        placed = 0
        max_attempts = num_seeds * 1000
        for _ in range(max_attempts):
            if placed >= num_seeds:
                break
            x = random.randint(0, self.width - 1) # --- Skladowa X zwiazana z szerokoscia
            y = random.randint(0, self.height - 1) # --- Skladowa Y zwiazana z wysokoscia
            z = random.randint(0, self.depth - 1) # --- Skladowa Z zwiazana z glebokoscia
            if self.grid[z, y, x] == 0:
                self.grid[z, y, x] = self.next_grain_id
                self.next_grain_id += 1
                placed += 1

    def seed_uniformly(self, rows, cols):
        # --- Rownomierne rozmieszczenie --- siatka rows x cols NA KAZDA warstwe Z
        dx = max(1, self.width // cols)
        dy = max(1, self.height // rows)
        for z in range(self.depth):
            for i in range(rows):
                for j in range(cols):
                    x = j * dx + dx // 2
                    y = i * dy + dy // 2
                    if x < self.width and y < self.height and self.grid[z, y, x] == 0:
                        self.grid[z, y, x] = self.next_grain_id
                        self.next_grain_id += 1

    def add_manual_seed(self, x, y, z=0):
        # --- Dodanie POJEDYNCZEGO zarodka w podanym miejscu --- TRYB RECZNY
        if 0 <= z < self.depth and 0 <= y < self.height and 0 <= x < self.width:
            if self.grid[z, y, x] == 0:
                self.grid[z, y, x] = self.next_grain_id
                self.next_grain_id += 1
                return True # --- Zwraca True, jesli sie udalo
        return False # --- Zwraca False, jesli komorka jest zajeta / poza siatka

    # --- Sasiedztwo
    def get_directions(self):
        # --- Zwraca liste kierunkow (dx, dy, dz) dla wybranego sasiedztwa (Von Neumann / Pentagonal Random / Hexagonal Random)
        direction2d = (self.depth == 1)

        if self.neighborhood_type == "von_neumann":
            if direction2d:
                # --- w 2D --- 4 kierunki --- gora, dol, prawo, lewo:
                return[(0,-1,0), (0,1,0), (0,0,-1), (0,0,1)]
            else:
                # --- w 3D --- 6 kierunkow --- takie same jak wyzej + dodatkowo przod i tyl (os Z)
                return [(0,-1,0), (0,1,0), (0,0,-1), (0,0,1), (-1,0,0), (1,0,0)]

        elif self.neighborhood_type == "pentagonal_random":
            # --- Losowo wybrany jeden z 4 wzorcow 5-cio elementowych (asymetryczne sasiedztwo w 2D)
            patterns = [
                [(0,-1,0),(0,-1,1),(0,0,1),(0,1,1),(0,1,0)], # --- Prawy
                [(0,-1,0),(0,-1,-1),(0,0,-1),(0,1,-1),(0,1,0)], # --- Lewy
                [(0,-1,-1),(0,-1,0),(0,-1,1),(0,0,-1),(0,0,1)], # --- Gora
                [(0,1,-1),(0,1,0),(0,1,1),(0,0,-1),(0,0,1)], # --- Dol
            ]
            return random.choice(patterns) # --- Zwraca losowy wybrany pattern

        elif self.neighborhood_type == "hexagonal_random":
            # --- Losowo wybrany jeden z 4 wzorcow 6-cio elementowych (sasiedztwo heksagonalne w 2D)
            patterns = [
                [(0,-1,0),(0,0,-1),(0,0,1),(0,1,0),(0,-1,1),(0,1,-1)],
                [(0,-1,0),(0,0,-1),(0,0,1),(0,1,0),(0,-1,-1),(0,1,1)],
            ]
            return random.choice(patterns) # --- Zwraca losowy wybrany pattern

        elif self.neighborhood_type == "moore":
            if direction2d:
                # --- w 2D --- 8 kierunkow --- wszystkie komorki (4 boki + 4 ukosne)
                return [
                    (0,-1,-1),(0,-1,0),(0,-1,1), # --- Wiersz gorny
                    (0,0,-1),         (0,0,1), # --- Ten sam wiersz (lewo / prawo)
                    (0,1,-1),(0,1,0),(0,1,1), # --- Wiersz dolny
                ]
            else:
                # --- w 3D --- 26 kierunkow --- pelna kostka 3x3x3 minus srodek (0,0,0)
                return[
                    (dz, dy, dx)
                    for dz in [-1, 0, 1]
                    for dy in [-1, 0, 1]
                    for dx in [-1, 0, 1]
                    if not (dz == 0 and dy == 0 and dx == 0)
                ]

        # --- Domyslnie sasiedztwo von Neumanna (w 2D)
        return [(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]

    def get_neighbors(self, z, y, x):
        neighbors = []
        for dz, dy, dx in self.get_directions():
            nz, ny, nx = z + dz, y + dy, x + dx

            if self.boundary_type == "periodic":
                # --- Zawijanie siatki --- komorki poza siatka sa pomijane
                nz %= self.depth
                ny %= self.height
                nx %= self.width
                neighbors.append(self.grid[nz, ny, nx])

            elif 0 <= nz < self.depth and 0 <= ny < self.height and 0 <= nx < self.width:
                # --- Absorbujace --- komorki poza siatka sa pomijane
                neighbors.append(self.grid[nz, ny, nx])

        return neighbors

    # --- Krok symulacji
    # --- Przy remisie (kilka ziaren tak samo czesto) --- losujemy zwyciezce
    def step(self):
        new_grid = self.grid.copy() # --- Pracujemy na kopii, aby krok byl jednoczesny

        for z in range(self.depth):
            for y in range(self.height):
                for x in range(self.width):
                    if self.grid[z, y, x] != 0:
                        continue # --- Komorka juz zajeta!!! --- Pomijamy

                    neighbors = self.get_neighbors(z, y, x)
                    grain_neighbors = [n for n in neighbors if n > 0]

                    if grain_neighbors:
                        # --- Wybieramy NAJCZESCIEJ sasiadujace ziarno
                        counts = Counter(grain_neighbors)
                        max_count = max(counts.values())
                        candidates = [gid for gid, count in counts.items() if count == max_count]
                        new_grid[z, y, x] = random.choice(candidates)

        self.grid = new_grid

    def is_complete(self):
        return bool(np.all(self.grid > 0)) # --- Zwraca True, gdy nie ma zadnej pustej komorki

    def get_layer(self, z=0):
        # --- Zwraca warstwe Z jako siatka 2D (wizualizacja 3D warstwa po warstwie)
        z = max(0, min(z, self.depth - 1))
        return self.grid[z]

    # --- Usuwanie ziaren z przestrzeni
    def get_percent_fill(self):
        total = self.width * self.height * self.depth
        filled = int(np.count_nonzero(self.grid))
        return (filled / total) * 100.0 # --- Zwraca % wypelnienia siatki (ile komorek != 0)

    def step_until_fill(self, percent_target):
        # --- Wykonanie krokow symulacji, az do osiagniecia zadanego % wypelnienia (fill)
        steps = 0 # --- Zwraca liczbe wykonanych krokow

        while self.get_percent_fill() < percent_target and not self.is_complete():
            self.step()
            steps += 1
        return steps

    PORE_ID = -1 # --- Stale ID scalonego poru, po usunieciu ziaren wszystkie puste komorki (0) dostaja wspolny ID = -1

    def get_unique_id_of_grain(self):
        # --- Zwraca zbior wszystkich UNIKALNYCH ID ziaren (bez 0 = pustej komorki)
        return set(int(grain) for grain in np.unique(self.grid) if grain > 0)

    def consolidate_pore(self):
        # --- Scalenie WSZYSTKICH pustych komorek (0) w jeden por ID = PORE_ID (-1)
        # --- Wywolanie po zakonczeniu usuwania ziaren / rozrostu do zadanego %
        self.grid[self.grid == 0] = self.PORE_ID

    def deconsolidate_pore(self):
        # --- Przywrocenie pustych komorek (0) --- metoda odwrotna do consolidate_pore()
        # --- Wznowienie rozrostu po scaleniu porow
        self.grid[self.grid == self.PORE_ID] = 0

    def has_consolidated_pore(self):
        # --- Zwraca True, jesli pory zostaly scalone (PORE_ID w siatce)
        return bool(np.count_nonzero(self.grid == self.PORE_ID))

    def get_count_pore(self):
        # --- Zwraca liczbe komorek nalezacych do scalonego poru
        return int(np.count_nonzero(self.grid == self.PORE_ID))

    def remove_grain_by_id(self, grain_id):
        # --- Jesli pory sa SCALONE --- usuniete komorki dostaje PORE_ID (-1)
        # --- Jesli pory sa NIESCALONE --- usuniete komorki dostaja 0 (puste)
        if grain_id > 0 and grain_id in self.get_unique_id_of_grain():
            new_value = self.PORE_ID if self.has_consolidated_pore() else 0
            self.grid[self.grid == grain_id] = new_value
            return True
        return False

    def remove_n_random_of_grain(self, number):
        # --- Usuwa N losowo wybranych ziaren
        # --- Usuniete komorki staja sie 0 lub PORE_ID
        index = list(self.get_unique_id_of_grain()) # --- Zwraca liste usunietych ID
        if not index:
            return []
        number = min(number, len(index))
        chosen = random.sample(index, number)
        new_value = self.PORE_ID if self.has_consolidated_pore() else 0
        for grain_id in chosen:
            self.grid[self.grid == grain_id] = new_value
        return chosen

    def get_grain_at(self, x, y, z=0):
        # --- Zwraca ID ziarna w danej komorce (0 = puste, -1 = scalony por, >0 = ziarno)
        if 0 <= z < self.depth and 0 <= y < self.height and 0 <= x < self.width:
            return int(self.grid[z, y, x])
        return 0