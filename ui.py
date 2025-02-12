 # will change after we have photo gui by kit !!!
 # this is just a demo !!! 
 #  we will have photo board background when we submit the project 

import pygame
import sys
import time

WINDOW_SIZE = (1280, 720) 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
MODERN_BG = (18, 18, 18)
ACCENT_COLOR = (75, 139, 190)
BUTTON_HOVER = (95, 159, 210)
ERROR_COLOR = (220, 53, 69)
SUCCESS_COLOR = (40, 167, 69)

PLAYER_EMOJIS = ["😎", "🤠", "🤓", "😊", "🥳"] # will change soon

class ModernButton:
    def __init__(self, rect, text, font, color=ACCENT_COLOR, hover_color=BUTTON_HOVER):
        self.rect = rect
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.active = True
        self.is_selected = False

    def draw(self, screen):
        if not self.active:
            base_color = GRAY
        else:
            base_color = self.hover_color if self.is_hovered or self.is_selected else self.color
        shadow_rect = self.rect.copy()
        shadow_rect.y += 2
        pygame.draw.rect(screen, (*BLACK, 128), shadow_rect, border_radius=10)
        pygame.draw.rect(screen, base_color, self.rect, border_radius=10)
        gradient = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for i in range(self.rect.height):
            alpha = int(100 * (1 - i/self.rect.height))
            pygame.draw.line(gradient, (255, 255, 255, alpha), 
                           (0, i), (self.rect.width, i))
        screen.blit(gradient, self.rect)
        text_shadow = self.font.render(self.text, True, BLACK)
        text_rect_shadow = text_shadow.get_rect(center=self.rect.center)
        text_rect_shadow.x += 1
        text_rect_shadow.y += 1
        screen.blit(text_shadow, text_rect_shadow)
        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        if self.is_selected:
            pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=10)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

class ModernInput:
    def __init__(self, rect, text, font, active_color=ACCENT_COLOR, inactive_color=GRAY):
        self.rect = rect
        self.text = text
        self.font = font
        self.active_color = active_color
        self.inactive_color = inactive_color
        self.active = False
        self.placeholder = "Enter name..."
        self.is_selected = False
        self.error = False
        self.background_alpha = 200

    def draw(self, screen):
        s = pygame.Surface(self.rect.size)
        s.set_alpha(self.background_alpha)
        if self.error:
            s.fill(ERROR_COLOR)
        else:
            color = self.active_color if self.active or self.is_selected else self.inactive_color
            s.fill(color)
        screen.blit(s, self.rect)
        if self.text:
            color = WHITE
            text = self.text
        else:
            color = LIGHT_GRAY
            text = self.placeholder
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        border_color = WHITE if self.active or self.is_selected else LIGHT_GRAY
        pygame.draw.rect(screen, border_color, self.rect, 2, border_radius=5)
        if self.is_selected:
            pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=5)

