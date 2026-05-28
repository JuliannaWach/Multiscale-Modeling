import sys
import random
import pygame
from datetime import datetime

from constants import *
from grain_growth import GrainGrowth
from grain_growth_mc import GrainGrowthMC
from menu import SideMenu
from view3d import show3dwindow
from ovito_export import save_porous_material
from microstucture_stats import MicrostructureStats
from stats_window import render_statistics_to_surface

# --- Kolory ziaren
PORE_COLOR = (40, 20, 10)
colors = {0: WHITE, -1: PORE_COLOR}

def get_color(gid):
    if gid not in colors:
        colors[gid] = (
            random.randint(50, 220),
            random.randint(50, 220),
            random.randint(50, 220),
        )
    return colors[gid]

def reset_colors():
    colors.clear()
    colors[0] = WHITE
    colors[-1] = PORE_COLOR

def get_color_map():
    return dict(colors)

def draw_grid(surface, grid_layer, canvas_rect, cell_size):
    rows, cols = grid_layer.shape
    for y in range(rows):
        for x in range(cols):
            color = get_color(grid_layer[y, x])
            rect = pygame.Rect(
                canvas_rect.x + x * cell_size,
                canvas_rect.y + y * cell_size,
                cell_size, cell_size
            )
            pygame.draw.rect(surface, color, rect)

