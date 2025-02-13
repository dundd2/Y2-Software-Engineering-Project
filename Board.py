# Base on PropertyTycoonCardData.xlsx from canvas 
# script based on Eric's provided flowchart photo (flowchart.drawio.png)
# will add more comment later to reference for which part of code is based on which part of the flowchart

import pygame
import math
from Property import Property
from typing import Optional, List
from loadexcel import load_property_data

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
MODERN_BG = (18, 18, 18)
ACCENT_COLOR = (75, 139, 190)
SUCCESS_COLOR = (40, 167, 69)
ERROR_COLOR = (220, 53, 69)

GROUP_COLORS = {
    "Brown": (139, 69, 19, 180),
    "Blue": (0, 0, 255, 180),
    "Purple": (128, 0, 128, 180),
    "Orange": (255, 165, 0, 180),
    "Red": (255, 0, 0, 180),
    "Yellow": (255, 255, 0, 180),
    "Green": (0, 128, 0, 180),
    "Deep Blue": (0, 0, 139, 180)
}

class Board:
    def __init__(self):
        self.spaces = [None] * 40
        self.properties_data = load_property_data()
        print("Board init - Properties data loaded:", bool(self.properties_data))
        
        if not self.properties_data:
            raise RuntimeError("Failed to load properties data")
            
        self.board_rects = self._create_board_rects()
        self.card_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.messages = []
        self.message_times = []
        self.animation_time = 0
        self.ANIMATION_DURATION = 2000

        self.special_spaces = {
            "1": "GO",
            "3": "Pot Luck",
            "5": "Income Tax",
            "8": "Opportunity Knocks",
            "11": "JAIL",
            "18": "Pot Luck",
            "21": "Free Parking",
            "23": "Opportunity Knocks",
            "31": "Go to Jail",
            "34": "Pot Luck",
            "37": "Opportunity Knocks",
            "39": "Super Tax"
        }
        
        self.image_mappings = {
            "GO": "Collect 200.png",
            "Pot Luck": "community chest.png",
            "Income Tax": "Pay 200.png",
            "Opportunity Knocks": "Draw a card.png",
            "JAIL": "Jail.png",
            "Free Parking": "Collect Fine.png",
            "Go to Jail": "Go to Jail!.png",
            "Super Tax": "Pay 200.png"
        }
        
        self.position_scales = {
            "corner": 1.0,
            "horizontal": 0.9,
            "vertical": 0.9,
        }
        
        self.space_images = {}
        self.load_space_images()
        
        for position_str, prop_data in self.properties_data.items():
            try:
                position = int(position_str)
                array_pos = position - 1
                if 0 <= array_pos < 40:
                    name = prop_data.get("name", "")
                    if "Station" in name:
                        self.spaces[array_pos] = Property(name, 200, 25)
                    elif name in ["Tesla Power Co", "Edison Water"]:
                        self.spaces[array_pos] = Property(name, 150, 0)
                    elif "price" in prop_data and prop_data.get("price"):
                        price = int(prop_data["price"])
                        rent = int(prop_data.get("rent", 0))
                        self.spaces[array_pos] = Property(name, price, rent)
                        
                    if prop_data.get("owner"):
                        self.spaces[array_pos].owner = prop_data["owner"]
            except (ValueError, TypeError) as e:
                print(f"Error processing position {position_str}: {e}")
                continue

    def load_space_images(self):
        try:
            import os
            base_dir = os.path.dirname(os.path.abspath(__file__))
            images_dir = os.path.join(base_dir, "assets", "image")
            
            for space_name, image_file in self.image_mappings.items():
                try:
                    image_path = os.path.join(images_dir, image_file)
                    image = pygame.image.load(image_path)
                    self.space_images[space_name] = image
                except pygame.error as e:
                    print(f"Could not load image for {space_name}: {e}")
                    self.space_images[space_name] = None
        except Exception as e:
            print(f"Error loading space images: {e}")

    def _create_board_rects(self):
        screen_info = pygame.display.Info()
        window_width = screen_info.current_w
        window_height = screen_info.current_h
        
        board_size = min(window_width, window_height) * 0.8
        space_size = board_size // 11
        start_x = (window_width - board_size) // 2
        start_y = (window_height - board_size) // 2

        rects = [None] * 40

        for i in range(11):
            rects[i] = pygame.Rect(
                start_x + board_size - (i + 1) * space_size,
                start_y + board_size - space_size,
                space_size,
                space_size
            )

        for i in range(11, 21):
            rects[i] = pygame.Rect(
                start_x,
                start_y + board_size - ((i - 9) * space_size),
                space_size,
                space_size
            )

        for i in range(21, 31):
            rects[i] = pygame.Rect(
                start_x + (i - 21) * space_size,
                start_y,
                space_size,
                space_size
            )

        for i in range(31, 40):
            rects[i] = pygame.Rect(
                start_x + board_size - space_size,
                start_y + (i - 31) * space_size,
                space_size,
                space_size
            )

        return rects

    def draw_player(self, screen, player, rect, index):
        is_corner = rect.width > rect.height + 10 or rect.height > rect.width + 10
        
        row = index // 2
        col = index % 2
        
        base_padding = 12 if is_corner else 8
        spacing = 35 if is_corner else 30
        
        if rect.width > rect.height + 10:
            pos_x = rect.x + base_padding + (col * spacing)
            pos_y = rect.y + (rect.height - 40) // 2 + (row * spacing // 2)
        elif rect.height > rect.width + 10:
            pos_x = rect.x + (rect.width - 40) // 2 + (col * spacing // 2)
            pos_y = rect.y + base_padding + (row * spacing)
        else:
            pos_x = rect.x + base_padding + (col * spacing)
            pos_y = rect.y + base_padding + (row * spacing)
        
        glow_size = 44
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        for i in range(4):
            alpha = int(100 * (1 - i/4))
            pygame.draw.rect(glow_surface, (*player.color[:3], alpha),
                            pygame.Rect(i, i, glow_size - i*2, glow_size - i*2),
                            border_radius=5)
        screen.blit(glow_surface, (pos_x - 2, pos_y - 2 - player.animation_offset))
        
        if player.player_image:
            token_rect = pygame.Rect(pos_x, pos_y - player.animation_offset, 40, 40)
            screen.blit(player.player_image, token_rect)

    def add_message(self, text):
        self.messages.append(text)
        self.message_times.append(pygame.time.get_ticks())
        if len(self.messages) > 10:
            self.messages.pop(0)
            self.message_times.pop(0)

    def draw(self, screen):
        window_width = screen.get_width()
        window_height = screen.get_height()
        
        board_size = int(window_height * 0.8)
        board_rect = pygame.Rect(
            (window_width - board_size) // 2,
            (window_height - board_size) // 2,
            board_size, board_size
        )
        
        shadow_size = 30
        shadow_surface = pygame.Surface((board_rect.width + shadow_size*2, board_rect.height + shadow_size*2), pygame.SRCALPHA)
        for i in range(shadow_size):
            alpha = int(100 * (1 - i/shadow_size))
            pygame.draw.rect(shadow_surface, (*BLACK, alpha),
                           pygame.Rect(i, i, 
                                     shadow_surface.get_width() - i*2,
                                     shadow_surface.get_height() - i*2),
                           border_radius=15)
        screen.blit(shadow_surface, 
                   (board_rect.x - shadow_size, board_rect.y - shadow_size))
        
        center_rect = pygame.Rect(
            board_rect.left + board_size//11,
            board_rect.top + board_size//11,
            board_size - 2*(board_size//11),
            board_size - 2*(board_size//11)
        )
        
        inner_gradient = pygame.Surface(center_rect.size, pygame.SRCALPHA)
        for i in range(center_rect.height):
            alpha = int(200 * (1 - i/center_rect.height))
            pygame.draw.line(inner_gradient, (*ACCENT_COLOR[:3], alpha),
                           (0, i), (center_rect.width, i))
        screen.blit(inner_gradient, center_rect)
        
        logo_text = self.title_font.render("Property", True, WHITE)
        logo_text2 = self.title_font.render("Tycoon", True, WHITE)
        logo_rect = logo_text.get_rect(centerx=center_rect.centerx, bottom=center_rect.centery-5)
        logo_rect2 = logo_text2.get_rect(centerx=center_rect.centerx, top=center_rect.centery+5)
        
        glow_size = 10
        glow_surface = pygame.Surface((logo_rect.width + glow_size*2, logo_rect.height*2 + glow_size*2 + 10), pygame.SRCALPHA)
        for i in range(glow_size):
            alpha = int(50 * (1 - i/glow_size))
            pygame.draw.rect(glow_surface, (*ACCENT_COLOR[:3], alpha),
                           pygame.Rect(i, i, 
                                     glow_surface.get_width() - i*2,
                                     glow_surface.get_height() - i*2),
                           border_radius=5)
        screen.blit(glow_surface, 
                   (logo_rect.x - glow_size, logo_rect.y - glow_size))
        
        screen.blit(logo_text, logo_rect)
        screen.blit(logo_text2, logo_rect2)
        
        current_time = pygame.time.get_ticks()
        animation_progress = (current_time % self.ANIMATION_DURATION) / self.ANIMATION_DURATION
        
        for i, rect in enumerate(self.board_rects):
            space = self.spaces[i]
            space_data = self.properties_data.get(str(i + 1), {})
            
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            base_color = MODERN_BG
            
            if space_data:
                group = space_data.get("group")
                name = space_data.get("name", "")
                
                if group in GROUP_COLORS:
                    base_color = GROUP_COLORS[group][:3]
                elif "Station" in name:
                    base_color = (100, 100, 100)
                elif name in ["Tesla Power Co", "Edison Water"]:
                    base_color = (100, 100, 0)
                
                if space and space.owner:
                    alpha = int(180 + 75 * abs(math.sin(2 * math.pi * animation_progress)))
                    pygame.draw.rect(s, (*base_color, alpha), s.get_rect(), border_radius=5)
                else:
                    pygame.draw.rect(s, (*base_color, 180), s.get_rect(), border_radius=5)
            
            screen.blit(s, rect)
            
            self.draw_space_contents(screen, rect, space, space_data)
            
            if space and space.owner:
                border_color = SUCCESS_COLOR
                for thickness in range(2):
                    pygame.draw.rect(screen, border_color, 
                                   rect.inflate(thickness*2, thickness*2), 
                                   1, border_radius=5)
            else:
                pygame.draw.rect(screen, WHITE, rect, 1, border_radius=5)

        info_panel_width = 300
        info_panel_height = 100
        info_panel_x = 20
        info_panel_y = window_height - info_panel_height - 20
        
        panel_shadow = pygame.Surface((info_panel_width + 8, info_panel_height + 8), pygame.SRCALPHA)
        for i in range(4):
            alpha = int(100 * (1 - i/4))
            pygame.draw.rect(panel_shadow, (*BLACK, alpha),
                           pygame.Rect(i, i, info_panel_width + 8 - i*2, info_panel_height + 8 - i*2),
                           border_radius=10)
        screen.blit(panel_shadow, (info_panel_x - 4, info_panel_y - 4))
        
        info_panel = pygame.Surface((info_panel_width, info_panel_height), pygame.SRCALPHA)
        pygame.draw.rect(info_panel, (*MODERN_BG, 200), info_panel.get_rect(), border_radius=10)
        screen.blit(info_panel, (info_panel_x, info_panel_y))
        
        text_y = info_panel_y + 10
        current_time = pygame.time.get_ticks()
        messages_to_remove = []
        
        visible_messages = self.messages[-3:]
        for message in visible_messages:
            text = self.small_font.render(message, True, WHITE)
            text_rect = text.get_rect(left=info_panel_x + 10, top=text_y)
            screen.blit(text, text_rect)
            text_y += 25
        
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]
            self.message_times = self.message_times[-10:]

    def draw_space_contents(self, screen, rect, space, space_data):
        name = space_data.get("name", "")
        position = space_data.get("position", "")
        group = space_data.get("group")
        header_height = rect.height * 0.2

        is_corner = rect.width > rect.height + 10 or rect.height > rect.width + 10
        is_horizontal = rect.width > rect.height
        scale_factor = (
            self.position_scales["corner"] if is_corner
            else self.position_scales["horizontal"] if is_horizontal
            else self.position_scales["vertical"]
        )

        depth = 4
        shadow = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        for i in range(depth):
            alpha = int(100 * (1 - i/depth))
            pygame.draw.rect(shadow, (*BLACK, alpha), 
                           shadow.get_rect().inflate(-i*2, -i*2), 0, border_radius=3)
        screen.blit(shadow, rect)

        if group in GROUP_COLORS:
            header_rect = pygame.Rect(rect.x, rect.y, rect.width, header_height)
            color = GROUP_COLORS[group]
            pygame.draw.rect(screen, color, header_rect, border_radius=5)
            pygame.draw.rect(screen, WHITE, header_rect, 1, border_radius=5)

        space_key = self.special_spaces.get(str(position), name)
        space_image = self.space_images.get(space_key)

        if space_image:
            available_height = rect.height - (header_height if group in GROUP_COLORS else 0)
            available_width = rect.width
            
            img_rect = space_image.get_rect()
            space_width = available_width * scale_factor
            space_height = available_height * scale_factor
            
            new_scale = min(
                space_width / img_rect.width,
                space_height / img_rect.height
            )
            
            new_width = int(img_rect.width * new_scale)
            new_height = int(img_rect.height * new_scale)
            
            try:
                scaled_image = pygame.transform.scale(space_image, (new_width, new_height))
                
                if is_corner:
                    image_x = rect.centerx - new_width // 2
                    image_y = rect.centery - new_height // 2
                elif is_horizontal:
                    image_x = rect.centerx - new_width // 2
                    if group in GROUP_COLORS:
                        image_y = rect.y + header_height + (available_height - new_height) // 2
                    else:
                        image_y = rect.centery - new_height // 2
                else:
                    image_x = rect.centerx - new_width // 2
                    if group in GROUP_COLORS:
                        image_y = rect.y + header_height + (available_height - new_height) // 2
                    else:
                        image_y = rect.centery - new_height // 2
                
                screen.blit(scaled_image, (image_x, image_y))
            except (pygame.error, ValueError) as e:
                print(f"Error scaling image for {name}: {e}")
                self._draw_fallback_text(screen, rect, name, group)
        else:
            self._draw_fallback_text(screen, rect, name, group)
            
        if space and hasattr(space, 'price'):
            price_font = pygame.font.Font(None, 16)
            price_text = price_font.render(f"£{space.price}", True, WHITE)
            price_rect = price_text.get_rect(centerx=rect.centerx, bottom=rect.bottom-2)
            screen.blit(price_text, price_rect)
            
            if space.owner:
                current_time = pygame.time.get_ticks()
                alpha = int(128 + 127 * math.sin(current_time * 0.003))
                s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.rect(s, (*ACCENT_COLOR, alpha), s.get_rect(), 2, border_radius=5)
                screen.blit(s, rect)
                
                owner_text = price_font.render(space.owner, True, WHITE)
                owner_rect = owner_text.get_rect(centerx=rect.centerx, bottom=rect.bottom-2)
                screen.blit(owner_text, owner_rect)

    def _draw_fallback_text(self, screen, rect, name, group):
        available_width = rect.width - 10
        text_size = 24
        while text_size > 16:
            test_font = pygame.font.Font(None, text_size)
            if test_font.size(name)[0] <= available_width:
                break
            text_size -= 1
        
        font = pygame.font.Font(None, text_size)
        y_offset = rect.height * 0.2 if group in GROUP_COLORS else 5
        
        name_shadow = font.render(name, True, BLACK)
        name_rect_shadow = name_shadow.get_rect(centerx=rect.centerx+1, top=rect.top+y_offset+1)
        screen.blit(name_shadow, name_rect_shadow)
        
        name_text = font.render(name, True, WHITE)
        name_rect = name_text.get_rect(centerx=rect.centerx, top=rect.top+y_offset)
        screen.blit(name_text, name_rect)

    def get_space(self, position):
        array_pos = (position - 1) % 40
        if 0 <= array_pos < len(self.spaces):
            return self.spaces[array_pos]
        return None

    def update_ownership(self, properties_data):
        for position_str, prop_data in properties_data.items():
            try:
                position = int(position_str)
                array_pos = position - 1
                if 0 <= array_pos < 40 and self.spaces[array_pos]:
                    self.spaces[array_pos].owner = prop_data.get("owner")
            except (ValueError, TypeError):
                continue

    def get_property_group(self, position):
        if str(position) in self.properties_data:
            return self.properties_data[str(position)].get("group")
        return None