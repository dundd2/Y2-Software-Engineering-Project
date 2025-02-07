import pygame

# Constants
BLUE = (0, 0, 255)

class Player:
    def __init__(self, name, money=1500, color=BLUE):
        self.name = name
        self.money = money
        self.position = 0
        self.properties = []
        self.in_jail = False
        self.jail_turns = 0
        self.color = color
        self.rect = pygame.Rect(0, 0, 20, 20)

    def move(self, steps):
        self.position = (self.position + steps) % 40

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
        else:
            print(f"{self.name} doesn't have enough money to buy {property.name}!")
