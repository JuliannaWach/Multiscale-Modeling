import pygame
import numpy as np
import math

# --- Paleta kolorow okna statystyk
BACKGROUND_COLOR = (18, 22, 34)
PANEL_BACKGROUND_COLOR = (26, 32, 48)
PANEL_BORDER = (50, 70, 110)
TEXT_COLOR = (220, 230, 255)
TEXT_DIM = (130, 145, 180)
ACCENT_BLUE = (60, 130, 240)
ACCENT_GREEN = (50, 210, 130)
ACCENT_ORANGE = (240, 150, 40)
ACCENT_PINK = (230, 80, 160)
ACCENT_TEAL = (40, 200, 200)
WHITE = (255, 255, 255)
GRID_LINE = (40, 50, 70)

STATISTICS_WIDTH = 1100
STATISTICS_HEIGHT = 720

FONT_TITLE = None
FONT_HEADER = None
FONT_BODY = None
FONT_SMALL = None

def init_font():
    global FONT_TITLE, FONT_HEADER, FONT_BODY, FONT_SMALL
    if FONT_TITLE is None:
        FONT_TITLE = pygame.font.SysFont("consolas", 18, bold=True)
        FONT_HEADER = pygame.font.SysFont("consolas", 14, bold=True)
        FONT_BODY = pygame.font.SysFont("consolas", 12)
        FONT_SMALL = pygame.font.SysFont("consolas", 11)

# --- Pomocnicze funkcje rysujace
def draw_rounded_rect(surface, color, rect, radius=6, border_color=None, border_width=1):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border_color:
        pygame.draw.rect(surface, border_color, rect, border_width, border_radius=radius)

def draw_text(surface, text, font, color, x, y, align="left"):
    surf = font.render(str(text), True, color)
    if align == "center":
        x = x - surf.get_width() // 2
    elif align == "right":
        x = x - surf.get_width()
    surface.blit(surf, (x, y))
    return surf.get_height()

