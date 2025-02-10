## to do :  there are some board game ui in the script right now ,need to move to ui.py
# change the WINDOW_SIZE later with the ui setting

import pygame
import math
from Property import Property
from typing import Optional, List
from loadexcel import load_property_data

WINDOW_SIZE = (1280, 720)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
MODERN_BG = (18, 18, 18)
ACCENT_COLOR = (75, 139, 190)

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

        self.board_rects = self._create_board_rects()
        self.card_font = pygame.font.Font(None, 18)
        self.title_font = pygame.font.Font(None, 20)
        self.message_font = pygame.font.Font(None, 32)
        
        self.messages = []
        self.message_duration = 3000
        self.message_times = []
        self.glow_surfaces = {}
        self.animation_time = 0
        self.ANIMATION_DURATION = 2000

    def _create_board_rects(self):
        rects = [None] * 40
        board_size = 600
        space_size = board_size // 11
        start_x = (WINDOW_SIZE[0] - board_size) // 2
        start_y = (WINDOW_SIZE[1] - board_size) // 2

        for i in range(10):
            rects[i] = pygame.Rect(
                start_x + (9-i) * space_size,
                start_y + board_size - space_size,
                space_size,
                space_size
            )

        for i in range(10, 20):
            rects[i] = pygame.Rect(
                start_x,
                start_y + (19-i) * space_size,
                space_size,
                space_size
            )

        for i in range(20, 30):
            rects[i] = pygame.Rect(
                start_x + (i-20) * space_size,
                start_y,
                space_size,
                space_size
            )

        for i in range(30, 40):
            rects[i] = pygame.Rect(
                start_x + board_size - space_size,
                start_y + (i-30) * space_size,
                space_size,
                space_size
            )

        return rects

    def draw_player(self, screen, player, rect, index):
        emoji = "😎🤠🤓😊🥳"[index % 5]
        
        pos_x = rect.x + 10 + (index * 15)
        pos_y = rect.y + 10 + (index * 15)
        
        token_size = 24
        glow_surface = pygame.Surface((token_size + 8, token_size + 8), pygame.SRCALPHA)
        
        for i in range(4):
            alpha = int(100 * (1 - i/4))
            pygame.draw.circle(glow_surface, (*ACCENT_COLOR[:3], alpha),
                            (token_size//2 + 4, token_size//2 + 4), token_size//2 - i)
        
        screen.blit(glow_surface, (pos_x - 4, pos_y - 4))
        
        text = self.card_font.render(emoji, True, WHITE)
        text_rect = text.get_rect(center=(pos_x + token_size//2, pos_y + token_size//2))
        screen.blit(text, text_rect)

    def add_message(self, text):
        self.messages.append(text)
        self.message_times.append(pygame.time.get_ticks())

    def draw(self, screen):
        screen.fill(MODERN_BG)
        
        gradient = pygame.Surface((WINDOW_SIZE[0], WINDOW_SIZE[1]), pygame.SRCALPHA)
        for i in range(WINDOW_SIZE[1]):
            alpha = int(255 * (1 - i/WINDOW_SIZE[1]))
            pygame.draw.line(gradient, (*ACCENT_COLOR[:3], alpha), (0, i), (WINDOW_SIZE[0], i))
        screen.blit(gradient, (0, 0))

        board_rect = pygame.Rect(
            (WINDOW_SIZE[0] - 600) // 2,
            (WINDOW_SIZE[1] - 600) // 2,
            600, 600
        )
        
        glow_size = 20
        glow_surface = pygame.Surface((
            board_rect.width + glow_size * 2,
            board_rect.height + glow_size * 2
        ), pygame.SRCALPHA)
        
        for i in range(glow_size):
            alpha = int(100 * (1 - i/glow_size))
            pygame.draw.rect(glow_surface, (*ACCENT_COLOR[:3], alpha),
                           (i, i, board_rect.width + glow_size * 2 - i * 2,
                            board_rect.height + glow_size * 2 - i * 2),
                           1, border_radius=10)
        
        screen.blit(glow_surface, 
                   (board_rect.x - glow_size, board_rect.y - glow_size))

        current_time = pygame.time.get_ticks()
        animation_progress = (current_time % self.ANIMATION_DURATION) / self.ANIMATION_DURATION

        for i, rect in enumerate(self.board_rects):
            space = self.spaces[i]
            space_data = self.properties_data.get(str(i + 1), {})
            
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            
            bgcolor = MODERN_BG
            if space_data:
                group = space_data.get("group")
                name = space_data.get("name", "")
                
                if group in GROUP_COLORS:
                    base_color = GROUP_COLORS[group]
                    if space and space.owner:
                        alpha = int(180 + 75 * abs(math.sin(2 * math.pi * animation_progress)))
                        bgcolor = (*base_color[:3], alpha)
                    else:
                        bgcolor = base_color
                elif "Station" in name:
                    bgcolor = (100, 100, 100, 180)
                elif name in ["Tesla Power Co", "Edison Water"]:
                    bgcolor = (100, 100, 0, 180)
            
            pygame.draw.rect(s, bgcolor, s.get_rect(), border_radius=5)
            screen.blit(s, rect)
            
            if space and space.owner:
                border_color = ACCENT_COLOR
                for thickness in range(2):
                    pygame.draw.rect(screen, border_color, 
                                   rect.inflate(thickness*2, thickness*2), 
                                   1, border_radius=5)
            else:
                pygame.draw.rect(screen, WHITE, rect, 1, border_radius=5)
            
            if space or space_data:
                self.draw_space_contents(screen, rect, space, space_data)

        current_time = pygame.time.get_ticks()
        y_offset = 50
        messages_to_remove = []
        
        for i, (message, time) in enumerate(zip(self.messages, self.message_times)):
            if current_time - time > self.message_duration:
                messages_to_remove.append(i)
                continue
            
            progress = (current_time - time) / self.message_duration
            alpha = max(0, 255 * (1 - progress))
            y_pos = y_offset - 20 * progress
            
            msg_surface = self.message_font.render(message, True, WHITE)
            msg_rect = msg_surface.get_rect(centerx=WINDOW_SIZE[0] // 2, top=y_pos)
            
            bg_rect = msg_rect.inflate(40, 20)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            
            for y in range(bg_rect.height):
                grad_alpha = int(alpha * (1 - y/bg_rect.height) * 0.7)
                pygame.draw.line(bg_surface, (*BLACK, grad_alpha),
                               (0, y), (bg_rect.width, y))
            
            screen.blit(bg_surface, bg_rect)
            
            msg_surface.set_alpha(int(alpha))
            screen.blit(msg_surface, msg_rect)
            
            y_offset += 40
        
        for i in reversed(messages_to_remove):
            self.messages.pop(i)
            self.message_times.pop(i)

    def draw_space_contents(self, screen, rect, space, space_data):
        name = space_data.get("name", "")
        
        available_width = rect.width - 10
        text_size = 20
        while text_size > 12:
            test_font = pygame.font.Font(None, text_size)
            if test_font.size(name)[0] <= available_width:
                break
            text_size -= 1
        
        font = pygame.font.Font(None, text_size)
        
        name_shadow = font.render(name, True, BLACK)
        name_rect_shadow = name_shadow.get_rect(centerx=rect.centerx+1, top=rect.top+6)
        screen.blit(name_shadow, name_rect_shadow)
        
        name_text = font.render(name, True, WHITE)
        name_rect = name_text.get_rect(centerx=rect.centerx, top=rect.top+5)
        screen.blit(name_text, name_rect)
        
        if space and hasattr(space, 'price'):
            price_font = pygame.font.Font(None, 16)
            price_text = price_font.render(f"£{space.price}", True, WHITE)
            price_rect = price_text.get_rect(centerx=rect.centerx, top=name_rect.bottom+2)
            screen.blit(price_text, price_rect)
            
            if space.is_station:
                rent_text = price_font.render("£25-£200", True, WHITE)
            elif space.is_utility:
                rent_text = price_font.render("4x/10x", True, WHITE)
            else:
                rent_text = price_font.render(f"Rent: £{space.rent}", True, WHITE)
            rent_rect = rent_text.get_rect(centerx=rect.centerx, top=price_rect.bottom+2)
            screen.blit(rent_text, rent_rect)
            
            if space.owner:
                owner_text = price_font.render(f"👤 {space.owner}", True, WHITE)
                owner_rect = owner_text.get_rect(centerx=rect.centerx, bottom=rect.bottom-2)
                screen.blit(owner_text, owner_rect)
        
        elif "action" in space_data or name in ["Chance", "Community Chest", "Income Tax", "Luxury Tax", "Go to Jail"]:
            action_font = pygame.font.Font(None, 14)
            display_text = space_data.get("action", "")
            if name == "Go to Jail":
                display_text = "Go to Jail!"
            elif name in ["Pot Luck", "Opportunity Knocks"]:
                display_text = "Draw a Card"
            elif name == "Income Tax":
                display_text = "Pay £200"
            elif name == "Super Tax":
                display_text = "Pay £100"
            
            action_text = action_font.render(display_text, True, WHITE)
            action_rect = action_text.get_rect(centerx=rect.centerx, bottom=rect.bottom-5)
            screen.blit(action_text, action_rect)

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