def compute_cell_size(canvas_width, canvas_height, grid_width, grid_height):
    return max(1, min(canvas_width // grid_width, canvas_height // grid_height))

def canvas_to_grid(mouse_position, canvas_rect, cell_size, grid_width, grid_height):
    mouse_x, mouse_y = mouse_position
    if not canvas_rect.collidepoint(mouse_x, mouse_y):
        return None, None
    gx = (mouse_x - canvas_rect.x) // cell_size
    gy = (mouse_y - canvas_rect.y) // cell_size
    if 0 <= gx < grid_width and 0 <= gy < grid_height:
        return gx, gy
    return None, None

def save_to_png(simulation, layer):
    grid_layer = simulation.get_layer(layer)
    height, width = grid_layer.shape
    scale = max(1, min(4, 800 // width, 800 // height))
    surf = pygame.Surface((width * scale, height * scale))
    for y in range(height):
        for x in range(width):
            color = get_color(grid_layer[y, x])
            pygame.draw.rect(surf, color, (x * scale, y * scale, scale, scale))
    filename = f"rozrost_ziaren_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pygame.image.save(surf, filename)
    return filename

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Modelowanie Wieloskalowe - Rozrost Ziaren CA/MC 2D/3D")
    clock = pygame.time.Clock()

    canvas_rect = pygame.Rect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)
    menu = SideMenu(CANVAS_WIDTH, 0, MENU_WIDTH, WINDOW_HEIGHT)

    # --- Stan programu
    simulation = None      # obiekt GrainGrowth (Cellular Automata)
    mc_simulation = None   # obiekt GrainGrowthMC (Monte Carlo, tworzony na podstawie Cellular Automata)
    cell_size = 7
    running = False
    step_count = 0
    display_every = 1
    manual_mode = False
    last_parameters = None
    last_mc_params = None
    statistics = MicrostructureStats()
    statistics_surface = None
    show_statistics = False

    while True:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_SPACE:
                    active_sim = mc_simulation if mc_simulation else simulation
                    if active_sim:
                        running = not running
                        menu.text_status = ("Symulacja dziala..." if running
                                            else "Pauza (SPACJA = wznow)")

                if event.key == pygame.K_r and last_parameters is not None:
                    reset_colors()
                    simulation = GrainGrowth(**last_parameters)
                    mc_simulation = None
                    cell_size = compute_cell_size(
                        canvas_rect.width, canvas_rect.height,
                        last_parameters["width"], last_parameters["height"]
                    )
                    menu.current_layer = 0
                    running = False
                    step_count = 0
                    manual_mode = (last_parameters["seeding_mode"] == "manual")
                    menu.text_status = "Reset! Kliknij Start"

            menu.handle_event(event, mc_simulation if mc_simulation else simulation)

            if menu.button_generate.is_clicked(event):
                parameters = menu.get_parameters()
                display_every = parameters.pop("display_every")
                reset_colors()
                statistics = MicrostructureStats()
                statistics.mode = "Cellular Automata"
                statistics.start_cellular_automata_timer()
                simulation = GrainGrowth(**parameters)
                statistics.record_initial_state(simulation, parameters)
                mc_simulation = None
                last_parameters = parameters.copy()
                cell_size = compute_cell_size(
                    canvas_rect.width, canvas_rect.height,
                    parameters["width"], parameters["height"]
                )
                menu.current_layer = 0
                running = False
                step_count = 0
                show_statistics = False
                statistics_surface = None
                manual_mode = (parameters["seeding_mode"] == "manual")

                if menu.is_mc_mode():
                    menu.text_status = ("Wygenerowano mikrostrukture Cellular Automata. "
                                        "Kliknij Start, aby uruchomic Monte Carlo.")
                elif manual_mode:
                    menu.text_status = "Kliknij na siatke, aby dodac ziarna. Start uruchamia."
                else:
                    menu.text_status = "Generowanie zakonczone. Kliknij Start."

            if menu.button_start.is_clicked(event):
                if menu.is_mc_mode():
                    # --- Tryb MC: najpierw rozrost Cellular Automata do pelnego wypelnienia, potem Monte Carlo
                    if simulation is not None:
                        # --- Jesli Cellular Automata nie jest kompletna --- rozrastamy do konca
                        if not simulation.is_complete():
                            while not simulation.is_complete():
                                simulation.step()
                                step_count += 1
                            statistics.stop_monte_carlo_timer(step_count)
                            menu.text_status = "CA ukonczone. Startuje MC..."

                        mc_params = menu.get_mc_parameters()
                        last_mc_params = mc_params.copy()
                        mc_simulation = GrainGrowthMC(
                            grain_growth_ca=simulation,
                            j_gb=mc_params["j_gb"],
                            kt=mc_params["kt"],
                            boundary_type=simulation.boundary_type,
                        )
                        statistics.mode = "Cellular Automata + Monte Carlo"
                        statistics.start_monte_carlo_timer()
                        step_count = 0
                        running = True
                        menu.text_status = (f"MC dziala... J_gb={mc_params['j_gb']:.1f}, "
                                            f"kt={mc_params['kt']:.1f}")
                    else:
                        menu.text_status = "Najpierw wygeneruj przestrzen!"
                else:
                    # --- Tryb Cellular Automata
                    if simulation:
                        running = True
                        manual_mode = False
                        menu.text_status = "Symulacja Cellular Automata dziala..."

            if menu.button_reset.is_clicked(event) and last_parameters is not None:
                reset_colors()
                statistics = MicrostructureStats()
                statistics.mode = "Cellular Automata"
                statistics.start_cellular_automata_timer()
                simulation = GrainGrowth(**last_parameters)
                statistics.record_initial_state(simulation, last_parameters)
                mc_simulation = None
                cell_size = compute_cell_size(
                    canvas_rect.width, canvas_rect.height,
                    last_parameters["width"], last_parameters["height"]
                )
                menu.current_layer = 0
                running = False
                step_count = 0
                manual_mode = (last_parameters["seeding_mode"] == "manual")
                menu.text_status = "Reset! Kliknij Start."

            if menu.button_statistics.is_clicked(event):
                active_sim = mc_simulation if mc_simulation else simulation
                if active_sim:
                    statistics.update_from_simulation(active_sim)
                    statistics_surface = render_statistics_to_surface(statistics, CANVAS_WIDTH, CANVAS_HEIGHT)
                    show_statistics = not show_statistics
                    menu.text_status = ("Statystyki aktywne. Kliknij ponownie aby wylaczyc."
                                        if show_statistics else "Statystyki ukryte.")
                else:
                    menu.text_status = "Brak symulacji — wygeneruj najpierw przestrzen!"

            if menu.button_pause.is_clicked(event):
                active_sim = mc_simulation if mc_simulation else simulation
                if active_sim:
                    running = not running
                    menu.text_status = ("Symulacja dziala..." if running else "Pauza")

            if menu.button_step.is_clicked(event):
                if menu.is_mc_mode() and mc_simulation is not None:
                    mc_simulation.step()
                    step_count += 1
                    running = False
                    menu.text_status = f"Iteracja Monte Carlo: {step_count}"
                elif simulation and not simulation.is_complete():
                    simulation.step()
                    step_count += 1
                    running = False
                    menu.text_status = f"Krok Cellular Automata: {step_count}"

            if menu.button_save.is_clicked(event):
                active_sim = mc_simulation if mc_simulation else simulation
                if active_sim:
                    function_save = save_to_png(active_sim, menu.current_layer)
                    menu.text_status = f"Zapisano: {function_save}"

            if menu.button_save_ovito.is_clicked(event):
                active_sim = mc_simulation if mc_simulation else simulation
                if active_sim:
                    fn, n_grains, n_pores, porosity = save_porous_material(active_sim)
                    menu.text_status = (f"OVITO zapisano: {fn} | "
                                        f"Porowatosc: {porosity:.1f}% | "
                                        f"Ziaren: {len(active_sim.get_unique_id_of_grain())}")
                else:
                    menu.text_status = "Brak symulacji do zapisania!"

            if menu.button_3d.is_clicked(event):
                active_sim = mc_simulation if mc_simulation else simulation
                if active_sim and active_sim.depth > 1:
                    menu.text_status = "Otwieranie okna 3D..."
                    show3dwindow(active_sim.grid.copy(), get_color_map())
                elif active_sim:
                    menu.text_status = "3D wymaga Glebokosci Z > 1"

            active_sim_for_removal = mc_simulation if mc_simulation else simulation

            if menu.button_remove.is_clicked(event) and active_sim_for_removal:
                mode = menu.removal_mode.value
                running = False

                if mode == "Do % wypelnienia":
                    target = menu.input_percent_fill.get_int(15, 1, 99)
                    if not active_sim_for_removal.is_complete():
                        steps_done = active_sim_for_removal.step_until_fill(target)
                        step_count += steps_done

                    import numpy as np
                    import random as _random
                    target_filled = int((target / 100.0) *
                                       active_sim_for_removal.width *
                                       active_sim_for_removal.height *
                                       active_sim_for_removal.depth)
                    index = list(active_sim_for_removal.get_unique_id_of_grain())
                    _random.shuffle(index)
                    current_fill = int(
                        active_sim_for_removal.get_percent_fill() *
                        active_sim_for_removal.width *
                        active_sim_for_removal.height *
                        active_sim_for_removal.depth / 100
                    )
                    removed_count = 0
                    for grain_id in index:
                        import numpy as _np
                        grain_cells = int(_np.count_nonzero(active_sim_for_removal.grid == grain_id))
                        active_sim_for_removal.remove_grain_by_id(grain_id)
                        current_fill -= grain_cells
                        removed_count += 1
                        if current_fill <= target_filled:
                            break
                    statistics.record_removal(removed_count)
                    percent_f = active_sim_for_removal.get_percent_fill()
                    menu.text_status = f"Usunieto ziarna. Wypelnienie: {percent_f:.1f}%"

                elif mode == "N losowych ziaren":
                    number = menu.input_remove_n.get_int(5, 1, 99999)
                    removed = active_sim_for_removal.remove_n_random_of_grain(number)
                    statistics.record_removal(len(removed))
                    percent_f = active_sim_for_removal.get_percent_fill()
                    menu.text_status = f"Usunieto {len(removed)} ziaren. Wypelnienie: {percent_f:.1f}%"

                elif mode == "Klikniecie myszka":
                    menu.remove_click_mode = not menu.remove_click_mode
                    menu.text_status = (
                        "Kliknij ziarno, aby usunac." if menu.remove_click_mode
                        else "Tryb usuwania wylaczony."
                    )

            # --- Scalanie porow
            if menu.button_consolidate.is_clicked(event) and active_sim_for_removal:
                if active_sim_for_removal.has_consolidated_pore():
                    active_sim_for_removal.deconsolidate_pore()
                    menu.text_status = "Pory rozscalone (0)"
                else:
                    active_sim_for_removal.consolidate_pore()
                    pore_c = active_sim_for_removal.get_count_pore()
                    total = (active_sim_for_removal.width *
                             active_sim_for_removal.height *
                             active_sim_for_removal.depth)
                    percent_f = (pore_c / total) * 100
                    menu.text_status = f"Pory scalone. Porowatosc: {percent_f:.1f}%"

            # --- Reczne dodawanie ziaren
            if (event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and manual_mode
                    and simulation is not None):
                gx, gy = canvas_to_grid(event.pos, canvas_rect, cell_size,
                                        simulation.width, simulation.height)
                if gx is not None:
                    simulation.add_manual_seed(gx, gy, menu.current_layer)

            # --- Usuniecie przez klikniecie
            if (event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and menu.remove_click_mode
                    and active_sim_for_removal is not None):
                gx, gy = canvas_to_grid(event.pos, canvas_rect, cell_size,
                                        active_sim_for_removal.width,
                                        active_sim_for_removal.height)
                if gx is not None:
                    gid = active_sim_for_removal.get_grain_at(gx, gy, menu.current_layer)
                    if gid > 0:
                        active_sim_for_removal.remove_grain_by_id(gid)
                        statistics.record_removal(1)
                        percent_f = active_sim_for_removal.get_percent_fill()
                        menu.text_status = f"Usunieto ID={gid}. Wypelnienie: {percent_f:.1f}%"
                    else:
                        menu.text_status = "Kliknales puste miejsce!"

        active_sim = mc_simulation if mc_simulation else simulation

        if running and active_sim:
            if menu.is_mc_mode() and mc_simulation is not None:
                # --- Monte Carlo: ograniczenie do maks. iteracji Monte Carlo
                mc_params = menu.get_mc_parameters()
                max_steps = mc_params["mc_steps"]

                for _ in range(display_every):
                    if step_count < max_steps:
                        mc_simulation.step()
                        step_count += 1

                if step_count >= max_steps:
                    running = False
                    statistics.stop_monte_carlo_timer(step_count)
                    menu.text_status = (f"Monte Carlo zakonczone. Iteracji: {step_count} | "
                                        f"Ziaren: {mc_simulation.get_grain_count()}")
                else:
                    menu.text_status = (f"MC krok: {step_count}/{max_steps} | "
                                        f"Ziaren: {mc_simulation.get_grain_count()}")

            else:
                # --- Cellular Automata
                if not simulation.is_complete():
                    for _ in range(display_every):
                        if not simulation.is_complete():
                            simulation.step()
                            step_count += 1

                    if simulation.is_complete():
                        running = False
                        statistics.stop_cellular_automata_timer(step_count)
                        menu.text_status = f"Cellular Automata gotowe :) Krokow: {step_count}"
                    else:
                        menu.text_status = f"Cellular Automata krok: {step_count}"

        screen.fill((50, 50, 50))

        active_sim = mc_simulation if mc_simulation else simulation

        if active_sim is not None:
            if show_statistics and statistics_surface is not None:
                # --- Panel statystyk zamiast siatki
                screen.blit(statistics_surface, (0, 0))
            else:
                pygame.draw.rect(screen, WHITE, canvas_rect)
                actual_z_layer = active_sim.get_layer(menu.current_layer)
                draw_grid(screen, actual_z_layer, canvas_rect, cell_size)

            if not show_statistics and manual_mode:
                mx, my = pygame.mouse.get_pos()
                gx, gy = canvas_to_grid((mx, my), canvas_rect, cell_size,
                                        simulation.width, simulation.height)
                if gx is not None:
                    highlight = pygame.Rect(
                        canvas_rect.x + gx * cell_size,
                        canvas_rect.y + gy * cell_size,
                        cell_size, cell_size
                    )
                    pygame.draw.rect(screen, RED, highlight, 2)

            # --- Etykieta trybu w lewym gornym rogu
            mode_font = pygame.font.SysFont(None, 18, bold=True)
            mode_label = "Monte Carlo (MC)" if mc_simulation else "Cellular Automata (CA)"
            mode_color = (30, 80, 180) if mc_simulation else (30, 120, 50)
            mode_surf = mode_font.render(mode_label, True, mode_color)
            screen.blit(mode_surf, (8, 6))

        else:
            pygame.draw.rect(screen, LIGHT_GREY, canvas_rect)
            hint_font = pygame.font.SysFont(None, 22)
            hint = hint_font.render(
                "Ustaw parametry i kliknij 'Generuj przestrzen'",
                True, DARK_GREY
            )
            screen.blit(hint, hint.get_rect(center=canvas_rect.center))

        pygame.draw.rect(screen, GREY, canvas_rect, 1)
        menu.draw(screen, active_sim)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()