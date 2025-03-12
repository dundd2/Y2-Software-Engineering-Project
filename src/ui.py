import pygame
import sys
import time
import math
import random
from src.text_scaler import text_scaler
import os
import webbrowser 

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
MODERN_BG = (18, 18, 18)
ACCENT_COLOR = (75, 139, 190)
BUTTON_HOVER = (95, 159, 210)
ERROR_COLOR = (220, 53, 69)
SUCCESS_COLOR = (40, 167, 69)
MODE_COLOR = (100, 200, 255)
TIME_COLOR = (255, 180, 100)
HUMAN_COLOR = (100, 200, 100)
AI_COLOR = (200, 100, 100)

DEFAULT_RES = (854, 480)

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(base_path, "assets", "font", "Play-Regular.ttf")

def get_window_size():
    surface = pygame.display.get_surface()
    if (surface):
        return surface.get_size()
    return DEFAULT_RES

class ModernButton:
    def __init__(self, rect, text, font, color=ACCENT_COLOR):
        self.rect = rect
        self.text = text
        self.font = font
        self.color = color
        self.hover = False
        self.active = True
        self.is_selected = False
        
        self.image = None
        try:
            button_map = {
                "Start Game": "Play_Button.png",
                "Back to Menu": "Back_Button.png",
                "Edit": "Edit_Button.png",
                "Exit Game": "Exit_Button.png",
                "+": "PlusHuman_Button.png" if color == HUMAN_COLOR else "PlusComputer_Button.png",
                "Play Again": "Play_ButtonSmall.png"
            }
            
            if text in button_map:
                image_path = os.path.join(base_path, f"assets/image/{button_map[text]}")
                self.image = pygame.image.load(image_path)
                self.image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
        except (pygame.error, FileNotFoundError):
            print(f"Could not load button image for {text}")
            
    def draw(self, screen):
        if not self.active:
            base_color = GRAY
            self._draw_basic_button(screen, base_color)
            return

        if self.image:
            if self.hover or self.is_selected:
                hover_img = self.image.copy()
                hover_img.fill((255, 255, 255, 50), special_flags=pygame.BLEND_RGBA_ADD)
                screen.blit(hover_img, self.rect)
            else:
                screen.blit(self.image, self.rect)
        else:
            base_color = BUTTON_HOVER if self.hover else self.color
            self._draw_basic_button(screen, base_color)
            
    def _draw_basic_button(self, screen, base_color):
        shadow_rect = self.rect.copy()
        shadow_rect.y += 2
        shadow = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=5)
        screen.blit(shadow, shadow_rect)

        pygame.draw.rect(screen, base_color, self.rect, border_radius=5)
        gradient = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for i in range(self.rect.height):
            alpha = int(100 * (1 - i/self.rect.height))
            pygame.draw.line(gradient, (255, 255, 255, alpha), 
                           (0, i), (self.rect.width, i))
        screen.blit(gradient, self.rect)

        if self.is_selected:
            pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=5)

        text_surface = self.font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

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
            s.fill(ERROR_COLOR[:3])
        else:
            color = self.active_color if self.active or self.is_selected else self.inactive_color
            s.fill(color[:3])
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