def draw_chart_bar(surface, rect, data_label, data_value, color, title="",
                   format_of_value="{:.0f}", y_label=""):
    x, y, width, height = rect.x, rect.y, rect.width, rect.height
    pad = 8
    top_pad = 24 if title else 8
    bottom_pad = 28
    left_pad = 46

    if title:
        draw_text(surface, title, FONT_HEADER, TEXT_COLOR,
                  x + width // 2, y + 4, align="center")

    chart_of_x = x + left_pad
    chart_of_y = y + top_pad
    chart_width = width - left_pad - pad
    chart_height = height - top_pad - bottom_pad

    if not data_value or max(data_value) == 0:
        draw_text(surface, "Brak danych", FONT_SMALL, TEXT_DIM,
                  x + width // 2, y + height // 2, align="center")
        return

    max_value = max(data_value) * 1.1

    # --- Linie siatki
    for i in range(5):
        gy = chart_of_y + chart_height - int(chart_height * i / 4)
        pygame.draw.line(surface, GRID_LINE, (chart_of_x, gy), (chart_of_x + chart_width, gy), 1)
        value = max_value * i / 4
        draw_text(surface, format_of_value.format(value), FONT_SMALL, TEXT_DIM, chart_of_x - 4, gy - 6, align="right")

    # --- Slupki
    number = len(data_value)
    bar_gap = max(1, chart_width // (number * 5))
    bar_width = max(1, chart_width - bar_gap * (number + 1) // number)
    for i, (label, val) in enumerate(zip(data_label, data_value)):
        bar_height = int(chart_height * val / max_value) if max_value > 0 else 0
        bar_x = chart_of_x + bar_gap + i * (bar_width + bar_gap)
        bar_y = chart_of_y + chart_of_y + chart_height - bar_height
        col = color if isinstance(color, tuple) else color[i % len(color)]
        pygame.draw.rect(surface, col, (bar_x, bar_y, bar_width, bar_height), border_radius=2)

        # --- Etykieta pod slupkiem
        if number <= 20:
            label_string = str(label)[:6]
            draw_text(surface, label_string, FONT_SMALL, TEXT_DIM,
                      bar_x + bar_width // 2, chart_of_y + chart_height + 3, align="center")

def draw_histogram(surface, rect, values, color, title="", bins=12):
    if not values:
        draw_text(surface, "Brak danych", FONT_SMALL, TEXT_DIM,
                  rect.x + rect.width // 2, rect.y + rect.height // 2, align="center")

        if title:
            draw_text(surface, title, FONT_HEADER, TEXT_COLOR,
                      rect.x + rect.width // 2, rect.y + 4, align="center")
        return

    array = np.array(values, dtype=float)
    counts, edges = np.histogram(array, bins=bins)
    labels = [f"{(edges[i] + edges[i+1]) / 2:.2f}" for i in range(len(counts))]
    draw_chart_bar(surface, rect, labels, counts.tolist(), color, title=title)

def draw_key_value_panel(surface, rect, data_dictionary, title=""):
    x, y, width, height = rect.x, rect.y, rect.width, rect.height
    draw_rounded_rect(surface, PANEL_BACKGROUND_COLOR, rect, radius=8, border_color=PANEL_BORDER)

    y_value = y + 8
    if title:
        draw_text(surface, title, FONT_HEADER, ACCENT_BLUE, x + 10, y_value)
        y_value += 20
        pygame.draw.line(surface, PANEL_BORDER, (x + 8, y_value - 2), (x + width - 8, y_value - 2), 1)

    row_height = 17
    available_rows = (y + height - y_value - 6) // row_height
    items = list(data_dictionary.items())[:available_rows]
    for key, value in items:
        draw_text(surface, f"{key}:", FONT_SMALL, TEXT_DIM, x + 10, y_value)
        draw_text(surface, str(value), FONT_SMALL, ACCENT_GREEN, x + width - 10, y_value, align="right")
        y_value += row_height

def draw_bar_char_in_mini_version(surface, rect, values, colors_list, labels, title=""):
    x, y, width, height = rect.x, rect.y, rect.width, rect.height
    draw_rounded_rect(surface, PANEL_BACKGROUND_COLOR, rect, radius=8, border_color=PANEL_BORDER)
    y_value = y + 8
    if title:
        draw_text(surface, title, FONT_HEADER, ACCENT_BLUE, x + 10, y_value)
        y_value += 20

    total = sum(values)
    if total == 0:
        draw_text(surface, "Brak danych", FONT_SMALL, TEXT_DIM, x + 10, y_value)
        return

    bar_height = 20
    bar_x = x + 10
    bar_width = width - 20
    for i, (value, color, label) in enumerate(zip(values, colors_list, labels)):
        fraction = value / total
        fill_width = int(bar_width * fraction)
        pygame.draw.rect(surface, color, (bar_x, y_value, fill_width, bar_height), border_radius=3)
        pygame.draw.rect(surface, PANEL_BORDER, (bar_x, y_value, bar_width, bar_height), 1, border_radius=3)
        label_string = f"{label}: {value} ({fraction*100:.1f}%)"
        draw_text(surface, label_string, FONT_SMALL, TEXT_COLOR, bar_x + 6, y_value + 4)
        y_value += bar_height + 6

def draw_shape_of_scatter(surface, rect, statistics_of_dictionary, x_key, y_key, title=""):
    x, y, width, height = rect.x, rect.y, rect.width, rect.height
    pad = 10
    top_pad = 22
    bottom_pad = 24
    left_pad = 36

    if title:
        draw_text(surface, title, FONT_HEADER, TEXT_COLOR,
                  x + width // 2, y + 4, align="center")

    center_x = x + left_pad
    center_y = y + top_pad
    center_width = width - left_pad - pad
    center_height = height - top_pad - bottom_pad

    if not statistics_of_dictionary:
        draw_text(surface, "Brak danych", FONT_SMALL, TEXT_DIM,
                  x + width // 2, y + height // 2, align="center")
        return

    x_string = [s[x_key] for s in statistics_of_dictionary.values() if x_key in s and y_key in s]
    y_string = [s[y_key] for s in statistics_of_dictionary.values() if x_key in s and y_key in s]

    if not x_string:
        return

    x_min, x_max = min(x_string), max(x_string)
    y_min, y_max = min(y_string), max(y_string)
    x_range = x_max - x_min if x_max != x_min else 1
    y_range = y_max - y_min if y_max != y_min else 1

    # --- Siatka
    for i in range(5):
        gx_version2 = center_x + int(center_width * i / 4)
        gy_version2 = center_y + int(center_height * i / 4)
        pygame.draw.line(surface, GRID_LINE, (gx_version2, center_y), (gx_version2, center_y + center_height), 1)
        pygame.draw.line(surface, GRID_LINE, (center_x, gy_version2), (center_x + center_width, gy_version2), 1)

    # --- Osie
    pygame.draw.line(surface, PANEL_BORDER, (center_x, center_y), (center_x, center_y + center_height), 2)
    pygame.draw.line(surface, PANEL_BORDER, (center_x, center_y + center_height), (center_x + center_width, center_y + center_height), 2)

    # --- Etykiety osi
    draw_text(surface, x_key, FONT_SMALL, TEXT_DIM, center_x + center_width // 2, center_y + center_height + 6, align="center")
    draw_text(surface, y_key, FONT_SMALL, TEXT_DIM, center_x - 34, center_y + center_height // 2, align="left")

    # --- Punkty
    for point_x, point_y in zip(x_string, y_string):
        string_of_x = center_x + int((point_x - x_min) / x_range * center_width)
        string_of_y = center_y + center_height - int((point_y - y_min) / y_range * center_height)
        pygame.draw.circle(surface, ACCENT_TEAL, (string_of_x, string_of_y), 3)
        pygame.draw.circle(surface, WHITE, (string_of_x, string_of_y), 3, 1)

def draw_gauge_bar(surface, rect, value, minimal_value, maximal_value, label, color, unit=""):
    x, y, width, height = rect.x, rect.y, rect.width, rect.height
    draw_rounded_rect(surface, PANEL_BACKGROUND_COLOR, rect, radius=6, border_color=PANEL_BORDER)

    draw_text(surface, label, FONT_SMALL, TEXT_DIM, x + 8, y + 5)

    bar_x = x + 8
    bar_y = y + 20
    bar_width = width - 16
    bar_height = 10

    pygame.draw.rect(surface, GRID_LINE, (bar_x, bar_y, bar_width, bar_height), border_radius=4)
    fraction = (value - minimal_value) / (maximal_value - minimal_value) if maximal_value != minimal_value else 0
    fraction = max(0, min(1, fraction))
    fill_width = int(bar_width * fraction)
    if fill_width > 0:
        pygame.draw.rect(surface, color, (bar_x, bar_y, fill_width, bar_height), border_radius=4)

    value_string = f"{value:.2f}{unit}"
    draw_text(surface, value_string, FONT_BODY, WHITE, x + width // 2, y + 34, align="center")

# --- Glowne okno statystyk
def show_statistics_window(statistics):
    sub_surface = pygame.display.set_mode((STATISTICS_WIDTH, STATISTICS_HEIGHT), pygame.NOFRAME | pygame.RESIZABLE)
    draw_statistics_surface(sub_surface, statistics)
    pygame.display.flip()

    # --- Petla zdarzen dla okna statystyk
    clock = pygame.time.Clock()
    running_statistics = True
    while running_statistics:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_statistics = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_s, pygame.K_q):
                    running_statistics = False
        clock.tick(30)

def render_statistics_to_surface(statistics, width=STATISTICS_WIDTH, height=STATISTICS_HEIGHT):
    init_font()
    surface = pygame.Surface((width, height))
    surface.fill(BACKGROUND_COLOR)
    draw_statistics_surface(surface, statistics)
    return surface

def draw_statistics_surface(surface, statistics):
    init_font()
    WIDTH, HEIGHT = surface.get_size()
    surface.fill(BACKGROUND_COLOR)

    pygame.draw.rect(surface, PANEL_BACKGROUND_COLOR, (0, 0, WIDTH, 38))
    draw_text(surface, "Statystyki Mikrostruktury", FONT_TITLE, ACCENT_BLUE, WIDTH // 2, 10, align="center")
    dimensions = statistics.grid_dimensions
    draw_text(surface, f"Siatka: {dimensions[0]}x{dimensions[1]}x{dimensions[2]} | "
              f"Tryb: {statistics.mode} | "
              f"Zarodkowanie: {statistics.seeding_mode} | "
              f"Sasiedztwo: {statistics.neighborhood_type}",
              FONT_SMALL, TEXT_DIM, WIDTH // 2, 24, align="center")
    pygame.draw.line(surface, PANEL_BORDER, (0, 38), (WIDTH, 38), 1)

    TOP = 44
    PAD = 8
    col_first_width = 230
    col_second_width = 260
    col_third_width = WIDTH - col_first_width - col_second_width - PAD * 4

    column_first_x = PAD
    column_first_hight_top = 300
    rect_key_value = pygame.Rect(column_first_x, TOP, col_first_width, column_first_hight_top)
    draw_rounded_rect(surface, PANEL_BACKGROUND_COLOR, rect_key_value, radius=8, border_color=PANEL_BORDER)
    draw_key_value_panel(surface, rect_key_value, statistics.summary_dictionary(), title="Podsumowanie")

    # --- Porowatosc
    rect_porosity = pygame.Rect(column_first_x, TOP + column_first_hight_top + PAD, col_first_width, 58)
    draw_gauge_bar(surface, rect_porosity, statistics.percent_porosity, 0, 100,
                   "Porowatosc", ACCENT_ORANGE, unit="%")

    # --- Proporcja ziarna / pory
    grain_cells = sum(statistics.grain_sizes) if statistics.grain_sizes else 0
    pore_cells = statistics.pore_cell_count
    rect_proportion = pygame.Rect(column_first_x, TOP + column_first_hight_top + PAD + 66, col_first_width,
                                  HEIGHT - TOP - column_first_hight_top - PAD - 66 - PAD)
    draw_bar_char_in_mini_version(
        surface, rect_proportion,
        [grain_cells, pore_cells],
        [ACCENT_GREEN, ACCENT_ORANGE],
        ["Ziarna", "Pory"],
        title="Sklad Mikrostruktury"
    )

    center_second_x = PAD + col_first_width + PAD
    row_height = (HEIGHT - TOP - PAD * 3) // 3

    rect_first_height = pygame.Rect(center_second_x, TOP, col_second_width, row_height)
    draw_rounded_rect(surface, PANEL_BACKGROUND_COLOR, rect_first_height, radius=8, border_color=PANEL_BORDER)
    draw_histogram_internal(surface, rect_first_height, statistics.grain_sizes, ACCENT_BLUE,
                            title="Rozklad rozmieszczenia ziaren", bins=12)

    rect_second_height = pygame.Rect(center_second_x, TOP + row_height + PAD, col_second_width, row_height)
    draw_rounded_rect(surface, PANEL_BACKGROUND_COLOR, rect_second_height, radius=8, border_color=PANEL_BORDER)
    value_zeta6 = statistics.get_shape_distribution_of_factor("zeta6")
    draw_histogram_internal(surface, rect_second_height, value_zeta6, ACCENT_TEAL,
                            title="Malinowska (z6, Wspolczynnik Kraglosci)", bins=10)

    rect_third_height = pygame.Rect(center_second_x, TOP + (row_height + PAD) * 2, col_second_width, row_height)
    draw_rounded_rect(surface, PANEL_BACKGROUND_COLOR, rect_third_height, radius=8, border_color=PANEL_BORDER)
    value_zeta2 = statistics.get_shape_distribution_of_factor("zeta2")
    draw_histogram_internal(surface, rect_second_height if not value_zeta6 else rect_third_height,
                            value_zeta2, ACCENT_PINK,
                            title="Wskaznik Ksztaltu (z2)", bins=10)
    if value_zeta6:
        draw_rounded_rect(surface, PANEL_BACKGROUND_COLOR, rect_third_height, radius=8, border_color=PANEL_BORDER)
        draw_histogram_internal(surface, rect_third_height, value_zeta2, ACCENT_PINK,
                                title="Wskaznik Ksztaltu (z2)", bins=10)

    center_third_x = center_second_x + col_second_width + PAD
    half_height = (HEIGHT - TOP - PAD) // 2

    # --- Scatter: zeta2 a zeta6
    scatter_of_rect = pygame.Rect(center_third_x, TOP, col_third_width, half_height - PAD)
    draw_rounded_rect(surface, PANEL_BACKGROUND_COLOR, scatter_of_rect, radius=8, border_color=PANEL_BORDER)
    draw_shape_of_scatter(surface, scatter_of_rect, statistics.shape_stats,
                          "zeta2", "zeta6", title="Ksztalt (z2) a Kraglosc (z6)")

    rect_size_grain = pygame.Rect(center_third_x, TOP + half_height, col_third_width, half_height - PAD)
    draw_rounded_rect(surface, PANEL_BACKGROUND_COLOR, rect_size_grain, radius=8, border_color=PANEL_BORDER)
    draw_classes_of_grain_size(surface, rect_size_grain, statistics)

    # --- ESC / S, aby zamknac (EXIT)
    pygame.draw.line(surface, PANEL_BORDER, (0, HEIGHT - 22), (WIDTH, HEIGHT - 22), 1)
    draw_text(surface, "ESC / S - Zamknij Statystyki | Kliknij poza obszarem okna, aby kontynuowac Symulacje",
              FONT_SMALL, TEXT_DIM, WIDTH // 2, HEIGHT - 16, align="center")

def draw_histogram_internal(surface, rect, values, color, title="", bins=10):
    x, y, width, height = rect.x, rect.y, rect.width, rect.height
    top_pad = 22 if title else 8
    bottom_pad = 24
    left_pad = 40
    pad = 6

    if title:
        draw_text(surface, title, FONT_HEADER, TEXT_COLOR, x + width // 2, y + 6, align="center")

    if not values:
        draw_text(surface, "Brak danych do wyswietlenia", FONT_SMALL, TEXT_DIM,
                  x + width // 2, y + height // 2, align="center")
        return

    array = np.array(values, dtype=float)
    counts, edges = np.histogram(array, bins=bins)

    chart_x = x + left_pad
    chart_y = y + top_pad
    chart_width = width - left_pad - pad
    chart_height = height - top_pad - bottom_pad

    if chart_width <= 0 or chart_height <= 0:
        return

    max_count = max(counts) if max(counts) > 0 else 1

    # --- Siatka
    for i in range(4):
        grid_y = chart_y + chart_height - int(chart_height * i / 3)
        pygame.draw.line(surface, GRID_LINE, (chart_x, grid_y), (chart_x + chart_width, grid_y), 1)
        draw_text(surface, f"{int(max_count * i / 3)}", FONT_SMALL, TEXT_DIM,
                  chart_x - 4, grid_y - 6, align="center")

    bin_width = chart_width // bins
    for i, count in enumerate(counts):
        bin_height = int(chart_height * count / max_count)
        bin_x = chart_x + i * bin_width
        bin_y = chart_y + chart_height - bin_height
        pygame.draw.rect(surface, color, (bin_x + 1, bin_y, bin_width - 2, bin_height), border_radius=2)

    # --- Etykiety osi X (pierwsze i ostatnie)
    draw_text(surface, f"{edges[0]:.1f}", FONT_SMALL, TEXT_DIM, chart_x, chart_y + chart_height + 4)
    draw_text(surface, f"{edges[-1]:.1f}", FONT_SMALL, TEXT_DIM,
              chart_x + chart_width, chart_y + chart_height + 4, align="right")

    # --- Srednia linia
    mean_value = float(np.mean(array))
    if edges[0] != edges[-1]:
        mean_x = chart_x + int((mean_value - edges[0]) / (edges[-1] - edges[0]) * chart_width)
        pygame.draw.line(surface, ACCENT_ORANGE,
                         (mean_x, chart_y), (mean_x, chart_y + chart_height), 2)
        draw_text(surface, f"average={mean_value:.1f}", FONT_SMALL, ACCENT_ORANGE,
                  mean_x + 2, chart_y + 2)

def draw_classes_of_grain_size(surface, rect, statistics):
    x, y, width, height = rect.x, rect.y, rect.width, rect.height
    draw_text(surface, "Klasy wielkosci ziaren", FONT_HEADER, TEXT_COLOR,
              x + width // 2, y + 6, align="center")

    if not statistics.grain_sizes:
        draw_text(surface, "Brak danych", FONT_SMALL, TEXT_DIM,
                  x + width // 2, y + height // 2, align="center")
        return

    mean = statistics.mean_grain_size
    small = statistics.get_count_of_small_grains(mean * 0.5)
    medium = len(statistics.grain_sizes) - small - statistics.get_count_of_large_grains(mean * 1.5)
    large = statistics.get_count_of_large_grains(mean * 1.5)
    total = len(statistics.grain_sizes)

    categories = [
        (f"Male (<{mean*0.5:.0f})", small, ACCENT_PINK),
        (f"Srednie", medium, ACCENT_BLUE),
        (f"Duze (>{mean*1.5:.0f})", large, ACCENT_GREEN),
    ]

    bar_area_width = width - 20
    bar_area_x = x + 10
    value_of_y = y + 28

    for label, count, color in categories:
        fraction = count / total if total > 0 else 0
        fill_width = int(bar_area_width * fraction)
        draw_text(surface, label, FONT_SMALL, TEXT_DIM, bar_area_x, value_of_y)
        value_of_y += 14
        pygame.draw.rect(surface, GRID_LINE, (bar_area_x, value_of_y, bar_area_width, 14), border_radius=4)
        if fill_width > 0:
            pygame.draw.rect(surface, color, (bar_area_x, value_of_y, fill_width, 14), border_radius=4)
        draw_text(surface, f"{count} ({fraction*100:.1f}%)", FONT_SMALL, WHITE,
                             bar_area_x + bar_area_width + 6, value_of_y + 2)
        value_of_y += 22

    # --- Dodatkowe informacje: Sredni wspolczynnik zeta6 oraz zeta1
    value_zeta6 = statistics.get_shape_distribution_of_factor("zeta6")
    value_zeta1 = statistics.get_shape_distribution_of_factor("zeta1")
    value_zeta10 = statistics.get_shape_distribution_of_factor("zeta10")

    value_of_y += 4
    pygame.draw.line(surface, PANEL_BORDER, (x + 8, value_of_y), (x + width - 8, value_of_y), 1)
    value_of_y += 6

    information = []
    if value_zeta6:
        information.append(f"Srednia Malinowska (z6): {np.mean(value_zeta6):.3f} ( = 1 dla kola)")
    if value_zeta1:
        information.append(f"Srednia Krawedz. (z1): {np.mean(value_zeta1):.3f}")
    if value_zeta10:
        information.append(f"Srednia d_min/d_max (z10): {np.mean(value_zeta10):.3f} ( = 1 dla kola)")
    if not information:
        information = ["Brak danych o ksztalcie (za malo komorek!)"]

    for line in information:
        draw_text(surface, line, FONT_SMALL, ACCENT_TEAL, x + 10, value_of_y)
        value_of_y += 16