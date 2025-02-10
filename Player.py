# player that show on the board
# will be a huge change once we have our gui player photo

import pygame
import math
## we are not submitting with the color box as player
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ACCENT_COLOR = (75, 139, 190)

class Player:
    def __init__(self, name, money=1500, color=BLUE):
        self.name = name
        self.money = money
        self.position = 1  
        self.properties = []
        self.in_jail = False
        self.jail_turns = 0
        self.color = color
        self.rect = pygame.Rect(0, 0, 30, 30) 
        self.animation_offset = 0
        self.animation_time = 0

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

        emoji = "😎🤠🤓😊🥳"[id(self) % 5]   # will change after we have gui photo ,not submit with emoji
        font = pygame.font.Font(None, 30)
        text = font.render(emoji, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

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
