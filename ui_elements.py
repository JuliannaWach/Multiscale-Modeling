import pygame
from constants import BLACK, WHITE, GREY, DARK_GREY, RED

HOVER_GREEN = (200, 240, 200)
ACTIVE_GREEN = (144, 238, 144)
BORDER = (0, 0, 0)

class Button:
    def __init__(self, x, y, width, height, text, background_color=WHITE, foreground_color=BLACK, font_size=17, active=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.background_color = background_color
        self.foreground_color = foreground_color
        self.active = active
        self.font = pygame.font.SysFont(None, font_size, bold=True)
        self.font_display = pygame.font.SysFont(None, font_size)
        self.enabled = True

    def draw(self, surface):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_x, mouse_y)

        if not self.enabled:
            background_color = (210, 210, 210)
            foreground_color = GREY
            border = GREY
            font = self.font_display

        elif self.active:
            background_color = ACTIVE_GREEN
            foreground_color = BLACK
            border = BORDER
            font = self.font

        elif hovered:
            background_color = HOVER_GREEN
            foreground_color = BLACK
            border = BORDER
            font = self.font

        else:
            background_color = self.background_color
            foreground_color = self.foreground_color
            border = BORDER
            font = self.font

        pygame.draw.rect(surface, background_color, self.rect, border_radius=2)
        pygame.draw.rect(surface, border, self.rect, 2, border_radius=2)

        text = font.render(self.text, True, foreground_color)
        surface.blit(text, text.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return(self.enabled # --- Zwraca True, jesli klikniemy LEWYM przyciskiem myszki
               and event.type == pygame.MOUSEBUTTONDOWN
               and event.button == 1
               and self.rect.collidepoint(event.pos))

class InputBox:
    def __init__(self, x, y, width, height, value="", label="", font_size=16):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = str(value)
        self.label = label
        self.active = False # --- Aktywnosc pola (focus)
        self.error = False # --- Nieprawidlowosc wartosci
        self.font = pygame.font.SysFont(None, font_size)
        self.label_font = pygame.font.SysFont(None, 13)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit():
                self.text += event.unicode # --- Akceptacja TYLKO cyfr

    def get_int(self, default=1, min_value=1, max_value=9999):
        try:
            value = int(self.text)
            if min_value <= value <= max_value:
                self.error = False
                return value
            self.error = True
            return default
        except ValueError:
            self.error = True
            return default

    def draw(self, surface):
        if self.label:
            my_label = self.label_font.render(self.label, True, (80, 80, 80))
            surface.blit(my_label, (self.rect.x, self.rect.y - 13)) # --- Etykieta nad polem 14 px powyzej

        # --- Tlo z ramka (jesli czerwona = ERROR, active_green = aktywne, border = normalne)
        border = RED if self.error else (ACTIVE_GREEN if self.active else BORDER)
        border_w = 2 if self.active else 1
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, border, self.rect, border_w)

        font = pygame.font.SysFont(None, 16)
        text_txt = self.font.render(self.text, True, BLACK)
        text_y = self.rect.y + (self.rect.height - text_txt.get_height()) // 2
        surface.blit(text_txt, (self.rect.x + 5, text_y))

class CycleSelector:
    def __init__(self, x, y, width, height, options, label="", font_size=16):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options
        self.index = 0
        self.label = label
        self.font = pygame.font.SysFont(None, font_size, bold=True)
        self.label_font = pygame.font.SysFont(None, 13)

    @property
    def value(self):
        return self.options[self.index]

    def handle_event(self, event):
        if (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos)):
            self.index = (self.index + 1) % len(self.options)

    def draw(self, surface):
        if self.label:
            my_label = self.label_font.render(self.label, True, (80, 80, 80))
            surface.blit(my_label, (self.rect.x, self.rect.y - 13))

        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        background_color = HOVER_GREEN if hovered else WHITE

        pygame.draw.rect(surface, background_color, self.rect, border_radius=2)
        pygame.draw.rect(surface, BORDER, self.rect, 2, border_radius=2)

        my_text = self.font.render(f"< {self.value} >", True, BLACK)
        surface.blit(my_text, my_text.get_rect(center=self.rect.center))