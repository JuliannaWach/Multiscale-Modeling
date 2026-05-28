import pygame
from constants import BLACK, WHITE, GREY, DARK_GREY, PANEL_BACKGROUND_COLOR, GREEN, WINDOW_HEIGHT
from ui_elements import Button, InputBox, CycleSelector

BORDER = (0, 0, 0)

# --- Kolory zakladek
TAB_ACTIVE_COLOR = (210, 235, 210)
TAB_INACTIVE_COLOR = (190, 190, 190)
TAB_BORDER_COLOR = (120, 120, 120)

class SideMenu:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

        self.status_font = pygame.font.SysFont(None, 14)
        self.separator_font = pygame.font.SysFont(None, 13)
        self.bold_font = pygame.font.SysFont(None, 16, bold=True)

        self.current_layer = 0
        self.text_status = "Ustaw parametry i kliknij 'Generuj'"

        # --- Aktywna zakladka: "Cellular Automata" lub "Monte Carlo"
        self.active_tab = "Cellular Automata"

        pixel = x + 10
        element_width = width - 20
        half_width = (element_width - 6) // 2
        button_height = 26
        actual_y = y + 6

        tab_width = element_width // 2
        self.tab_ca_rect = pygame.Rect(pixel, actual_y, tab_width - 2, button_height)
        self.tab_mc_rect = pygame.Rect(pixel + tab_width + 2, actual_y, tab_width - 2, button_height)
        actual_y += button_height + 6

        self.button_generate = Button(pixel, actual_y, element_width, button_height, "Generuj przestrzen")
        actual_y += button_height + 3

        self.button_start = Button(pixel, actual_y, element_width, button_height, "Start symulacji")
        actual_y += button_height + 3

        self.button_reset = Button(pixel, actual_y, half_width, button_height, "Reset")
        self.button_pause = Button(pixel + half_width + 6, actual_y, half_width, button_height, "Pauza")
        actual_y += button_height + 3

        self.button_step = Button(pixel, actual_y, half_width, button_height, "Iteracja")
        self.button_save = Button(pixel + half_width + 6, actual_y, half_width, button_height, "Zapisz PNG")
        actual_y += button_height + 3

        self.button_3d = Button(pixel, actual_y, half_width, button_height, "Pokaz 3D")
        self.button_save_ovito = Button(pixel + half_width + 6, actual_y, half_width, button_height, "Zapisz OVITO")
        actual_y += button_height + 3

        self.button_statistics = Button(pixel, actual_y, element_width, button_height, "Statystyki mikrostruktury")
        actual_y += button_height + 6

        # --- Separator wspolny
        self.sep_common_y = actual_y
        actual_y += 8

        step = 38  # krok: 13px label + 24px pole + 1px odstep

        self.input_width = InputBox(pixel, actual_y, half_width, 24, "100", "Szerokosc X")
        self.input_height = InputBox(pixel + half_width + 6, actual_y, half_width, 24, "100", "Wysokosc Y")
        actual_y += step

        self.input_depth = InputBox(pixel, actual_y, element_width, 24, "1", "Glebokosc Z (1=2D)")
        actual_y += step + 2

        self.sel_seeding = CycleSelector(pixel, actual_y, element_width, 24,
                                         ["Losowe", "Jednorodne", "Reczne"], "Zarodkowanie")
        actual_y += step

        self.input_seeds = InputBox(pixel, actual_y, half_width, 24, "15", "Liczba ziaren")
        self.input_every = InputBox(pixel + half_width + 6, actual_y, half_width, 24, "1", "Kroki/klatke")
        actual_y += step

        self.input_rows = InputBox(pixel, actual_y, half_width, 24, "3", "Wiersze")
        self.input_cols = InputBox(pixel + half_width + 6, actual_y, half_width, 24, "3", "Kolumny")
        actual_y += step + 2

        self.sel_neighborhood = CycleSelector(pixel, actual_y, element_width, 24,
                                              ["Von Neumann", "Moore", "Pentagonalne", "Heksagonalne"],
                                              "Sasiedztwo (CA)")
        actual_y += step + 2

        self.sel_boundary_condition = CycleSelector(pixel, actual_y, element_width, 24,
                                                    ["Periodyczne", "Absorbujace"],
                                                    "Warunki Brzegowe")
        actual_y += step + 4

        # --- Separator po parametrach siatki
        self.sep_grid_y = actual_y
        actual_y += 8

        self.mc_params_start_y = actual_y

        self.input_j_gb = InputBox(pixel, actual_y, half_width, 24, "1", "J_gb x10 (energia granicy)")
        self.input_kt = InputBox(pixel + half_width + 6, actual_y, half_width, 24, "5", "kt x10 (stala term.)")
        actual_y += step

        self.input_mc_steps = InputBox(pixel, actual_y, element_width, 24, "50", "Maks. iteracji MC")
        actual_y += step + 2

        self.mc_params_end_y = actual_y

        self.sep_mc_y = actual_y
        actual_y += 8

        self.removal_start_y = actual_y

        self.removal_mode = CycleSelector(pixel, actual_y, element_width, 24,
                                          ["Do % wypelnienia", "N losowych ziaren", "Klikniecie myszka"],
                                          "Tryb usuwania ziaren")
        actual_y += step

        self.input_percent_fill = InputBox(pixel, actual_y, half_width, 24, "15", "% Wypelnienia")
        self.input_remove_n = InputBox(pixel + half_width + 6, actual_y, half_width, 24, "5", "Liczba N")
        actual_y += step

        self.button_remove = Button(pixel, actual_y, element_width, button_height, "Zastosuj usuniecie")
        actual_y += button_height + 3

        self.button_consolidate = Button(pixel, actual_y, element_width, button_height, "Scal pory (ID = -1)")
        actual_y += button_height + 4

        self.removal_end_y = actual_y

        # --- Tryb klikniecia myszka
        self.remove_click_mode = False

        # --- Separator po usuniecia
        self.sep_removal_y = actual_y
        actual_y += 8

        self.button_z_down = Button(pixel, actual_y, half_width, button_height, "<<")
        self.button_z_up = Button(pixel + half_width + 6, actual_y, half_width, button_height, ">>")
        self.button_z_rect = pygame.Rect(pixel, actual_y + button_height + 3, element_width, 18)
        actual_y += button_height + 24

        self.status_y = actual_y

        self.pixel = pixel
        self.element_width = element_width

    # --- Czy tryb Monte Carlo aktywny
    def is_mc_mode(self):
        return self.active_tab == "Monte Carlo"

    def inputs(self):
        base = [self.input_width, self.input_height, self.input_depth,
                self.input_seeds, self.input_rows, self.input_cols,
                self.input_every, self.input_percent_fill, self.input_remove_n]
        if self.is_mc_mode():
            base += [self.input_j_gb, self.input_kt, self.input_mc_steps]
        return base

    def selectors(self):
        return [self.sel_seeding, self.sel_neighborhood, self.sel_boundary_condition,
                self.removal_mode]

    def handle_event(self, event, simulation):
        # --- Klikniecia zakladek
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.tab_ca_rect.collidepoint(event.pos):
                self.active_tab = "Cellular Automata"
            elif self.tab_mc_rect.collidepoint(event.pos):
                self.active_tab = "Monte Carlo"

        for element in self.inputs() + self.selectors():
            element.handle_event(event)
        if self.button_z_down.is_clicked(event) and simulation:
            self.current_layer = max(0, self.current_layer - 1)
        if self.button_z_up.is_clicked(event) and simulation:
            self.current_layer = min(simulation.depth - 1, self.current_layer + 1)

    def get_parameters(self):
        seed_map = {"Losowe": "random", "Jednorodne": "uniform", "Reczne": "manual"}
        neighborhood_map = {
            "Von Neumann": "von_neumann", "Moore": "moore",
            "Pentagonalne": "pentagonal_random", "Heksagonalne": "hexagonal_random"
        }
        boundary_map = {"Periodyczne": "periodic", "Absorbujace": "absorbing"}

        params = {
            "width": self.input_width.get_int(100, 2, 500),
            "height": self.input_height.get_int(100, 2, 500),
            "depth": self.input_depth.get_int(1, 1, 50),
            "num_seeds": self.input_seeds.get_int(15, 1, 50000),
            "rows": self.input_rows.get_int(3, 1, 200),
            "cols": self.input_cols.get_int(3, 1, 200),
            "display_every": self.input_every.get_int(1, 1, 1000),
            "seeding_mode": seed_map[self.sel_seeding.value],
            "neighborhood_type": neighborhood_map[self.sel_neighborhood.value],
            "boundary_type": boundary_map[self.sel_boundary_condition.value],
        }
        return params

    def get_mc_parameters(self):
        # --- j_gb i kt przechowywane jako x10 (int), wewnetrznie dzielone przez 10
        j_gb_raw = self.input_j_gb.get_int(10, 1, 30)  # domyslnie 1.0 -> wartosc 10 -> 1.0
        kt_raw = self.input_kt.get_int(5, 1, 60)        # domyslnie 0.5 -> wartosc 5 -> 0.5
        mc_steps = self.input_mc_steps.get_int(50, 1, 9999)
        return {
            "j_gb": j_gb_raw / 10.0,
            "kt": kt_raw / 10.0,
            "mc_steps": mc_steps,
        }

    def draw_separator(self, surface, y):
        pygame.draw.line(surface, (190, 190, 190),
                         (self.x + 8, y), (self.x + self.width - 8, y), 1)

    def draw_tab(self, surface, rect, label, active):
        color = TAB_ACTIVE_COLOR if active else TAB_INACTIVE_COLOR
        pygame.draw.rect(surface, color, rect, border_radius=3)
        pygame.draw.rect(surface, TAB_BORDER_COLOR, rect, 1, border_radius=3)
        font = pygame.font.SysFont(None, 15, bold=True)
        txt = font.render(label, True, BLACK if active else (80, 80, 80))
        surface.blit(txt, txt.get_rect(center=rect.center))

    def draw(self, surface, simulation):
        pygame.draw.rect(surface, PANEL_BACKGROUND_COLOR, self.rect)
        pygame.draw.line(surface, (160, 160, 160),
                         (self.rect.x, 0), (self.rect.x, self.height), 1)

        self.draw_tab(surface, self.tab_ca_rect, "CA (Cellular Automata)", self.active_tab == "CA")
        self.draw_tab(surface, self.tab_mc_rect, "MC (Monte Carlo)", self.active_tab == "MC")

        # --- Wspolne przyciski
        self.button_generate.draw(surface)
        self.button_start.draw(surface)
        self.button_reset.draw(surface)
        self.button_pause.draw(surface)
        self.button_step.draw(surface)
        self.button_save.draw(surface)
        self.button_3d.draw(surface)
        self.button_save_ovito.draw(surface)
        self.button_statistics.draw(surface)

        self.draw_separator(surface, self.sep_common_y)

        # --- Parametry siatki
        for element in [self.input_width, self.input_height, self.input_depth,
                        self.sel_seeding, self.input_seeds, self.input_every,
                        self.input_rows, self.input_cols,
                        self.sel_neighborhood, self.sel_boundary_condition]:
            element.draw(surface)

        self.draw_separator(surface, self.sep_grid_y)

        # --- Parametry Monte Carlo (tylko w trybie MC)
        if self.is_mc_mode():
            font_mc = pygame.font.SysFont(None, 13, bold=True)
            header = font_mc.render("--- PARAMETRY MONTE CARLO ---", True, (30, 80, 160))
            surface.blit(header, (self.x + 10, self.sep_grid_y + 2))
            self.input_j_gb.draw(surface)
            self.input_kt.draw(surface)
            self.input_mc_steps.draw(surface)

            # --- Podpowiedz o wartosciach rzeczywistych
            j_val = self.input_j_gb.get_int(10, 1, 30) / 10.0
            kt_val = self.input_kt.get_int(5, 1, 60) / 10.0
            hint_font = pygame.font.SysFont(None, 13)
            hint = hint_font.render(f"J_gb = {j_val:.1f}  |  kt = {kt_val:.1f}", True, (60, 60, 150))
            surface.blit(hint, (self.x + 10, self.mc_params_end_y - 12))

        self.draw_separator(surface, self.sep_mc_y)

        # --- Sekcja usuwania ziaren
        font_header = pygame.font.SysFont(None, 13, bold=True)
        header = font_header.render("--- USUWANIE ZIAREN ---", True, (120, 50, 50))
        surface.blit(header, (self.x + self.pixel - self.x + 60, self.sep_mc_y + 2))

        self.removal_mode.draw(surface)
        self.input_percent_fill.draw(surface)
        self.input_remove_n.draw(surface)

        self.button_remove.active = self.remove_click_mode
        self.button_remove.draw(surface)

        consolidated = simulation is not None and simulation.has_consolidated_pore()
        self.button_consolidate.active = consolidated
        self.button_consolidate.draw(surface)

        # --- Info o wypelnieniu
        if simulation is not None:
            percent_fill = simulation.get_percent_fill()
            grain_count = len(simulation.get_unique_id_of_grain())
            percent_fill_font = pygame.font.SysFont(None, 13)
            percent_fill_text = percent_fill_font.render(
                f"Wypelnienie: {percent_fill:.1f}% | Ziaren: {grain_count}", True, (60, 60, 120)
            )
            surface.blit(percent_fill_text, (self.x + 10, self.sep_removal_y - 13))

        self.draw_separator(surface, self.sep_removal_y)

        # --- Warstwa Z
        layer3d = simulation is not None and simulation.depth > 1
        self.button_z_down.enabled = layer3d
        self.button_z_up.enabled = layer3d
        self.button_z_down.draw(surface)
        self.button_z_up.draw(surface)

        pygame.draw.rect(surface, WHITE, self.button_z_rect)
        pygame.draw.rect(surface, (160, 160, 160), self.button_z_rect, 1)
        if layer3d:
            z_label = f"Warstwa Z: {self.current_layer + 1} / {simulation.depth}"
        else:
            z_label = "Warstwa Z: 1 / 1 (2D)"
        txt_z = self.status_font.render(z_label, True, BLACK)
        surface.blit(txt_z, txt_z.get_rect(center=self.button_z_rect.center))

        # --- Pasek statusu (zawijany)
        words = self.text_status.split()
        lines, line = [], ""
        for word in words:
            test = (line + " " + word).strip()
            if self.status_font.size(test)[0] > self.width - 20:
                lines.append(line)
                line = word
            else:
                line = test
        if line:
            lines.append(line)
        for i, ln in enumerate(lines[:3]):
            s = self.status_font.render(ln, True, (70, 70, 70))
            surface.blit(s, (self.x + 10, self.status_y + i * 15))