# player that show on the board
# will be a huge change once we have our gui player photo
# Bug :13/02/2025 : photo didnt shot on the board as it should , need to be fix

import pygame
import math
import os

WHITE = (255, 255, 255)
HUMAN_COLOR = (75, 139, 190)
AI_COLOR = (190, 75, 75)

class Player:
    def __init__(self, name, money=1500, color=None, is_ai=False, player_number=1):
        self.name = name
        self.money = money
        self.position = 1  
        self.properties = []
        self.in_jail = False
        self.jail_turns = 0
        self.color = color or (AI_COLOR if is_ai else HUMAN_COLOR)
        self.rect = pygame.Rect(0, 0, 40, 40)
        self.animation_offset = 0
        self.animation_time = 0
        self.is_ai = is_ai
        self.player_number = min(max(player_number, 1), 5)
        self.player_image = None
        self.load_player_image()

    def load_player_image(self):
        try:
            current_dir = os.getcwd()
            image_path = os.path.join(current_dir, "assets", "image", f"Playerlogo ({self.player_number}).png")
            print(f"Attempting to load player image from: {image_path}")
            if os.path.exists(image_path):
                self.player_image = pygame.image.load(image_path)
                self.player_image = pygame.transform.scale(self.player_image, (40, 40))
                print(f"Successfully loaded player {self.player_number} image")
            else:
                print(f"Image file not found at {image_path}")
                self.create_fallback_token()
        except pygame.error as e:
            print(f"Could not load player image {self.player_number}: {e}")
            self.create_fallback_token()

    def create_fallback_token(self):
        self.player_image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(self.player_image, self.color, (20, 20), 20)
        player_number_font = pygame.font.Font(None, 28)
        number_text = player_number_font.render(str(self.player_number), True, WHITE)
        number_rect = number_text.get_rect(center=(20, 20))
        self.player_image.blit(number_text, number_rect)
        print(f"Created fallback token for player {self.player_number}")

    def draw(self, screen, x, y):
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
        if self.player_image:
            screen.blit(self.player_image, self.rect)

    def move(self, steps):
        self.position = ((self.position - 1 + steps) % 40) + 1
        self.animation_time = pygame.time.get_ticks()  

    def pay(self, amount):
        self.money -= amount

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
