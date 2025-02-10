import pygame
import sys
from Board import Board
from Game import Game
from Player import Player
from ui import StartPage

pygame.init()

WINDOW_SIZE = (800, 600)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)

def main():
    # start with start page
    start_page = StartPage()
    game_started = False
    
    # show start page until game starts
    while not game_started:
        start_page.draw()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game_started = start_page.handle_click(event.pos)
            elif event.type == pygame.MOUSEMOTION:
                start_page.handle_motion(event.pos)
            elif event.type == pygame.KEYDOWN:
                game_started = start_page.handle_key(event)
    
    # get player information
    num_players, player_names = start_page.get_player_info()
    
    # initialize players
    players = []
    for i in range(num_players):
        players.append(Player(player_names[i]))
    
    game = Game(players)
    
    # main game loop
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        game.handle_motion(mouse_pos)
        
        game.draw()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game_over = game.handle_click(event.pos)
                if game_over:
                    running = False
            elif event.type == pygame.KEYDOWN:
                game_over = game.handle_key(event)
                if game_over:
                    running = False

    pygame.quit()
    sys.exit()

def handle_click(self, pos):
    """Handle mouse clicks"""
    if self.state == "ROLL":
        if self.roll_button.collidepoint(pos):
            return self.play_turn()
    elif self.state == "BUY":
        if self.yes_button.collidepoint(pos):
            self.handle_buy_decision(True)
            return False
        elif self.no_button.collidepoint(pos):
            self.handle_buy_decision(False)
            return False
    return False

if __name__ == "__main__":
    main()
