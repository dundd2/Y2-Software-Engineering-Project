import pygame
from Property import Property
from typing import Optional, List

# Constants
WINDOW_SIZE = (800, 600)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Board:
    def __init__(self):
        self.spaces: List[Optional[Property]] = [None] * 40
        self.spaces[1] = Property("Main Street", 100, 10)
        self.spaces[3] = Property("Side Street", 150, 15)
        self.spaces[5] = Property("Train Station", 200, 20)
        self.spaces[8] = Property("Shop", 120, 12)
        self.spaces[39] = Property("Mansion", 500, 50)
        self.board_rects = self._create_board_rects()

    def _create_board_rects(self):
        rects = []
        board_size = 500
        space_size = board_size // 11
        start_x = (WINDOW_SIZE[0] - board_size) // 2
        start_y = (WINDOW_SIZE[1] - board_size) // 2

        # Create board positions
        for i in range(40):
            if i < 10:  # Bottom row
                rects.append(pygame.Rect(start_x + (9-i) * space_size, start_y + board_size - space_size, space_size, space_size))
            elif i < 20:  # Left column
                rects.append(pygame.Rect(start_x, start_y + (19-i) * space_size, space_size, space_size))
            elif i < 30:  # Top row
                rects.append(pygame.Rect(start_x + (i-20) * space_size, start_y, space_size, space_size))
            else:  # Right column
                rects.append(pygame.Rect(start_x + board_size - space_size, start_y + (i-30) * space_size, space_size, space_size))
        return rects

    def draw(self, screen):
        for i, rect in enumerate(self.board_rects):
            pygame.draw.rect(screen, WHITE, rect, 2)
            space = self.spaces[i]
            if isinstance(space, Property):
                font = pygame.font.Font(None, 20)
                text = font.render(space.name, True, WHITE)
                screen.blit(text, (rect.x + 2, rect.y + 2))

    def get_space(self, position):
        return self.spaces[position]