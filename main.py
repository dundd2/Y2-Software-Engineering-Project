import pygame
import sys
from Board import Board
from Game import Game
from Player import Player
from ui import MainMenuPage, StartPage, GameModePage, EndGamePage, SettingsPage, HowToPlayPage

pygame.init()

WINDOW_SIZE = (1280, 720)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)

def apply_screen_settings(resolution):
    global WINDOW_SIZE
    WINDOW_SIZE = resolution
    return pygame.display.set_mode(WINDOW_SIZE)

def create_game(player_info, game_settings):
    total_players, player_names, ai_count = player_info
    players = []
    player_number = 1
    
    for name in player_names[:total_players-ai_count]:
        players.append(Player(name, player_number=player_number))
        player_number += 1
        
    for name in player_names[total_players-ai_count:]:
        players.append(Player(name, is_ai=True, player_number=player_number))
        player_number += 1
    
    return Game(players, game_mode=game_settings["mode"], time_limit=game_settings["time_limit"])

def run_game(game, game_settings):
    running = True
    game_over_data = None
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        game.handle_motion(mouse_pos)
        game.draw()
        
        for game_event in pygame.event.get():
            if game_event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif game_event.type == pygame.MOUSEBUTTONDOWN:
                game_over_data = game.handle_click(game_event.pos)
                if game_over_data:
                    running = False
            elif game_event.type == pygame.KEYDOWN:
                if game_event.key == pygame.K_ESCAPE and game_settings["mode"] == "full":
                    if game.logic.players:
                        current_player = game.logic.players[game.logic.current_player_index]
                        game.handle_voluntary_exit(current_player['name'])
                else:
                    game_over_data = game.handle_key(game_event)
                    if game_over_data:
                        running = False
    
    return game_over_data

def handle_end_game(game_over_data):
    end_page = EndGamePage(
        winner_name=game_over_data["winner"],
        final_assets=game_over_data.get("final_assets"),
        bankrupted_players=game_over_data.get("bankrupted_players"),
        voluntary_exits=game_over_data.get("voluntary_exits")
    )
    
    while True:
        end_page.draw()
        
        for end_event in pygame.event.get():
            if end_event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif end_event.type == pygame.MOUSEBUTTONDOWN:
                result = end_page.handle_click(end_event.pos)
                if result == "play_again":
                    return True
                elif result == "quit":
                    pygame.quit()
                    sys.exit()
            elif end_event.type == pygame.KEYDOWN:
                result = end_page.handle_key(end_event)
                if result == "play_again":
                    return True
                elif result == "quit":
                    pygame.quit()
                    sys.exit()
            elif end_event.type == pygame.MOUSEMOTION:
                end_page.handle_motion(end_event.pos)

def main():
    global WINDOW_SIZE
    while True:
        current_page = MainMenuPage()
        player_info = None
        game_settings = None
        
        game_running = True
        while game_running:
            current_page.draw()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    result = (current_page.handle_click(event.pos) if event.type == pygame.MOUSEBUTTONDOWN 
                            else current_page.handle_key(event))
                    
                    if result:
                        if isinstance(current_page, MainMenuPage):
                            if result == "start":
                                current_page = StartPage()
                            elif result == "how_to_play":
                                current_page = HowToPlayPage()
                            elif result == "settings":
                                current_page = SettingsPage()
                        elif isinstance(current_page, HowToPlayPage):
                            current_page = MainMenuPage()
                        elif isinstance(current_page, SettingsPage):
                            settings = current_page.get_settings()
                            if settings["resolution"] != WINDOW_SIZE:
                                WINDOW_SIZE = settings["resolution"]
                                apply_screen_settings(WINDOW_SIZE)
                            current_page = MainMenuPage()
                        elif isinstance(current_page, StartPage):
                            player_info = current_page.get_player_info()
                            current_page = GameModePage()
                        elif isinstance(current_page, GameModePage):
                            game_settings = current_page.get_game_settings()
                            
                            game = create_game(player_info, game_settings)
                            game_over_data = run_game(game, game_settings)
                            
                            if game_over_data:
                                play_again = handle_end_game(game_over_data)
                                if play_again:
                                    current_page = MainMenuPage()
                
                elif event.type == pygame.MOUSEMOTION:
                    current_page.handle_motion(event.pos)

if __name__ == "__main__":
    main()
