import pygame
import random
from Board import Board
from Property import Property
from typing import Optional

# Constants
WINDOW_SIZE = (800, 600)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Game:
    def __init__(self, players):
        self.players = players
        self.board = Board()
        self.turn = 0
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Property Tycoon")
        self.font = pygame.font.Font(None, 36)
        self.state = "ROLL"  # States: ROLL, BUY, END
        self.current_property: Optional[Property] = None

    def draw(self):
        self.screen.fill(BLACK)
        self.board.draw(self.screen)

        # Draw players
        for player in self.players:
            rect = self.board.board_rects[player.position].copy()
            rect.x += 5 + self.players.index(player) * 10
            rect.y += 5 + self.players.index(player) * 10
            pygame.draw.rect(self.screen, player.color, rect)

        # Draw player info
        y = 10
        for player in self.players:
            text = self.font.render(f"{player.name}: ${player.money}", True, WHITE)
            self.screen.blit(text, (10, y))
            y += 30

        # Draw state-specific information
        if self.state == "ROLL":
            text = self.font.render(f"{self.players[self.turn].name}'s turn - Click to roll dice", True, WHITE)
            self.screen.blit(text, (10, WINDOW_SIZE[1] - 40))
        elif self.state == "BUY" and self.current_property is not None:
            text = self.font.render(f"Buy {self.current_property.name}? (Y/N)", True, WHITE)
            self.screen.blit(text, (10, WINDOW_SIZE[1] - 40))

        pygame.display.flip()

    def play_turn(self):
        player = self.players[self.turn]
        
        if player.in_jail:
            # Handle jail logic
            if player.jail_turns >= 3:
                player.in_jail = False
                player.jail_turns = 0
            else:
                player.jail_turns += 1
                self.turn = (self.turn + 1) % len(self.players)
            return

        dice1, dice2 = random.randint(1, 6), random.randint(1, 6)
        steps = dice1 + dice2
        player.move(steps)
        space = self.board.get_space(player.position)

        if space and isinstance(space, Property):
            if space.owner is None:
                self.state = "BUY"
                self.current_property = space
            else:
                space.charge_rent(player)
                self.state = "ROLL"
                self.turn = (self.turn + 1) % len(self.players)
        else:
            self.state = "ROLL"
            self.turn = (self.turn + 1) % len(self.players)
