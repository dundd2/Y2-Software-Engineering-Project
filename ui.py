import pygame

# Constants
WINDOW_SIZE = (800, 600)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)

class StartPage:
    def __init__(self):
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Property Tycoon")
        self.title_font = pygame.font.Font(None, 72)
        self.button_font = pygame.font.Font(None, 36)
        self.version_font = pygame.font.Font(None, 24)
        
        # Create button rectangle
        button_width = 200
        button_height = 50
        self.button_rect = pygame.Rect(
            (WINDOW_SIZE[0] - button_width) // 2,
            (WINDOW_SIZE[1] - button_height) // 2,
            button_width,
            button_height
        )
        
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw title
        title_text = self.title_font.render("Property Tycoon", True, WHITE)
        title_rect = title_text.get_rect(centerx=WINDOW_SIZE[0]//2, y=100)
        self.screen.blit(title_text, title_rect)
        
        # Draw start button
        pygame.draw.rect(self.screen, WHITE, self.button_rect, 2)
        start_text = self.button_font.render("Start Game", True, WHITE)
        text_rect = start_text.get_rect(center=self.button_rect.center)
        self.screen.blit(start_text, text_rect)
        
        # Draw version
        version_text = self.version_font.render("Build Version: 07.02.2025", True, GRAY)
        version_rect = version_text.get_rect(right=WINDOW_SIZE[0]-10, bottom=WINDOW_SIZE[1]-10)
        self.screen.blit(version_text, version_rect)
        
        pygame.display.flip()
    
    def handle_click(self, pos):
        return self.button_rect.collidepoint(pos)