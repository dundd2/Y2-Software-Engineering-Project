import pygame
import sys
import asyncio
import os 
pygame.init()
os.chdir(os.path.dirname(os.path.abspath(__file__))) 
from Board import Board
from Game import Game
from Player import Player
from ui import MainMenuPage, StartPage, GameModePage, EndGamePage, SettingsPage, HowToPlayPage, AIDifficultyPage
from text_scaler import text_scaler

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

GAME_INSTRUCTIONS = [
    "Use WASD or Arrow keys to move",
    "Press + or - to zoom",
    "Press ESC to exit game",
    "Use mouse to click buttons"
]

async def apply_screen_settings(resolution):
    global WINDOW_SIZE
    WINDOW_SIZE = resolution
    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
    text_scaler.update_scale_factor(resolution[0], resolution[1])
    
    if pygame.display.get_surface():
        current_w, current_h = pygame.display.get_surface().get_size()
        if current_w != resolution[0] or current_h != resolution[1]:
            screen = pygame.display.set_mode(resolution, pygame.RESIZABLE)
            pygame.display.flip()
    
    return screen

def create_game(player_info, game_settings):
    if not player_info or not game_settings:
        raise ValueError("Missing player info or game settings")
        
    total_players, player_names, ai_count = player_info
    if not isinstance(total_players, int) or not isinstance(ai_count, int):
        raise ValueError("Invalid player counts")
        
    players = []
    player_number = 1
    
    for name in player_names[:total_players-ai_count]:
        if not name.strip():
            continue
        players.append(Player(name, player_number=player_number))
        player_number += 1
        
    for name in player_names[total_players-ai_count:]:
        if not name.strip():
            continue
        players.append(Player(name, is_ai=True, player_number=player_number))
        player_number += 1
    
    if not players:
        raise ValueError("No valid players created")
        
    return Game(players, 
               game_mode=game_settings.get("mode", "full"),
               time_limit=game_settings.get("time_limit"))

async def run_game(game, game_settings):
    running = True
    game_over_data = None
    
    while running:
        await asyncio.sleep(0)
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
            elif game_event.type == pygame.VIDEORESIZE:
                await apply_screen_settings((game_event.w, game_event.h))
            elif game_event.type == pygame.MOUSEMOTION:
                game.handle_motion(game_event.pos)
    
    return game_over_data

async def handle_end_game(game_over_data):
    end_page = EndGamePage(
        winner_name=game_over_data["winner"],
        final_assets=game_over_data.get("final_assets"),
        bankrupted_players=game_over_data.get("bankrupted_players"),
        voluntary_exits=game_over_data.get("voluntary_exits")
    )
    
    while True:
        await asyncio.sleep(0)
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

async def main():
    global WINDOW_SIZE
    text_scaler.update_scale_factor(WINDOW_SIZE[0], WINDOW_SIZE[1])
    screen = await apply_screen_settings(WINDOW_SIZE)
    
    while True:
        await asyncio.sleep(0)
        current_page = MainMenuPage(instructions=GAME_INSTRUCTIONS)
        player_info = None
        game_settings = None
        ai_difficulty = None
        
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
                                current_page = StartPage(instructions=GAME_INSTRUCTIONS)
                            elif result == "how_to_play":
                                current_page = HowToPlayPage(instructions=GAME_INSTRUCTIONS)
                            elif result == "settings":
                                current_page = SettingsPage(instructions=GAME_INSTRUCTIONS)
                        elif isinstance(current_page, HowToPlayPage):
                            current_page = MainMenuPage(instructions=GAME_INSTRUCTIONS)
                        elif isinstance(current_page, SettingsPage):
                            settings = current_page.get_settings()
                            if settings["resolution"] != WINDOW_SIZE:
                                screen = await apply_screen_settings(settings["resolution"])
                            current_page = MainMenuPage(instructions=GAME_INSTRUCTIONS)
                        elif isinstance(current_page, StartPage):
                            if result == "back":
                                current_page = MainMenuPage(instructions=GAME_INSTRUCTIONS)
                            else:
                                player_info = current_page.get_player_info()
                                if player_info[2] > 0:
                                    current_page = AIDifficultyPage(instructions=GAME_INSTRUCTIONS)
                                else:
                                    current_page = GameModePage(instructions=GAME_INSTRUCTIONS)
                        elif isinstance(current_page, AIDifficultyPage):
                            if result == "back":
                                current_page = StartPage(instructions=GAME_INSTRUCTIONS)
                            else:
                                ai_difficulty = result
                                current_page = GameModePage(instructions=GAME_INSTRUCTIONS)
                        elif isinstance(current_page, GameModePage):
                            if result == "back":
                                if ai_difficulty:
                                    current_page = AIDifficultyPage(instructions=GAME_INSTRUCTIONS)
                                else:
                                    current_page = StartPage(instructions=GAME_INSTRUCTIONS)
                            else:
                                game_settings = current_page.get_game_settings()
                                if ai_difficulty:
                                    game_settings["ai_difficulty"] = ai_difficulty
                                
                                game = create_game(player_info, game_settings)
                                game_over_data = await run_game(game, game_settings)
                                
                                if game_over_data:
                                    play_again = await handle_end_game(game_over_data)
                                    if play_again:
                                        current_page = MainMenuPage(instructions=GAME_INSTRUCTIONS)
                
                elif event.type == pygame.MOUSEMOTION:
                    current_page.handle_motion(event.pos)
                elif event.type == pygame.VIDEORESIZE:
                    screen = await apply_screen_settings((event.w, event.h))
            
            pygame.display.flip()

if __name__ == "__main__":
    asyncio.run(main())