class StartPage:
    def __init__(self):
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Property Tycoon")
        self.title_font = pygame.font.Font(None, 82)
        self.button_font = pygame.font.Font(None, 42)
        self.version_font = pygame.font.Font(None, 28)
        self.input_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.selected_element = 0
        self.active_input = -1
        button_width = 300
        button_height = 60
        self.start_button = ModernButton(
            pygame.Rect(
                (WINDOW_SIZE[0] - button_width) // 2,
                WINDOW_SIZE[1] - 120,  
                button_width,
                button_height
            ),
            "Start Game",
            self.button_font
        )
        self.player_count = 2
        self.player_names = ["Player 1 😎", "Player 2 🤠", "Player 3 🤓", "Player 4 😊", "Player 5 🥳"] # just for demo
        self.name_inputs = []
        input_y_start = WINDOW_SIZE[1] // 2 - 100
        input_width = 300
        input_height = 50
        for i in range(5):
            self.name_inputs.append(ModernInput(
                pygame.Rect(
                    (WINDOW_SIZE[0] - input_width) // 2,
                    input_y_start + i * 70,
                    input_width,
                    input_height
                ),
                self.player_names[i],
                self.input_font
            ))
        count_x_offset = 250
        self.minus_button = ModernButton(
            pygame.Rect(
                WINDOW_SIZE[0]//2 - count_x_offset,
                input_y_start - 80,
                50,
                50
            ),
            "-",
            self.button_font
        )
        self.plus_button = ModernButton(
            pygame.Rect(
                WINDOW_SIZE[0]//2 + count_x_offset - 50,
                input_y_start - 80,
                50,
                50
            ),
            "+",
            self.button_font
        )
        self.error_message = None
        self.error_time = 0
        self.ERROR_DISPLAY_TIME = 3000

    def draw(self):
        self.screen.fill(MODERN_BG)
        gradient = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        for i in range(WINDOW_SIZE[1]):
            alpha = int(255 * (1 - i/WINDOW_SIZE[1]))
            pygame.draw.line(gradient, (*ACCENT_COLOR[:3], alpha), (0, i), (WINDOW_SIZE[0], i))
        self.screen.blit(gradient, (0, 0))
        title_shadow = self.title_font.render("Property Tycoon", True, BLACK)
        title_glow = self.title_font.render("Property Tycoon", True, ACCENT_COLOR)
        title_text = self.title_font.render("Property Tycoon", True, WHITE)
        title_rect = title_text.get_rect(centerx=WINDOW_SIZE[0]//2, y=80)
        shadow_rect = title_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        self.screen.blit(title_shadow, shadow_rect)
        self.screen.blit(title_glow, title_rect)
        self.screen.blit(title_text, title_rect)
        count_text = self.button_font.render(f"Number of Players: {self.player_count}", True, WHITE)
        count_rect = count_text.get_rect(centerx=WINDOW_SIZE[0]//2, y=WINDOW_SIZE[1]//2 - 180)
        self.screen.blit(count_text, count_rect)
        self.minus_button.active = self.player_count > 2
        self.plus_button.active = self.player_count < 5
        self.minus_button.is_selected = (self.selected_element == 0)
        self.plus_button.is_selected = (self.selected_element == 1)
        self.minus_button.draw(self.screen)
        self.plus_button.draw(self.screen)
        for i in range(self.player_count):
            self.name_inputs[i].active = (i == self.active_input)
            self.name_inputs[i].is_selected = (self.selected_element == i + 2)
            self.name_inputs[i].error = not self.player_names[i].strip()
            self.name_inputs[i].text = self.player_names[i]
            self.name_inputs[i].draw(self.screen)
        can_start = all(name.strip() for name in self.player_names[:self.player_count])
        self.start_button.active = can_start
        self.start_button.is_selected = (self.selected_element == 7)
        self.start_button.draw(self.screen)
        current_time = pygame.time.get_ticks()
        if self.error_message and current_time - self.error_time < self.ERROR_DISPLAY_TIME:
            alpha = max(0, 255 - ((current_time - self.error_time) / self.ERROR_DISPLAY_TIME * 255))
            error_surface = self.font.render(self.error_message, True, ERROR_COLOR)
            error_surface.set_alpha(int(alpha))
            error_rect = error_surface.get_rect(centerx=WINDOW_SIZE[0]//2, bottom=WINDOW_SIZE[1]-20)
            self.screen.blit(error_surface, error_rect)
        version_text = self.version_font.render("Build Version: 09.02.2025", True, GRAY)
        version_rect = version_text.get_rect(right=WINDOW_SIZE[0]-20, bottom=WINDOW_SIZE[1]-20)
        self.screen.blit(version_text, version_rect)
        if self.active_input == -1:
            hint_text = self.small_font.render("Use ↑/↓ to navigate, Enter to select", True, LIGHT_GRAY)
            hint_rect = hint_text.get_rect(centerx=WINDOW_SIZE[0]//2, bottom=WINDOW_SIZE[1]-40)
            self.screen.blit(hint_text, hint_rect)
        pygame.display.flip()
    
    def handle_click(self, pos):
        if self.minus_button.check_hover(pos):
            self.player_count = max(2, self.player_count - 1)
            return False
        if self.plus_button.check_hover(pos):
            self.player_count = min(5, self.player_count + 1)
            return False
        for i in range(self.player_count):
            if self.name_inputs[i].rect.collidepoint(pos):
                self.active_input = i
                return False
        if self.start_button.check_hover(pos):
            return True
        self.active_input = -1
        return False
        
    def handle_key(self, event):
        if self.active_input >= 0:
            if event.key == pygame.K_RETURN:
                self.active_input = -1
            elif event.key == pygame.K_BACKSPACE:
                name = self.player_names[self.active_input]
                emoji = name[-2:] if len(name) >= 2 else ""
                self.player_names[self.active_input] = name[:-3] + emoji if len(name) > 3 else emoji
            elif event.key == pygame.K_TAB:
                self.active_input = (self.active_input + 1) % self.player_count
                self.selected_element = self.active_input + 2
            else:
                if len(self.player_names[self.active_input]) < 15:
                    name = self.player_names[self.active_input]
                    emoji = name[-2:] if len(name) >= 2 else ""
                    self.player_names[self.active_input] = name[:-2] + event.unicode + emoji
        else:
            if event.key in (pygame.K_UP, pygame.K_LEFT):
                self.selected_element = (self.selected_element - 1) % 8
                while self.selected_element >= 2 and self.selected_element < 7 and self.selected_element - 2 >= self.player_count:
                    self.selected_element = (self.selected_element - 1) % 8
            elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):
                self.selected_element = (self.selected_element + 1) % 8
                while self.selected_element >= 2 and self.selected_element < 7 and self.selected_element - 2 >= self.player_count:
                    self.selected_element = (self.selected_element + 1) % 8
            elif event.key == pygame.K_RETURN:
                if self.selected_element == 0 and self.player_count > 2:
                    self.player_count -= 1
                elif self.selected_element == 1 and self.player_count < 5:
                    self.player_count += 1
                elif 2 <= self.selected_element <= 6:
                    self.active_input = self.selected_element - 2
                elif self.selected_element == 7:
                    can_start = all(name.strip() for name in self.player_names[:self.player_count])
                    if can_start:
                        return True
            elif event.key == pygame.K_ESCAPE:
                self.active_input = -1
        return False

    def handle_motion(self, pos):
        self.minus_button.check_hover(pos)
        self.plus_button.check_hover(pos)
        self.start_button.check_hover(pos)

    def get_player_info(self):
        return self.player_count, [name.strip() for name in self.player_names[:self.player_count]]
