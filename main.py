import random
import pygame
import sys
from Board import Board
from Game import Game
from Player import Player
from Property import Property
from ui import StartPage

# Initialize Pygame
pygame.init()

# Constants
WINDOW_SIZE = (800, 600)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

def main():
    # Start with the start page
    start_page = StartPage()
    game_started = False
    
    # Show start page until game starts
    while not game_started:
        start_page.draw()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_page.handle_click(event.pos):
                    game_started = True
    
    # Initialize game after start button is clicked
    player_count = 2  # For simplicity, start with 2 players
    players = [
        Player("Player 1", color=BLUE),
        Player("Player 2", color=RED)
    ]
    game = Game(players)
    
    # Main game loop
    while True:
        game.draw()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.state == "ROLL":
                    game.play_turn()
                
            if event.type == pygame.KEYDOWN:
                if game.state == "BUY":
                    if event.key == pygame.K_y:
                        game.players[game.turn].buy_property(game.current_property)
                        game.state = "ROLL"
                        game.turn = (game.turn + 1) % len(game.players)
                    elif event.key == pygame.K_n:
                        game.state = "ROLL"
                        game.turn = (game.turn + 1) % len(game.players)

        if any(player.money <= 0 for player in game.players):
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    main()
