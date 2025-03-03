import pygame
import math
import os
from src.text_scaler import text_scaler

WHITE = (255, 255, 255)
HUMAN_COLOR = (75, 139, 190)
AI_COLOR = (190, 75, 75)

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Player:
    def __init__(self, name, player_number=1, is_ai=False):
        self.name = name
        self.player_number = player_number
        self.is_ai = is_ai
        self.money = 0
        self.properties = []
        self.position = 1
        self.in_jail = False
        self.jail_turns = 0
        self.jail_cards = 0
        self.bankrupt = False
        self.voluntary_exit = False
        self.final_assets = 0
        self.color = AI_COLOR if is_ai else HUMAN_COLOR
        self.rect = pygame.Rect(0, 0, 40, 40)
        self.animation_offset = 0
        self.animation_time = 0
        self.highlight_intensity = 0
        self.is_active = False
        self.is_winner = False
        self.bounce_offset = 0
        self.bounce_speed = 0.15
        self.glow_alpha = 0
        self.target_animation_offset = 0
        
        self.is_moving = False
        self.move_start_position = 1
        self.move_target_position = 1
        self.move_progress = 0.0
        self.move_speed = 0.1
        self.move_path = []
        self.current_path_index = 0
        
        self.load_player_image()
        print(f"Player {name} initial position: {self.position}")

    def load_player_image(self):
        try:
            image_path = os.path.join(base_path, "assets", "image", f"Playerlogo ({self.player_number}).png")
            print(f"Attempting to load player image from: {image_path}")
            
            if os.path.exists(image_path):
                self.player_image = pygame.image.load(image_path)
                self.player_image = pygame.transform.scale(self.player_image, (40, 40))
                print(f"Successfully loaded player {self.player_number} image")
            else:
                print(f"Image file not found at {image_path}, trying absolute path...")
                current_dir = os.getcwd()
                abs_path = os.path.join(current_dir, "assets", "image", f"Playerlogo ({self.player_number}).png")
                if os.path.exists(abs_path):
                    self.player_image = pygame.image.load(abs_path)
                    self.player_image = pygame.transform.scale(self.player_image, (40, 40))
                    print(f"Successfully loaded player {self.player_number} image from absolute path")
                else:
                    print(f"Image file not found at {abs_path}")
                    self.create_fallback_token()
        except pygame.error as e:
            print(f"Could not load player image {self.player_number}: {e}")
            self.create_fallback_token()

    def create_fallback_token(self):
        self.player_image = pygame.Surface((40, 40), pygame.SRCALPHA)
        
        token_color = (*self.color[:3], 230)
        highlight_color = tuple(min(c + 40, 255) for c in self.color[:3])
        
        pygame.draw.circle(self.player_image, token_color, (20, 20), 20)
        for i in range(10):
            alpha = int(100 * (1 - i/10))
            pygame.draw.circle(self.player_image, (*highlight_color, alpha), (15, 15), 20-i)
            
        number_font = pygame.font.Font('assets/font/Play-Regular.ttf', text_scaler.get_scaled_size(28))
        number_text = number_font.render(str(self.player_number), True, WHITE)
        number_rect = number_text.get_rect(center=(20, 20))
        
        shadow_text = number_font.render(str(self.player_number), True, (0, 0, 0))
        shadow_rect = number_rect.copy()
        shadow_rect.x += 1
        shadow_rect.y += 1
        self.player_image.blit(shadow_text, shadow_rect)
        self.player_image.blit(number_text, number_rect)
        
        print(f"Created enhanced fallback token for player {self.player_number}")

    def update_animation(self):
        current_time = pygame.time.get_ticks()
        
        if self.is_active:
            self.target_animation_offset = 5
            self.highlight_intensity = min(self.highlight_intensity + 0.1, 1.0)
        else:
            self.target_animation_offset = 0
            self.highlight_intensity = max(self.highlight_intensity - 0.1, 0.0)
            
        self.animation_offset += (self.target_animation_offset - self.animation_offset) * 0.2
        
        if self.is_winner:
            self.bounce_offset = math.sin(current_time * self.bounce_speed) * 8
            self.glow_alpha = abs(math.sin(current_time * 0.003)) * 255
        else:
            self.bounce_offset = 0
            self.glow_alpha = 0
            
        if self.is_moving:
            if self.current_path_index < len(self.move_path):
                self.move_progress += self.move_speed
                
                if self.move_progress > 1.0:
                    next_position = self.move_path[self.current_path_index]
                    if 1 <= next_position <= 40:
                        self.position = next_position
                        print(f"Animation step: {self.name} now at position {self.position}")
                    else:
                        print(f"Warning: Invalid position {next_position} detected for {self.name}, resetting to position 1")
                        self.position = 1
                    self.current_path_index += 1
                    
                    if self.current_path_index >= len(self.move_path):
                        self.is_moving = False
                        if 1 <= self.move_target_position <= 40:
                            self.position = self.move_target_position
                            print(f"Player {self.name} finished moving to position {self.position}")
                        else:
                            print(f"Warning: Invalid target position {self.move_target_position} detected for {self.name}, resetting to position 1")
                            self.position = 1
            else:
                self.is_moving = False
                if 1 <= self.move_target_position <= 40:
                    self.position = self.move_target_position
                    print(f"Player {self.name} finished moving to position {self.position}")
                else:
                    print(f"Warning: Invalid target position {self.move_target_position} detected for {self.name}, resetting to position 1")
                    self.position = 1

    def get_total_offset(self):
        return self.animation_offset + self.bounce_offset

    def set_active(self, active):
        self.is_active = active

    def set_winner(self, winner):
        self.is_winner = winner

    def draw_player(self, screen, x, y):
        if not (1 <= self.position <= 40):
            print(f"Warning: Invalid position {self.position} detected in draw_player for {self.name}, resetting to position 1")
            self.position = 1
            
        print(f"Drawing player {self.name} at screen coordinates: ({x}, {y})")
        current_time = pygame.time.get_ticks()
        self.animation_offset = abs(math.sin(current_time * 0.003)) * 5
        self.rect.x = x
        self.rect.y = y - self.animation_offset
        
        glow_surface = pygame.Surface((self.rect.width + 8, self.rect.height + 8), pygame.SRCALPHA)
        for i in range(4):
            alpha = int(100 * (1 - i/4))
            pygame.draw.circle(glow_surface, (*self.color[:3], alpha),
                            (self.rect.width//2 + 4, self.rect.height//2 + 4),
                            self.rect.width//2 - i)
        screen.blit(glow_surface, (self.rect.x - 4, self.rect.y - 4))
        
        if hasattr(self, 'player_image') and self.player_image is not None:
            print(f"Drawing player {self.player_number} image at position: ({self.rect.x}, {self.rect.y})")
            screen.blit(self.player_image, self.rect)
        else:
            print(f"No image for player {self.player_number}, creating fallback")
            self.create_fallback_token()
            screen.blit(self.player_image, self.rect)

    def move(self, steps):
        if self.is_moving:
            return
        
        if not (1 <= self.position <= 40):
            print(f"Warning: Invalid position {self.position} detected for {self.name} before move, resetting to position 1")
            self.position = 1
            
        if not isinstance(steps, int) or steps < 0 or steps > 40:
            print(f"Warning: Invalid steps value {steps} for {self.name}, adjusting to valid range")
            steps = max(0, min(steps, 40))
            
        self.move_start_position = self.position
        new_position = ((self.position - 1 + steps) % 40) + 1
        
        print(f"Player.move: {self.name} from {self.position} to {new_position} ({steps} steps)")
        
        if 1 <= new_position <= 40:
            self.move_target_position = new_position
            self.generate_move_path(steps)
            self.is_moving = True
            self.move_progress = 0.0
            self.current_path_index = 0
            self.animation_time = pygame.time.get_ticks()
        else:
            print(f"Error: Invalid move resulting in position {new_position} for player {self.name}, resetting to position 1")
            self.position = 1
            self.move_target_position = 1
    
    def generate_move_path(self, steps):
        self.move_path = []
        
        if not isinstance(steps, int) or steps < 0 or steps > 40:
            print(f"Warning: Invalid steps value {steps} for {self.name} in generate_move_path, adjusting to valid range")
            steps = max(0, min(steps, 40))
            
        if not (1 <= self.position <= 40):
            print(f"Warning: Invalid position {self.position} detected in generate_move_path for {self.name}, resetting to position 1")
            self.position = 1
            
        current_pos = self.position
        
        for i in range(steps):
            next_pos = ((current_pos + 1 - 1) % 40) + 1
            if not (1 <= next_pos <= 40):
                print(f"Warning: Invalid position {next_pos} calculated in path generation for {self.name}, resetting to position 1")
                next_pos = 1
            self.move_path.append(next_pos)
            current_pos = next_pos
        
        print(f"Generated move path for {self.name}: {self.move_path}")
    
    def is_animation_complete(self):
        return not self.is_moving

    def pay(self, amount):
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    def receive(self, amount):
        self.money += amount

    def buy_property(self, property):
        if self.money >= property.price:
            self.money -= property.price
            self.properties.append(property)
            property.owner = self
            print(f"{self.name} bought {property.name}!")
            return True
        else:
            print(f"{self.name} doesn't have enough money to buy {property.name}!")
            return False

    def add_jail_card(self, card_type):
        self.jail_cards.append(card_type)

    def use_jail_card(self):
        if self.jail_cards:
            card_type = self.jail_cards.pop()
            self.in_jail = False
            self.jail_turns = 0
            return card_type
        return None

    def handle_jail_turn(self):
        if not self.in_jail:
            return False

        if self.is_ai:
            import random
            if self.jail_cards and random.random() < 0.7: 
                return self.use_jail_card()
            elif self.money >= 50 and random.random() < 0.5: 
                self.pay(50)
                self.in_jail = False
                self.jail_turns = 0
                return None
        
        self.jail_turns += 1
        if self.jail_turns >= 3:
            if self.money >= 50:
                self.pay(50)
            self.in_jail = False
            self.jail_turns = 0
        
        return None

    def can_afford(self, amount):
        return self.money >= amount

    def add_property(self, property):
        if property not in self.properties:
            self.properties.append(property)
            property.owner = self
            
    def remove_property(self, property):
        if property in self.properties:
            self.properties.remove(property)
            property.owner = None
            
    def get_total_assets(self):
        total = self.money
        
        for prop in self.properties:
            if not prop.mortgaged:
                total += prop.price
            
            if prop.houses > 0:
                total += prop.get_house_sale_value() * prop.houses
            
            if prop.has_hotel:
                total += prop.get_hotel_sale_value()
        
        return total
        
    def get_mortgageable_properties(self):
        return [p for p in self.properties if not p.mortgaged and p.houses == 0 and not p.has_hotel]
        
    def get_unmortgageable_properties(self):
        return [p for p in self.properties if p.mortgaged]
        
    def get_properties_with_houses(self):
        return [p for p in self.properties if p.houses > 0]
        
    def get_properties_with_hotels(self):
        return [p for p in self.properties if p.has_hotel]
        
    def can_build_houses(self):
        return any(p.can_build_house(self.properties) for p in self.properties)
        
    def can_build_hotels(self):
        return any(p.can_build_hotel(self.properties) for p in self.properties)
        
    def handle_bankruptcy(self, creditor=None):
        self.bankrupt = True
        
        for prop in self.properties[:]:
            if creditor:
                self.remove_property(prop)
                creditor.add_property(prop)
                if prop.mortgaged:
                    unmortgage_cost = prop.get_unmortgage_cost() - prop.get_mortgage_value()
                    if creditor.can_afford(unmortgage_cost):
                        creditor.pay(unmortgage_cost)
                        prop.unmortgage()
            else:
                self.remove_property(prop)
                prop.mortgaged = False
                prop.houses = 0
                prop.has_hotel = False
        
        if creditor and self.money > 0:
            creditor.receive(self.money)
        self.money = 0
        
    def handle_voluntary_exit(self):
        self.voluntary_exit = True
        self.final_assets = self.get_total_assets()
        self.handle_bankruptcy()