class BasePage:
    def __init__(self, instructions=None):
        window_size = get_window_size()
        self.screen = pygame.display.set_mode(window_size)
        try:
            asset_path = os.path.join(base_path, "assets/image/Logo.png")
            self.logo_image = pygame.image.load(asset_path)
            logo_width = int(window_size[0] * 0.3)
            logo_height = int(logo_width * (self.logo_image.get_height() / self.logo_image.get_width()))
            self.logo_image = pygame.transform.scale(self.logo_image, (logo_width, logo_height))
        except (pygame.error, FileNotFoundError):
            print("Could not load game logo")
            self.logo_image = None
            
        try:
            asset_path = os.path.join(base_path, "assets/image/starterbackground.png")
            self.background_image = pygame.image.load(asset_path)
            # Don't resize here, we'll handle proper scaling in draw_background
        except (pygame.error, FileNotFoundError):
            print("Could not load background image")
            self.background_image = None
            
        self.title_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(82))
        self.button_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(42))
        self.version_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(28))
        self.small_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(24))
        self.instructions = instructions

    def draw_background(self):
        window_size = get_window_size()
        if self.background_image:
            img_width, img_height = self.background_image.get_size()
            window_width, window_height = window_size
            
            img_aspect = img_width / img_height
            window_aspect = window_width / window_height
            
            if window_aspect > img_aspect:  
                scaled_width = window_width
                scaled_height = int(scaled_width / img_aspect)
            else:  
                scaled_height = window_height
                scaled_width = int(scaled_height * img_aspect)
            
            pos_x = (window_width - scaled_width) // 2
            pos_y = (window_height - scaled_height) // 2
            
            scaled_bg = pygame.transform.scale(self.background_image, (scaled_width, scaled_height))
            self.screen.blit(scaled_bg, (pos_x, pos_y))
            
            overlay = pygame.Surface(window_size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
        else:
            self.screen.fill(MODERN_BG)
            gradient = pygame.Surface(window_size, pygame.SRCALPHA)
            for i in range(window_size[1]):
                alpha = int(255 * (1 - i/window_size[1]))
                pygame.draw.line(gradient, (*ACCENT_COLOR[:3], alpha), (0, i), (window_size[0], i))
            self.screen.blit(gradient, (0, 0))

    def draw_title(self):
        window_size = get_window_size()
        if self.logo_image:
            logo_rect = self.logo_image.get_rect(centerx=window_size[0]//2, y=50)
            
            glow_surface = pygame.Surface((logo_rect.width + 20, logo_rect.height + 20), pygame.SRCALPHA)
            current_time = pygame.time.get_ticks()
            glow_intensity = abs(math.sin(current_time * 0.003))
            for i in range(10):
                alpha = int(25 * (1 - i/10) * glow_intensity)
                pygame.draw.rect(glow_surface, (*ACCENT_COLOR, alpha),
                               pygame.Rect(i, i, glow_surface.get_width() - i*2, glow_surface.get_height() - i*2),
                               border_radius=5)
            self.screen.blit(glow_surface, (logo_rect.x - 10, logo_rect.y - 10))
            self.screen.blit(self.logo_image, logo_rect)
        else:
            title_shadow = self.title_font.render("Property Tycoon", True, BLACK)
            title_glow = self.title_font.render("Property Tycoon", True, ACCENT_COLOR)
            title_text = self.title_font.render("Property Tycoon", True, WHITE)
            title_rect = title_text.get_rect(centerx=window_size[0]//2, y=80)
            shadow_rect = title_rect.copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            self.screen.blit(title_shadow, shadow_rect)
            self.screen.blit(title_glow, title_rect)
            self.screen.blit(title_text, title_rect)

    def draw_instructions(self):
        if self.instructions:
            window_size = get_window_size()
            font_size = text_scaler.get_scaled_size(20)
            font = pygame.font.Font(FONT_PATH, font_size)
            padding = 10
            line_height = font_size + 2
            
            total_height = len(self.instructions) * line_height
            
            for i, instruction in enumerate(self.instructions):
                text_surface = font.render(instruction, True, WHITE)
                y_position = window_size[1] - (total_height - (i * line_height)) - padding
                self.screen.blit(text_surface, (padding, y_position))

    def draw(self):
        self.draw_background()
        self.draw_title()
        self.draw_instructions()
        pygame.display.flip()

class MainMenuPage(BasePage):
    def __init__(self, instructions=None):
        super().__init__(instructions=instructions)
        self.small_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(24))
        button_width = 300
        button_height = 60
        
        self.start_button = ModernButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] // 2,
                button_width,
                button_height
            ),
            "Start Game",
            self.button_font
        )
        
        self.how_to_play_button = ModernButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] // 2 + 80,
                button_width,
                button_height
            ),
            "How to Play",
            self.button_font,
            color=MODE_COLOR
        )
        
        self.settings_button = ModernButton(
            pygame.Rect(
                20,
                get_window_size()[1] - button_height - 20,
                button_width,
                button_height
            ),
            "Settings",
            self.button_font
        )
        
        try:
            youtube_path = os.path.join(base_path, "assets/image/Youtube Logo.png")
            self.youtube_logo = pygame.image.load(youtube_path)
            self.youtube_logo = pygame.transform.scale(self.youtube_logo, (40, 40))
            self.youtube_rect = self.youtube_logo.get_rect(topleft=(20, 20))
            
            github_path = os.path.join(base_path, "assets/image/GitHub-Symbol.png")
            self.github_logo = pygame.image.load(github_path)
            self.github_logo = pygame.transform.scale(self.github_logo, (40, 40))
            self.github_rect = self.github_logo.get_rect(topleft=(80, 20))
            
            self.github_hover = False
            self.youtube_hover = False
            
            self.github_url = "https://github.com/Minosaji/Software-Engineering-Project"
            self.youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=ygUJcmljayByb2xs"
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load social media logos: {e}")
            self.github_logo = None
            self.youtube_logo = None

    def draw(self):
        self.draw_background()
        self.draw_title()
        
        self.start_button.draw(self.screen)
        self.how_to_play_button.draw(self.screen)
        self.settings_button.draw(self.screen)
        
        if hasattr(self, 'youtube_logo') and self.youtube_logo:
            if self.youtube_hover:
                glow_surface = pygame.Surface((self.youtube_rect.width + 10, self.youtube_rect.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*ACCENT_COLOR, 150), 
                               pygame.Rect(0, 0, glow_surface.get_width(), glow_surface.get_height()),
                               border_radius=5)
                self.screen.blit(glow_surface, (self.youtube_rect.x - 5, self.youtube_rect.y - 5))
            self.screen.blit(self.youtube_logo, self.youtube_rect)
        
        if hasattr(self, 'github_logo') and self.github_logo:
            if self.github_hover:
                glow_surface = pygame.Surface((self.github_rect.width + 10, self.github_rect.height + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (*ACCENT_COLOR, 150), 
                               pygame.Rect(0, 0, glow_surface.get_width(), glow_surface.get_height()),
                               border_radius=5)
                self.screen.blit(glow_surface, (self.github_rect.x - 5, self.github_rect.y - 5))
            self.screen.blit(self.github_logo, self.github_rect)
        
        version_text = self.version_font.render("Build Version: 12.03.2025", True, ERROR_COLOR)
        version_rect = version_text.get_rect(right=get_window_size()[0] - 20, bottom=get_window_size()[1]-20)
        self.screen.blit(version_text, version_rect)
        
        controls_text1 = self.small_font.render("Press ENTER to start", True, LIGHT_GRAY)
        controls_text2 = self.small_font.render("H for how to play, S for settings", True, LIGHT_GRAY)

        controls_rect1 = controls_text1.get_rect(right=get_window_size()[0] - 20, bottom=get_window_size()[1]-70)
        controls_rect2 = controls_text2.get_rect(right=get_window_size()[0] - 20, bottom=get_window_size()[1]-45)
        
        self.screen.blit(controls_text1, controls_rect1)
        self.screen.blit(controls_text2, controls_rect2)

        pygame.display.flip()

    def handle_click(self, pos):
        if self.start_button.check_hover(pos):
            return "start"
        elif self.how_to_play_button.check_hover(pos):
            return "how_to_play"
        elif self.settings_button.check_hover(pos):
            return "settings"
        elif hasattr(self, 'github_rect') and self.github_rect.collidepoint(pos):
            try:
                webbrowser.open(self.github_url)
                print(f"Opening GitHub URL: {self.github_url}")
            except Exception as e:
                print(f"Error opening GitHub URL: {e}")
        elif hasattr(self, 'youtube_rect') and self.youtube_rect.collidepoint(pos):
            try:
                webbrowser.open(self.youtube_url)
                print(f"Opening YouTube URL: {self.youtube_url}")
            except Exception as e:
                print(f"Error opening YouTube URL: {e}")
        return None

    def handle_motion(self, pos):
        self.start_button.check_hover(pos)
        self.how_to_play_button.check_hover(pos)
        self.settings_button.check_hover(pos)
        
        if hasattr(self, 'github_rect'):
            self.github_hover = self.github_rect.collidepoint(pos)
        if hasattr(self, 'youtube_rect'):
            self.youtube_hover = self.youtube_rect.collidepoint(pos)
            
    def handle_key(self, event):
        if event.key == pygame.K_RETURN:
            return "start"
        elif event.key == pygame.K_h:
            return "how_to_play"
        elif event.key == pygame.K_s:
            return "settings"
        return None

class SettingsPage(BasePage):
    CONFIRMATION_DURATION = 5000

    def __init__(self, instructions=None):
        super().__init__(instructions=instructions)
        self.small_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(24))
        self.resolution_options = [
            (1280, 720),
            (854, 480),
            (1600, 900),
            (1920, 1080),
            (2560, 1440)
        ]
        self.current_resolution = 0
        self.show_confirmation = False
        self.confirmation_time = 0
        
        button_width = 400
        button_height = 60
        self.resolution_button = ModernButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] // 2 - 100,
                button_width,
                button_height
            ),
            f"Screen Size: {self.resolution_options[self.current_resolution][0]}x{self.resolution_options[self.current_resolution][1]}",
            self.button_font
        )
        confirm_button_width = 300
        self.confirm_button = ModernButton(
            pygame.Rect(
                (get_window_size()[0] - confirm_button_width) // 2,
                get_window_size()[1] // 2 + 50,
                confirm_button_width,
                button_height
            ),
            "Confirm",
            self.button_font
        )
        back_button_width = 300
        self.back_button = ModernButton(
            pygame.Rect(
                (get_window_size()[0] - back_button_width) // 2,
                get_window_size()[1] - 120,
                back_button_width,
                button_height
            ),
            "Back to Menu",
            self.button_font
        )

    def draw(self):
        self.draw_background()
        self.draw_title()
        
        settings_text = self.button_font.render("Game Settings", True, WHITE)
        settings_rect = settings_text.get_rect(centerx=get_window_size()[0]//2, y=180)
        self.screen.blit(settings_text, settings_rect)
        
        self.resolution_button.text = f"Screen Size: {self.resolution_options[self.current_resolution][0]}x{self.resolution_options[self.current_resolution][1]}"
        self.resolution_button.draw(self.screen)
        
        info_text = self.small_font.render("All resolutions maintain 16:9 aspect ratio", True, LIGHT_GRAY)
        info_rect = info_text.get_rect(centerx=get_window_size()[0]//2, top=self.resolution_button.rect.bottom + 10)
        self.screen.blit(info_text, info_rect)
        
        if self.show_confirmation:
            current_time = pygame.time.get_ticks()
            if current_time - self.confirmation_time < self.CONFIRMATION_DURATION:
                confirm_text = self.small_font.render("Press ENTER or click Confirm to apply changes", True, SUCCESS_COLOR)
                confirm_rect = confirm_text.get_rect(left=20, top=info_rect.bottom + 10)
                self.screen.blit(confirm_text, confirm_rect)
            else:
                self.show_confirmation = False
        
        controls = [
            "Controls:",
            "R - Change screen resolution",
            "Enter/Space - Apply and return"
        ]
        
        y_offset = get_window_size()[1] - 180
        for hint in controls:
            hint_text = self.small_font.render(hint, True, LIGHT_GRAY)
            hint_rect = hint_text.get_rect(right=get_window_size()[0] - 20, y=y_offset)
            self.screen.blit(hint_text, hint_rect)
            y_offset += 25
        
        self.confirm_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        pygame.display.flip()

    def handle_click(self, pos):
        if self.resolution_button.check_hover(pos):
            self.current_resolution = (self.current_resolution + 1) % len(self.resolution_options)
            self.show_confirmation = True
            self.confirmation_time = pygame.time.get_ticks()
            return False
        elif self.confirm_button.check_hover(pos):
            current_resolution = get_window_size()
            new_resolution = self.resolution_options[self.current_resolution]
            if current_resolution != new_resolution:
                return True
        elif self.back_button.check_hover(pos):
            return True
        return False

    def handle_motion(self, pos):
        self.resolution_button.check_hover(pos)
        self.confirm_button.check_hover(pos)
        self.back_button.check_hover(pos)

    def handle_key(self, event):
        if event.key == pygame.K_r:
            self.current_resolution = (self.current_resolution + 1) % len(self.resolution_options)
            self.show_confirmation = True
            self.confirmation_time = pygame.time.get_ticks()
            return False
        elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
            current_resolution = get_window_size()
            new_resolution = self.resolution_options[self.current_resolution]
            if current_resolution != new_resolution:
                return True
        return False
    
    def get_settings(self):
        return {"resolution": self.resolution_options[self.current_resolution]}

class StartPage(BasePage):
    def __init__(self, instructions=None):
        super().__init__(instructions=instructions)
        self.screen = pygame.display.set_mode(get_window_size())
        pygame.display.set_caption("Property Tycoon")
        self.title_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(82))
        self.button_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(42))
        self.version_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(28))
        self.input_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(36))
        self.small_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(24))
        self.selected_element = 0
        self.active_input = -1

        self.human_count = 1
        self.ai_count = 1
        self.total_players = self.human_count + self.ai_count
        self.player_names = ["Human Player 1"]
        self.ai_names = ["AI-1"]
        self.ai_name_counter = 1

        button_width = 300
        button_height = 60
        input_y_start = get_window_size()[1] // 2 + 50
        input_width = 300
        input_height = 50
        count_x_offset = 250

        self.human_minus_button = ModernButton(
            pygame.Rect(
                get_window_size()[0]//2 - count_x_offset - 100,
                input_y_start - 140,
                50,
                50
            ),
            "-",
            self.button_font,
            color=HUMAN_COLOR
        )
        
        self.human_plus_button = ModernButton(
            pygame.Rect(
                get_window_size()[0]//2 - count_x_offset + 50,
                input_y_start - 140,
                50,
                50
            ),
            "+",
            self.button_font,
            color=HUMAN_COLOR
        )

        self.ai_minus_button = ModernButton(
            pygame.Rect(
                get_window_size()[0]//2 + count_x_offset - 100,
                input_y_start - 140,
                50,
                50
            ),
            "-",
            self.button_font,
            color=AI_COLOR
        )
        
        self.ai_plus_button = ModernButton(
            pygame.Rect(
                get_window_size()[0]//2 + count_x_offset + 50,
                input_y_start - 140,
                50,
                50
            ),
            "+",
            self.button_font,
            color=AI_COLOR
        )

        self.name_inputs = []
        for i in range(5):
            self.name_inputs.append(ModernInput(
                pygame.Rect(
                    (get_window_size()[0] - input_width) // 2,
                    input_y_start + i * 60,
                    input_width,
                    input_height
                ),
                "",
                self.input_font
            ))

        self.start_button = ModernButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] - 100,
                button_width,
                button_height
            ),
            "Start Game",
            self.button_font
        )

        self.back_button = ModernButton(
            pygame.Rect(
                20,
                get_window_size()[1] - 100,
                200,
                button_height
            ),
            "Back to Menu",
            self.button_font
        )

    def generate_unique_ai_name(self):
        self.ai_name_counter += 1
        return f"AI-{self.ai_name_counter}"

    def update_player_lists(self):
        while len(self.ai_names) < self.ai_count:
            self.ai_names.append(self.generate_unique_ai_name())
        while len(self.ai_names) > self.ai_count:
            self.ai_names.pop()

    def draw(self):
        self.draw_background()
        self.draw_title()

        input_y_start = get_window_size()[1] // 2 + 50
        
        human_text = self.button_font.render(f"Human Players: {self.human_count}", True, HUMAN_COLOR)
        human_rect = human_text.get_rect(centerx=get_window_size()[0]//2 - 150, y=input_y_start - 200)
        self.screen.blit(human_text, human_rect)

        ai_text = self.button_font.render(f"AI Players: {self.ai_count}", True, AI_COLOR)
        ai_rect = ai_text.get_rect(centerx=get_window_size()[0]//2 + 150, y=input_y_start - 200)
        self.screen.blit(ai_text, ai_rect)

        total_text = self.small_font.render(f"Total Players: {self.total_players}/5", True, LIGHT_GRAY)
        total_rect = total_text.get_rect(centerx=get_window_size()[0]//2, y=input_y_start - 170)
        self.screen.blit(total_text, total_rect)

        self.human_minus_button.active = self.human_count > 1
        self.human_plus_button.active = self.human_count < 5 and self.total_players < 5
        self.ai_minus_button.active = self.ai_count > 0
        self.ai_plus_button.active = self.ai_count < 4 and self.total_players < 5

        self.human_minus_button.draw(self.screen)
        self.human_plus_button.draw(self.screen)
        self.ai_minus_button.draw(self.screen)
        self.ai_plus_button.draw(self.screen)

        for i in range(self.human_count):
            self.name_inputs[i].active = (i == self.active_input)
            self.name_inputs[i].text = self.player_names[i] if i < len(self.player_names) else ""
            self.name_inputs[i].draw(self.screen)
            
            human_label = self.small_font.render("Human", True, HUMAN_COLOR)
            label_rect = human_label.get_rect(
                right=self.name_inputs[i].rect.left - 10,
                centery=self.name_inputs[i].rect.centery
            )
            self.screen.blit(human_label, label_rect)

        for i in range(self.ai_count):
            ai_input_rect = self.name_inputs[self.human_count + i].rect
            ai_text = self.input_font.render(self.ai_names[i], True, LIGHT_GRAY)
            ai_rect = ai_text.get_rect(center=ai_input_rect.center)
            
            pygame.draw.rect(self.screen, (*AI_COLOR[:3], 50), ai_input_rect, border_radius=5)
            self.screen.blit(ai_text, ai_rect)
            
            ai_label = self.small_font.render("AI", True, AI_COLOR)
            label_rect = ai_label.get_rect(
                right=ai_input_rect.left - 10,
                centery=ai_input_rect.centery
            )
            self.screen.blit(ai_label, label_rect)

        can_start = (all(name.strip() for name in self.player_names[:self.human_count]) and 
                    self.total_players >= 2 and self.total_players <= 5)
        self.start_button.active = can_start
        self.start_button.draw(self.screen)

        self.back_button.draw(self.screen)

        controls = [
            "Controls:",
            "H/h - Adjust human players",
            "A/a - Adjust AI players",
            "Enter - Edit name",
            "Space - Start game",
            "ESC/Back - Return to menu"
        ]
        
        y_offset = get_window_size()[1] - 210
        for hint in controls:
            hint_text = self.small_font.render(hint, True, LIGHT_GRAY)
            hint_rect = hint_text.get_rect(right=get_window_size()[0] - 20, y=y_offset)  
            self.screen.blit(hint_text, hint_rect)
            y_offset += 20

        pygame.display.flip()

    def handle_click(self, pos):
        if self.human_minus_button.check_hover(pos) and self.human_count > 1:
            self.human_count -= 1
            self.total_players = self.human_count + self.ai_count
            return False
            
        if self.human_plus_button.check_hover(pos) and self.human_count < 5 and self.total_players < 5:
            self.human_count += 1
            self.total_players = self.human_count + self.ai_count
            if len(self.player_names) < self.human_count:
                self.player_names.append(f"Human {self.human_count}")
            return False

        if self.ai_minus_button.check_hover(pos) and self.ai_count > 0:
            self.ai_count -= 1
            self.total_players = self.human_count + self.ai_count
            self.update_player_lists()
            return False

        if self.ai_plus_button.check_hover(pos) and self.ai_count < 4 and self.total_players < 5:
            self.ai_count += 1
            self.total_players = self.human_count + self.ai_count
            self.update_player_lists()
            return False

        for i in range(self.human_count):
            if self.name_inputs[i].rect.collidepoint(pos):
                self.active_input = i
                return False
                
        if self.start_button.check_hover(pos) and self.start_button.active:
            return True

        if self.back_button.check_hover(pos):
            return "back"

        self.active_input = -1
        return False

    def handle_motion(self, pos):
        self.human_minus_button.check_hover(pos)
        self.human_plus_button.check_hover(pos)
        self.ai_minus_button.check_hover(pos)
        self.ai_plus_button.check_hover(pos)
        self.start_button.check_hover(pos)
        self.back_button.check_hover(pos)

    def handle_key(self, event):
        if self.active_input >= 0:
            if event.key == pygame.K_RETURN:
                self.active_input = -1
            elif event.key == pygame.K_BACKSPACE:
                name = self.player_names[self.active_input]
                self.player_names[self.active_input] = name[:-1] if len(name) > 0 else ""
            elif event.key == pygame.K_TAB:
                self.active_input = (self.active_input + 1) % self.human_count
            elif event.key == pygame.K_ESCAPE:
                self.active_input = -1
            else:
                if len(self.player_names[self.active_input]) < 15:
                    self.player_names[self.active_input] += event.unicode
        else:
            if event.key == pygame.K_h:
                if event.mod & pygame.KMOD_SHIFT and self.human_count < 5 and self.total_players < 5:
                    self.human_count += 1
                    if len(self.player_names) < self.human_count:
                        self.player_names.append(f"Human {self.human_count}")
                elif self.human_count > 1:
                    self.human_count -= 1
                self.total_players = self.human_count + self.ai_count
            
            elif event.key == pygame.K_a:
                if event.mod & pygame.KMOD_SHIFT and self.ai_count < 4 and self.total_players < 5:
                    self.ai_count += 1
                    self.update_player_lists()
                elif self.ai_count > 0:
                    self.ai_count -= 1
                    self.update_player_lists()
                self.total_players = self.human_count + self.ai_count
            
            elif event.key == pygame.K_SPACE:
                if self.start_button.active:
                    return True
            
            elif event.key == pygame.K_RETURN and self.start_button.active:
                return True

            elif event.key == pygame.K_ESCAPE:
                return "back"
        return False

    def get_player_info(self):
        all_names = self.player_names[:self.human_count] + self.ai_names[:self.ai_count]
        return self.total_players, all_names, self.ai_count

class PlayerSelectPage(BasePage):
    def __init__(self):
        super().__init__()
        self.input_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(36))
        self.small_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(24))
        self.selected_element = 0
        self.active_input = -1
        
        self.player_count = 2
        self.player_names = ["" for _ in range(5)]
        
        input_width = 300
        input_height = 50
        input_y_start = get_window_size()[1] // 2 - 100
        
        self.name_inputs = []
        for i in range(5):
            input_rect = pygame.Rect(
                (get_window_size()[0] - input_width) // 2,
                input_y_start + i * 70,
                input_width,
                input_height
            )
            input_field = ModernInput(input_rect, "", self.input_font)
            input_field.placeholder = f"Enter Player {i+1} name..."
            self.name_inputs.append(input_field)

        count_x_offset = 250
        self.minus_button = ModernButton(
            pygame.Rect(
                get_window_size()[0]//2 - count_x_offset,
                input_y_start - 80,
                50,
                50
            ),
            "-",
            self.button_font
        )
        
        self.plus_button = ModernButton(
            pygame.Rect(
                get_window_size()[0]//2 + count_x_offset - 50,
                input_y_start - 80,
                50,
                50
            ),
            "+",
            self.button_font
        )
        
        button_width = 300
        button_height = 60
        self.continue_button = ModernButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] - 120,
                button_width,
                button_height
            ),
            "Continue",
            self.button_font
        )

    def draw(self):
        self.draw_background()
        self.draw_title()
        
        section_title = self.button_font.render("Select Number of Players", True, WHITE)
        title_rect = section_title.get_rect(centerx=get_window_size()[0]//2, y=get_window_size()[1]//2 - 170)  
        self.screen.blit(section_title, title_rect)
        
        count_text = self.button_font.render(str(self.player_count), True, WHITE)
        count_rect = count_text.get_rect(centerx=get_window_size()[0]//2, y=get_window_size()[1]//2 - 130) 
        self.screen.blit(count_text, count_rect)
        
        self.minus_button.active = self.player_count > 2
        self.plus_button.active = self.player_count < 5
        self.minus_button.is_selected = (self.selected_element == 0)
        self.plus_button.is_selected = (self.selected_element == 1)
        self.minus_button.draw(self.screen)
        self.plus_button.draw(self.screen)
        
        name_section_title = self.button_font.render("Enter Player Names", True, WHITE)
        name_title_rect = name_section_title.get_rect(centerx=get_window_size()[0]//2, y=get_window_size()[1]//2 - 90)
        self.screen.blit(name_section_title, name_title_rect)
        
        for i in range(self.player_count):
            self.name_inputs[i].active = (i == self.active_input)
            self.name_inputs[i].is_selected = (self.selected_element == i + 2)
            self.name_inputs[i].error = not self.player_names[i].strip()
            if self.player_names[i]:
                self.name_inputs[i].text = self.player_names[i]
            self.name_inputs[i].draw(self.screen)
            
            if i == self.active_input:
                help_text = self.small_font.render("Type name and press Enter", True, LIGHT_GRAY)
                help_rect = help_text.get_rect(
                    left=self.name_inputs[i].rect.right + 10,
                    centery=self.name_inputs[i].rect.centery
                )
                self.screen.blit(help_text, help_rect)
        
        can_continue = all(name.strip() for name in self.player_names[:self.player_count])
        self.continue_button.active = can_continue
        self.continue_button.is_selected = (self.selected_element == 7)
        self.continue_button.draw(self.screen)
        
        controls = [
            "↑/↓ - Navigate fields",
            "Enter - Edit name",
            "Tab - Next field",
            "Escape - Cancel editing"
        ]
        
        y_offset = get_window_size()[1] - 80
        for hint in controls:
            hint_text = self.small_font.render(hint, True, LIGHT_GRAY)
            hint_rect = hint_text.get_rect(centerx=get_window_size()[0]//2, y=y_offset)
            self.screen.blit(hint_text, hint_rect)
            y_offset += 20
        
        pygame.display.flip()

    def handle_click(self, pos):
        if self.minus_button.check_hover(pos) and self.player_count > 2:
            self.player_count -= 1
            return False
            
        if self.plus_button.check_hover(pos) and self.player_count < 5:
            self.player_count += 1
            return False
            
        for i in range(self.player_count):
            if self.name_inputs[i].rect.collidepoint(pos):
                self.active_input = i
                return False
                
        if self.continue_button.check_hover(pos):
            if all(name.strip() for name in self.player_names[:self.player_count]):
                return True
                
        self.active_input = -1
        return False

    def handle_motion(self, pos):
        self.minus_button.check_hover(pos)
        self.plus_button.check_hover(pos)
        self.continue_button.check_hover(pos)
        
    def handle_key(self, event):
        if self.active_input >= 0:
            if event.key == pygame.K_RETURN:
                if self.name_inputs[self.active_input].text.strip():
                    self.player_names[self.active_input] = self.name_inputs[self.active_input].text.strip()
                self.active_input = -1
            elif event.key == pygame.K_BACKSPACE:
                if self.name_inputs[self.active_input].text:
                    self.name_inputs[self.active_input].text = self.name_inputs[self.active_input].text[:-1]
                    self.player_names[self.active_input] = self.name_inputs[self.active_input].text
            elif event.key == pygame.K_TAB:
                if self.name_inputs[self.active_input].text.strip():
                    self.player_names[self.active_input] = self.name_inputs[self.active_input].text.strip()
                self.active_input = (self.active_input + 1) % self.player_count
                self.selected_element = self.active_input + 2
            elif event.key == pygame.K_ESCAPE:
                self.active_input = -1
            else:
                if len(self.name_inputs[self.active_input].text) < 15:
                    self.name_inputs[self.active_input].text += event.unicode
                    self.player_names[self.active_input] = self.name_inputs[self.active_input].text
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
                    if all(name.strip() for name in self.player_names[:self.player_count]):
                        return True
            elif event.key == pygame.K_ESCAPE:
                self.active_input = -1
        return False

    def get_player_info(self):
        return self.player_count, [name.strip() for name in self.player_names[:self.player_count]]

class HowToPlayPage(BasePage):
    def __init__(self, instructions=None):
        super().__init__(instructions=instructions)
        self.small_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(24))
        
        button_width = 300
        button_height = 60
        self.back_button = ModernButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] - 120,
                button_width,
                button_height
            ),
            "Back to Menu",
            self.button_font
        )
        
        self.instructions = [
            "How to Play Property Tycoon",
            "",
            "To be updated...",
        ]

    def draw(self):
        self.draw_background()
        self.draw_title()
        
        y_offset = 280
        for i, line in enumerate(self.instructions):
            if i == 0:
                text_surface = self.button_font.render(line, True, WHITE)
            elif line == "":
                y_offset += 10
                continue
            elif line.endswith(":"):
                text_surface = self.button_font.render(line, True, ACCENT_COLOR)
            else:
                text_surface = self.small_font.render(line, True, LIGHT_GRAY)
            
            text_rect = text_surface.get_rect(centerx=get_window_size()[0]//2, y=y_offset)
            self.screen.blit(text_surface, text_rect)
            y_offset += 30 if i == 0 else 25
        
        self.back_button.draw(self.screen)
        
        hint_text = self.small_font.render("Press ESC or BACKSPACE to return to menu", True, LIGHT_GRAY)
        hint_rect = hint_text.get_rect(right=get_window_size()[0] - 20, bottom=get_window_size()[1]-20) 
        self.screen.blit(hint_text, hint_rect)
        
        pygame.display.flip()

    def handle_click(self, pos):
        if self.back_button.check_hover(pos):
            return True
        return None

    def handle_motion(self, pos):
        self.back_button.check_hover(pos)

    def handle_key(self, event):
        if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
            return True
        return None

class GameModePage(BasePage):
    def __init__(self, instructions=None):
        super().__init__(instructions=instructions)
        self.small_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(24))
        
        self.game_mode = "full"
        self.time_limit = None
        self.custom_time_input = ModernInput(
            pygame.Rect(
                (get_window_size()[0] - 300) // 2,
                get_window_size()[1] // 2,
                300,
                60
            ),
            "30",
            self.button_font,
            active_color=TIME_COLOR
        )
        
        self.custom_time_input.placeholder = "Enter time..."
        
        self.last_time_input = "30"
        
        mode_button_width = 400
        button_height = 60
        self.mode_button = ModernButton(
            pygame.Rect(
                (get_window_size()[0] - mode_button_width) // 2,
                get_window_size()[1] // 2 - 20,
                mode_button_width,
                button_height
            ),
            "Game Mode: Full Game",
            self.button_font,
            color=MODE_COLOR
        )
        
        self.time_label = "Time Limit (minutes):"
        
        button_width = 300
        self.start_button = ModernButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] - 120,
                button_width,
                button_height
            ),
            "Start Game",
            self.button_font
        )
        
        self.back_button = ModernButton(
            pygame.Rect(
                20,  
                get_window_size()[1] - 120,
                200, 
                button_height
            ),
            "Back to Menu",  
            self.button_font
        )
        
        self.full_game_text = "Full Game: Last player standing wins"
        self.abridged_text = "Abridged Game: Highest value after time limit wins"
        self.input_error = None

    def draw(self):
        self.draw_background()
        self.draw_title()
        
        self.mode_button.rect.y = get_window_size()[1] // 2 - 20
        self.mode_button.text = f"Game Mode: {'Abridged' if self.game_mode == 'abridged' else 'Full Game'}"
        self.mode_button.draw(self.screen)
        
        mode_info = self.abridged_text if self.game_mode == "abridged" else self.full_game_text
        info_text = self.small_font.render(mode_info, True, LIGHT_GRAY)
        info_rect = info_text.get_rect(centerx=get_window_size()[0]//2, top=self.mode_button.rect.bottom + 10)
        self.screen.blit(info_text, info_rect)
        
        if self.game_mode == "abridged":
            label_text = self.small_font.render(self.time_label, True, LIGHT_GRAY)
            label_rect = label_text.get_rect(centerx=get_window_size()[0]//2, bottom=self.custom_time_input.rect.top - 10)
            self.screen.blit(label_text, label_rect)
            
            self.custom_time_input.draw(self.screen)
            
            if self.input_error:
                error_text = self.small_font.render(self.input_error, True, ERROR_COLOR)
                error_rect = error_text.get_rect(centerx=get_window_size()[0]//2, top=self.custom_time_input.rect.bottom + 5)
                self.screen.blit(error_text, error_rect)
            else:
                try:
                    minutes = int(self.custom_time_input.text)
                    time_info = f"Game will end after {minutes} minutes"
                    time_text = self.small_font.render(time_info, True, LIGHT_GRAY)
                    time_rect = time_text.get_rect(centerx=get_window_size()[0]//2, top=self.custom_time_input.rect.bottom + 5)
                    self.screen.blit(time_text, time_rect)
                except ValueError:
                    pass
        
        self.start_button.draw(self.screen)
        self.back_button.draw(self.screen)
        
        controls = [
            "Controls: ↑/↓ to navigate",
            "M - Change game mode",
        ]
        if self.game_mode == "abridged":
            controls.append("Click on time input to enter custom time")
            
        y_offset = get_window_size()[1] - 150
        for hint in controls:
            hint_text = self.small_font.render(hint, True, LIGHT_GRAY)
            hint_rect = hint_text.get_rect(right=get_window_size()[0] - 20, y=y_offset) 
            self.screen.blit(hint_text, hint_rect)
            y_offset += 25
        
        pygame.display.flip()

    def handle_click(self, pos):
        if self.mode_button.check_hover(pos):
            self.game_mode = "abridged" if self.game_mode == "full" else "full"
            if self.game_mode == "abridged":
                try:
                    minutes = int(self.custom_time_input.text)
                    self.time_limit = minutes * 60
                    print(f"Custom time limit set: {minutes} minutes")
                except ValueError:
                    self.time_limit = 30 * 60  # Default 30 
                    print("Default time limit set: 30 minutes")
            else:
                self.time_limit = None
                print("Game mode changed to Full Game (no time limit)")
            return False
            
        if self.game_mode == "abridged" and self.custom_time_input.rect.collidepoint(pos):
            self.custom_time_input.active = True
            return False
            
        if self.start_button.check_hover(pos):
            if self.game_mode == "abridged":
                try:
                    minutes = int(self.custom_time_input.text)
                    if minutes <= 0:
                        self.input_error = "Time must be greater than 0"
                        return False
                    self.time_limit = minutes * 60
                    self.input_error = None
                    print(f"Starting abridged game with time limit: {minutes} minutes")
                except ValueError:
                    self.input_error = "Please enter a valid number"
                    return False
            else:
                print("Starting full game (no time limit)")
            return True
            
        if self.back_button.check_hover(pos):
            return "back"
        
        self.custom_time_input.active = False
        return False

    def handle_motion(self, pos):
        self.mode_button.check_hover(pos)
        self.start_button.check_hover(pos)
        self.back_button.check_hover(pos)
        
    def handle_key(self, event):
        if self.custom_time_input.active and self.game_mode == "abridged":
            if event.key == pygame.K_RETURN:
                try:
                    minutes = int(self.custom_time_input.text)
                    if minutes <= 0:
                        self.input_error = "Time must be greater than 0"
                        return False
                    self.time_limit = minutes * 60
                    self.input_error = None
                    self.custom_time_input.active = False
                    print(f"Custom time limit set: {minutes} minutes")
                except ValueError:
                    self.input_error = "Please enter a valid number"
                return False
            elif event.key == pygame.K_ESCAPE:
                self.custom_time_input.active = False
                return False
            else:
                if event.key == pygame.K_BACKSPACE:
                    self.custom_time_input.text = self.custom_time_input.text[:-1]
                    self.input_error = None
                    return False
                
                if event.unicode.isdigit():
                    if len(self.custom_time_input.text) < 4:
                        self.custom_time_input.text += event.unicode
                        self.input_error = None
                    return False
                return False
        
        if event.key == pygame.K_m:
            self.game_mode = "abridged" if self.game_mode == "full" else "full"
            if self.game_mode == "abridged":
                try:
                    minutes = int(self.custom_time_input.text)
                    self.time_limit = minutes * 60
                    print(f"Custom time limit set: {minutes} minutes")
                except ValueError:
                    self.time_limit = 30 * 60  # Default 30 
                    print("Default time limit set: 30 minutes")
            else:
                self.time_limit = None
                print("Game mode changed to Full Game (no time limit)")
        elif event.key == pygame.K_RETURN:
            if self.game_mode == "abridged":
                try:
                    minutes = int(self.custom_time_input.text)
                    if minutes <= 0:
                        self.input_error = "Time must be greater than 0"
                        return False
                    self.time_limit = minutes * 60
                    self.input_error = None
                    print(f"Starting abridged game with time limit: {minutes} minutes")
                except ValueError:
                    self.input_error = "Please enter a valid number"
                    return False
            else:
                print("Starting full game (no time limit)")
            return True
        elif event.key == pygame.K_ESCAPE:
            return "back"
        return False

    def get_game_settings(self):
        settings = {
            "mode": self.game_mode,
            "time_limit": None
        }
        
        if self.game_mode == "abridged":
            try:
                minutes = int(self.custom_time_input.text)
                if minutes > 0:
                    settings["time_limit"] = minutes * 60
                    print(f"Game settings: Abridged mode with {minutes} minutes time limit")
                else:
                    settings["time_limit"] = 30 * 60  # Default 30 min
                    print("Game settings: Abridged mode with default 30 minutes time limit (invalid input)")
            except ValueError:
                settings["time_limit"] = 30 * 60  # Default 30 
                print("Game settings: Abridged mode with default 30 minutes time limit (invalid input)")
        else:
            print("Game settings: Full game mode (no time limit)")
            
        return settings

class EndGamePage(BasePage):
    def __init__(self, winner_name, final_assets=None, bankrupted_players=None, voluntary_exits=None, tied_winners=None, lap_count=None):
        super().__init__()
        self.small_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(24))
        self.winner_name = winner_name
        self.final_assets = final_assets or {}
        self.bankrupted_players = bankrupted_players or []
        self.voluntary_exits = voluntary_exits or []
        self.tied_winners = tied_winners or []
        self.lap_count = lap_count or {}
        
        self.screen = pygame.display.get_surface()
        if not self.screen:
            self.screen = pygame.display.set_mode(get_window_size())
            print("Created new surface for EndGamePage")
        else:
            print("Using existing surface for EndGamePage")
            
        try:
            endgame_bg_path = os.path.join(base_path, "assets/image/EndgamePageBG.jpg")
            self.endgame_bg = pygame.image.load(endgame_bg_path)
            self.endgame_bg = pygame.transform.scale(self.endgame_bg, get_window_size())
            print("Loaded EndgamePageBG.jpg successfully")
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load end game background: {e}")
            self.endgame_bg = None
            
        button_width = 300
        button_height = 60
        self.play_again_button = ModernButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] - 100,
                button_width,
                button_height
            ),
            "Play Again",
            self.button_font,
            color=SUCCESS_COLOR
        )
        
        self.quit_button = ModernButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                get_window_size()[1] - 180,
                button_width,
                button_height
            ),
            "Quit Game",
            self.button_font,
            color=ERROR_COLOR
        )
        
        self.confetti = []
        for _ in range(100):
            self.confetti.append({
                'x': random.randint(0, get_window_size()[0]),
                'y': random.randint(-100, 0),
                'speed': random.uniform(1, 3),
                'size': random.randint(5, 15),
                'color': random.choice([
                    (255, 223, 0),  
                    (255, 0, 0),  
                    (0, 255, 0),  
                    (0, 0, 255),  
                    (255, 0, 255), 
                    (0, 255, 255), 
                ])
            })

    def draw(self):

        if hasattr(self, 'endgame_bg') and self.endgame_bg:
            self.screen.blit(self.endgame_bg, (0, 0))
            overlay = pygame.Surface(get_window_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))  
            self.screen.blit(overlay, (0, 0))
        else:
            self.draw_background() 
        
        for particle in self.confetti:
            particle['y'] += particle['speed']
            if particle['y'] > get_window_size()[1]:
                particle['y'] = random.randint(-100, 0)
                particle['x'] = random.randint(0, get_window_size()[0])
            
            pygame.draw.rect(
                self.screen, 
                particle['color'], 
                (particle['x'], particle['y'], particle['size'], particle['size'])
            )
        
        card_width = 700
        card_height = 500
        card_x = (get_window_size()[0] - card_width) // 2
        card_y = (get_window_size()[1] - card_height) // 2 - 30

        shadow = pygame.Surface((card_width + 8, card_height + 8), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, (card_x + 4, card_y + 4))

        pygame.draw.rect(self.screen, WHITE, pygame.Rect(card_x, card_y, card_width, card_height), border_radius=15)

        winner_text = self.title_font.render("Game Over!", True, ACCENT_COLOR)
        self.screen.blit(winner_text, (card_x + (card_width - winner_text.get_width()) // 2, card_y + 30))

        trophy_size = 60
        trophy_x = card_x + (card_width - trophy_size) // 2
        trophy_y = card_y + 80
        
        gold_color = (255, 215, 0)
        
        pygame.draw.rect(
            self.screen,
            gold_color,
            (trophy_x + 15, trophy_y + 45, 30, 15),
            border_radius=5
        )
        
        pygame.draw.rect(
            self.screen,
            gold_color,
            (trophy_x + 25, trophy_y + 25, 10, 25)
        )
        
        pygame.draw.ellipse(
            self.screen,
            gold_color,
            (trophy_x + 10, trophy_y, 40, 30)
        )
        
        pygame.draw.ellipse(
            self.screen,
            gold_color,
            (trophy_x, trophy_y + 10, 15, 20)
        )
        pygame.draw.ellipse(
            self.screen,
            gold_color,
            (trophy_x + 45, trophy_y + 10, 15, 20)
        )

        if self.winner_name == "Tie" and self.tied_winners:
            winner_text = "It's a Tie!"
            winner_name = self.button_font.render(winner_text, True, SUCCESS_COLOR)
            self.screen.blit(winner_name, (card_x + (card_width - winner_name.get_width()) // 2, card_y + 150))
            
            tied_text = self.small_font.render(
                f"Tied players: {', '.join(self.tied_winners)}", True, ACCENT_COLOR
            )
            self.screen.blit(tied_text, (card_x + (card_width - tied_text.get_width()) // 2, card_y + 180))
        else:
            winner_name = self.button_font.render(f"Winner: {self.winner_name}", True, SUCCESS_COLOR)
            self.screen.blit(winner_name, (card_x + (card_width - winner_name.get_width()) // 2, card_y + 150))

        pygame.draw.line(
            self.screen, 
            LIGHT_GRAY, 
            (card_x + 50, card_y + 190), 
            (card_x + card_width - 50, card_y + 190), 
            2
        )

        y_offset = card_y + 210
        if self.final_assets:
            assets_title = self.button_font.render("Final Assets", True, BLACK)
            self.screen.blit(assets_title, (card_x + (card_width - assets_title.get_width()) // 2, y_offset))
            y_offset += 40
            
            sorted_assets = sorted(self.final_assets.items(), key=lambda x: x[1], reverse=True)
            col_width = (card_width - 100) // 2
            
            for i, (name, amount) in enumerate(sorted_assets):
                col = i % 2
                row = i // 2
                
                x_pos = card_x + 50 + col * col_width
                y_pos = y_offset + row * 35
                
                if self.tied_winners and name in self.tied_winners:
                    text_color = SUCCESS_COLOR
                elif name == self.winner_name and not self.tied_winners:
                    text_color = SUCCESS_COLOR
                else:
                    text_color = LIGHT_GRAY
                
                player_text = self.small_font.render(
                    f"{name}: £{amount:,}", True, text_color
                )
                self.screen.blit(player_text, (x_pos, y_pos))

        if self.bankrupted_players:
            y_offset = y_offset + (len(sorted_assets) // 2 + (1 if len(sorted_assets) % 2 else 0)) * 35 + 20
            
            bankrupt_title = self.small_font.render("Bankrupted Players:", True, ERROR_COLOR)
            self.screen.blit(bankrupt_title, (card_x + 50, y_offset))
            y_offset += 30
            
            bankrupt_text = self.small_font.render(
                f"{', '.join(self.bankrupted_players)}", True, ERROR_COLOR
            )
            self.screen.blit(bankrupt_text, (card_x + 70, y_offset))
            y_offset += 40  

        if self.voluntary_exits:
            y_offset += 20 
            voluntary_title = self.small_font.render("Voluntary Exits:", True, ACCENT_COLOR)
            self.screen.blit(voluntary_title, (card_x + 50, y_offset))
            y_offset += 30
            
            voluntary_text = self.small_font.render(
                f"{', '.join(self.voluntary_exits)}", True, ACCENT_COLOR
            )
            self.screen.blit(voluntary_text, (card_x + 70, y_offset))
            y_offset += 40 

        if self.lap_count:
            y_offset += 50 
            
            lap_title = self.small_font.render("Laps Completed:", True, ACCENT_COLOR)
            self.screen.blit(lap_title, (card_x + 50, y_offset))
            y_offset += 30
            
            sorted_laps = sorted(self.lap_count.items(), key=lambda x: x[1], reverse=True)
            
            lap_text_parts = []
            for name, laps in sorted_laps:
                if (self.tied_winners and name in self.tied_winners) or (name == self.winner_name and not self.tied_winners):
                    lap_text_parts.append(f"{name}: {laps}")
                else:
                    lap_text_parts.append(f"{name}: {laps}")
            
            lap_text_combined = ", ".join(lap_text_parts)
            max_width = card_width - 140 
            
            test_text = self.small_font.render(lap_text_combined, True, ACCENT_COLOR)
            if test_text.get_width() > max_width:
                current_line = ""
                current_y = y_offset
                
                for i, part in enumerate(lap_text_parts):
                    test_line = current_line + (", " if current_line else "") + part
                    test_render = self.small_font.render(test_line, True, ACCENT_COLOR)
                    
                    if test_render.get_width() > max_width and current_line:
                        line_text = self.small_font.render(current_line, True, ACCENT_COLOR)
                        self.screen.blit(line_text, (card_x + 70, current_y))
                        current_y += 25
                        current_line = part
                    else:
                        current_line = test_line if not current_line else current_line + ", " + part
                
                if current_line:
                    line_text = self.small_font.render(current_line, True, ACCENT_COLOR)
                    self.screen.blit(line_text, (card_x + 70, current_y))
            else:
                lap_text = self.small_font.render(lap_text_combined, True, ACCENT_COLOR)
                self.screen.blit(lap_text, (card_x + 70, y_offset))

        self.play_again_button.draw(self.screen)
        self.quit_button.draw(self.screen)

    def handle_click(self, pos):
        if self.play_again_button.check_hover(pos):
            return "play_again"
        elif self.quit_button.check_hover(pos):
            return "quit"
        return None

    def handle_motion(self, pos):
        self.play_again_button.check_hover(pos)
        self.quit_button.check_hover(pos)

    def handle_key(self, event):
        if event.key == pygame.K_SPACE:
            return "play_again"
        elif event.key == pygame.K_ESCAPE:
            return "quit"
        return None

class AIDifficultyPage(BasePage):
    def __init__(self, instructions=None):
        super().__init__(instructions=instructions)
        self.small_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(24))
        button_width = 300
        button_height = 60
        center_y = get_window_size()[1] // 2 + 50 

        self.easy_button = ModernButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                center_y - 50,
                button_width,
                button_height
            ),
            "Easy",
            self.button_font,
            color=SUCCESS_COLOR
        )

        self.hard_button = ModernButton(
            pygame.Rect(
                (get_window_size()[0] - button_width) // 2,
                center_y + 50,
                button_width,
                button_height
            ),
            "Hard",
            self.button_font,
            color=ERROR_COLOR
        )

        self.back_button = ModernButton(
            pygame.Rect(
                20,  
                get_window_size()[1] - 120,
                200,  
                button_height
            ),
            "Back to Menu", 
            self.button_font
        )

    def draw(self):
        self.draw_background()
        self.draw_title()

        difficulty_text = self.button_font.render("Select AI Difficulty", True, WHITE)
        text_rect = difficulty_text.get_rect(centerx=get_window_size()[0]//2, y=250) 
        self.screen.blit(difficulty_text, text_rect)

        easy_desc = self.small_font.render("AI will make basic decisions", True, LIGHT_GRAY)
        easy_rect = easy_desc.get_rect(centerx=get_window_size()[0]//2, y=self.easy_button.rect.bottom + 10)
        
        hard_desc = self.small_font.render("AI will make strategic decisions", True, LIGHT_GRAY)
        hard_rect = hard_desc.get_rect(centerx=get_window_size()[0]//2, y=self.hard_button.rect.bottom + 10)

        self.easy_button.draw(self.screen)
        self.hard_button.draw(self.screen)
        
        self.screen.blit(easy_desc, easy_rect)
        self.screen.blit(hard_desc, hard_rect)

        controls = [
            "Press E for Easy mode",
            "Press H for Hard mode"
        ]
        y_offset = get_window_size()[1] - 150  
        for hint in controls:
            hint_text = self.small_font.render(hint, True, LIGHT_GRAY)
            hint_rect = hint_text.get_rect(right=get_window_size()[0] - 20, y=y_offset)  
            self.screen.blit(hint_text, hint_rect)
            y_offset += 25

        self.back_button.draw(self.screen)

        pygame.display.flip()

    def handle_click(self, pos):
        if self.back_button.check_hover(pos):
            return "back"
        if self.easy_button.check_hover(pos):
            return "easy"
        elif self.hard_button.check_hover(pos):
            return "hard"
        return None

    def handle_motion(self, pos):
        self.back_button.check_hover(pos)
        self.easy_button.check_hover(pos)
        self.hard_button.check_hover(pos)

    def handle_key(self, event):
        if event.key == pygame.K_ESCAPE:
            return "back"
        elif event.key in [pygame.K_e, pygame.K_RETURN]:
            return "easy"
        elif event.key == pygame.K_h:
            return "hard"
        return None

class DevelopmentNotification:
    def __init__(self, screen, player_name, font=None):
        self.screen = screen
        self.player_name = player_name
        self.window_size = screen.get_size()
        
        if font:
            self.font = font
        else:
            self.font = pygame.font.Font(FONT_PATH, 24)
            
        self.dev_font = pygame.font.Font(FONT_PATH, 26)
        
        self.text = f"{self.player_name}, you may modify properties now"
        
        self.padding = 20
        self.notification_text = self.dev_font.render(self.text, True, WHITE)
        self.bg_width = self.notification_text.get_width() + self.padding * 2
        self.bg_height = self.notification_text.get_height() + self.padding * 2
        
        self.x = (self.window_size[0] - self.bg_width) // 2
        self.y = 80
        
        self.button_width = 150
        self.button_height = 50
        self.continue_button = pygame.Rect(
            (self.window_size[0] - self.button_width) // 2, 
            self.y + self.bg_height + 15,
            self.button_width, 
            self.button_height
        )
        
        self.dev_color = (0, 180, 120)

    def draw(self, mouse_pos):
        bg_surface = pygame.Surface((self.bg_width, self.bg_height), pygame.SRCALPHA)
        
        pygame.draw.rect(bg_surface, (*self.dev_color, 230), bg_surface.get_rect(), border_radius=15)
        
        for i in range(4):
            alpha = 80 - i * 20
            pygame.draw.rect(bg_surface, (*self.dev_color, alpha), 
                           (-i, -i, self.bg_width + i*2, self.bg_height + i*2), 
                           border_radius=15)
        
        self.screen.blit(bg_surface, (self.x, self.y))
        self.screen.blit(self.notification_text, (self.x + self.padding, self.y + self.padding))
        
        hover = self.continue_button.collidepoint(mouse_pos)
        button_color = (50, 180, 100) if hover else (30, 150, 80)
        
        pygame.draw.rect(self.screen, button_color, self.continue_button, border_radius=10)
        pygame.draw.rect(self.screen, (255, 255, 255), self.continue_button, 2, border_radius=10)
        
        button_text = self.font.render("Continue", True, WHITE)
        text_x = self.continue_button.x + (self.continue_button.width - button_text.get_width()) // 2
        text_y = self.continue_button.y + (self.continue_button.height - button_text.get_height()) // 2
        self.screen.blit(button_text, (text_x, text_y))
    
    def check_button_click(self, pos):
        return self.continue_button.collidepoint(pos)

class AIEmotionUI:
    
    def __init__(self, screen, ai_player, game_instance):

        self.screen = screen
        self.ai_player = ai_player
        self.game = game_instance
        self.visible = False
        self.window_size = get_window_size()
        
        button_size = (48, 48)
        panel_width = 130
        panel_height = 160
        
        self.panel_rect = pygame.Rect(
            self.window_size[0] - panel_width - 20,  
            200,  
            panel_width,
            panel_height
        )
        
        self.happy_button_rect = pygame.Rect(
            self.panel_rect.x + (self.panel_rect.width - button_size[0]) // 2,
            self.panel_rect.y + 30,  
            button_size[0],
            button_size[1]
        )
        
        self.angry_button_rect = pygame.Rect(
            self.panel_rect.x + (self.panel_rect.width - button_size[0]) // 2,
            self.panel_rect.y + 30 + button_size[1] + 15,   
            button_size[0],
            button_size[1]
        )
        
        self.happy_image = None
        self.angry_image = None
        self.happy_hover = False
        self.angry_hover = False
        
        try:
            happy_path = os.path.join(base_path, "assets/image/Happy.png")
            self.happy_image = pygame.image.load(happy_path)
            self.happy_image = pygame.transform.scale(self.happy_image, button_size)
            
            angry_path = os.path.join(base_path, "assets/image/Angry.png")
            self.angry_image = pygame.image.load(angry_path)
            self.angry_image = pygame.transform.scale(self.angry_image, button_size)
        except (pygame.error, FileNotFoundError):
            print("Could not load emotion king images")
            self.happy_image = pygame.Surface(button_size)
            self.happy_image.fill((50, 200, 50))
            self.angry_image = pygame.Surface(button_size)
            self.angry_image.fill((200, 50, 50))
        
        self.font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(14))
        
        self.happy_clicks_after_limit = 0
        self.angry_clicks_after_limit = 0
        self.easter_egg_threshold = 5
        self.youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&pp=ygUJcmljayByb2xs"
        self.easter_egg_triggered = False
    
    def show(self):
        self.visible = True
    
    def hide(self):
        self.visible = False
    
    def draw(self):
        if not self.visible:
            return
            
        if not self.ai_player or not self.ai_player.is_ai or not hasattr(self.ai_player, 'ai_controller') or not hasattr(self.ai_player.ai_controller, 'mood_modifier'):
            return
            
        pygame.draw.rect(self.screen, (*MODERN_BG, 220), self.panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, ACCENT_COLOR, self.panel_rect, 2, border_radius=10)
        
        title_text = self.font.render("Taunt", True, WHITE)
        title_rect = title_text.get_rect(centerx=self.panel_rect.centerx, y=self.panel_rect.y + 5)
        self.screen.blit(title_text, title_rect)
        
        if self.happy_hover:
            glow = pygame.Surface((self.happy_button_rect.width + 4, self.happy_button_rect.height + 4), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 255, 255, 128), glow.get_rect(), border_radius=5)
            self.screen.blit(glow, (self.happy_button_rect.x - 2, self.happy_button_rect.y - 2))
            
        if self.angry_hover:
            glow = pygame.Surface((self.angry_button_rect.width + 4, self.angry_button_rect.height + 4), pygame.SRCALPHA)
            pygame.draw.rect(glow, (255, 255, 255, 128), glow.get_rect(), border_radius=5)
            self.screen.blit(glow, (self.angry_button_rect.x - 2, self.angry_button_rect.y - 2))
        
        self.screen.blit(self.happy_image, self.happy_button_rect)
        self.screen.blit(self.angry_image, self.angry_button_rect)
        
        mood_value = getattr(self.ai_player.ai_controller, 'mood_modifier', 0)
        mood_text = f"Mood: {mood_value:.2f}"
        mood_color = (
            int(255 * min(1, max(0, (mood_value + 0.3) / 0.6))),
            int(255 * min(1, max(0, (0.3 - mood_value) / 0.6))),
            50
        )
        mood_surface = self.font.render(mood_text, True, mood_color)
        mood_rect = mood_surface.get_rect(centerx=self.panel_rect.centerx, bottom=self.panel_rect.bottom - 5)
        self.screen.blit(mood_surface, mood_rect)
        
        total_clicks = self.happy_clicks_after_limit + self.angry_clicks_after_limit
        if total_clicks > 0 and total_clicks < self.easter_egg_threshold:
            egg_text = f"{self.easter_egg_threshold - total_clicks} more..."
            egg_surface = self.font.render(egg_text, True, (255, 215, 0))
            egg_rect = egg_surface.get_rect(centerx=self.panel_rect.centerx, bottom=self.panel_rect.bottom - 25)
            self.screen.blit(egg_surface, egg_rect)
    
    def check_hover(self, pos):

        if not self.visible:
            return False
            
        self.happy_hover = self.happy_button_rect.collidepoint(pos)
        self.angry_hover = self.angry_button_rect.collidepoint(pos)
        
        return self.happy_hover or self.angry_hover
    
    def handle_click(self, pos):

        if not self.visible:
            return False
            
        if self.happy_button_rect.collidepoint(pos):
            mood_value = getattr(self.ai_player.ai_controller, 'mood_modifier', 0)
            if mood_value >= 0.3:
                self.happy_clicks_after_limit += 1
                self._check_easter_egg()
            
            print(f"Happy button clicked for {self.ai_player.name} - making AI happier")
            self.game.update_ai_mood(self.ai_player.name, False)
            return True
            
        if self.angry_button_rect.collidepoint(pos):
            mood_value = getattr(self.ai_player.ai_controller, 'mood_modifier', 0)
            if mood_value <= -0.3:
                self.angry_clicks_after_limit += 1
                self._check_easter_egg()
            
            print(f"Angry button clicked for {self.ai_player.name} - making AI angrier")
            self.game.update_ai_mood(self.ai_player.name, True)
            return True
            
        return False
        
    def _check_easter_egg(self):
        total_clicks = self.happy_clicks_after_limit + self.angry_clicks_after_limit
        
        if total_clicks >= self.easter_egg_threshold and not self.easter_egg_triggered:
            try:
                print("Easter egg triggered: Opening YouTube...")
                webbrowser.open(self.youtube_url)
                self.easter_egg_triggered = True
                self.happy_clicks_after_limit = 0
                self.angry_clicks_after_limit = 0
            except Exception as e:
                print(f"Error opening YouTube URL: {e}")
