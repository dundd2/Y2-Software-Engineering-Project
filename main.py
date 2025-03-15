# Property Tycoon main.py
# Created for Year 2 G6046: Software Engineering Project-Group 5
# -*- coding: utf-8 -*-

import pygame
import sys
import asyncio
import os 
import random

pygame.init()
os.chdir(os.path.dirname(os.path.abspath(__file__))) 

from src.Board import Board
from src.Game import Game
from src.Player import Player
from src.ui import MainMenuPage, StartPage, GameModePage, EndGamePage, SettingsPage, HowToPlayPage, AIDifficultyPage, CreditsPage
from src.text_scaler import text_scaler
from src.FontManager import FontManager 

WINDOW_SIZE = (1280, 720)  
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)

STARTING_BANK_MONEY = 50000
STARTING_PLAYER_MONEY = 1500
JAIL_FINE = 50
PASSING_GO_AMOUNT = 200
HOTEL_VALUE_IN_HOUSES = 5  # A hotel is worth 5 houses
HOTEL_REPLACES_HOUSES = True  # When building a hotel, houses are returned to bank

FPS = 20

GAME_INSTRUCTIONS = [
    "Use WASD or Arrow keys to move",
    "Press + or - to zoom",
    "Press ESC to exit game",
    "Use mouse to click buttons",
    "Buy properties when landing on them",
    "You must complete one lap around the board before buying properties",
    "Build houses/hotels on owned property sets",
    "Pay rent when landing on others' properties",
    "Collect £200 when passing GO"
]

async def apply_screen_settings(resolution):
    global WINDOW_SIZE
    WINDOW_SIZE = resolution
    screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
    
    pygame.display.set_caption("Property Tycoon Build 14.03.2025")
    try:
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "image", "icon.ico")
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)
    except (pygame.error, FileNotFoundError) as e:
        print(f"Could not load game icon: {e}")
    
    text_scaler.update_scale_factor(resolution[0], resolution[1])
    FontManager.update_scale_factor(resolution[0], resolution[1])  
    
    if pygame.display.get_surface():
        current_w, current_h = pygame.display.get_surface().get_size()
        if current_w != resolution[0] or current_h != resolution[1]:
            screen = pygame.display.set_mode(resolution, pygame.RESIZABLE)
            pygame.display.flip()
    
    return screen

def create_game(player_info, game_settings):
    if not player_info or not game_settings:
        raise ValueError("Missing player info or game settings")
        
    total_players, player_names, ai_count, token_indices = player_info
    if not isinstance(total_players, int) or not isinstance(ai_count, int):
        raise ValueError("Invalid player counts")
        
    players = []
    player_number = 1
    
    bank_money = STARTING_BANK_MONEY
    
    for i, name in enumerate(player_names[:total_players-ai_count]):
        if not name.strip():
            continue
        token_index = token_indices[i] + 1  
        player = Player(name, player_number=token_index)
        player.money = STARTING_PLAYER_MONEY
        bank_money -= STARTING_PLAYER_MONEY
        players.append(player)
        player_number += 1
        
    for i, name in enumerate(player_names[total_players-ai_count:]):
        if not name.strip():
            continue
        token_index = token_indices[total_players-ai_count+i] + 1  
        player = Player(name, is_ai=True, player_number=token_index, 
                       ai_difficulty=game_settings.get("ai_difficulty", "easy"))
        player.money = STARTING_PLAYER_MONEY
        bank_money -= STARTING_PLAYER_MONEY
        players.append(player)
        player_number += 1
    
    if not players:
        raise ValueError("No valid players created")
        
    game = Game(players, 
               game_mode=game_settings.get("mode", "full"),
               time_limit=game_settings.get("time_limit"),
               ai_difficulty=game_settings.get("ai_difficulty", "easy"))
    
    game.bank_money = bank_money
    game.free_parking_pot = 0
    
    return game

async def run_game(game, game_settings):
    running = True
    game_over_data = None
    last_time_check = pygame.time.get_ticks()
    last_ai_progress_time = pygame.time.get_ticks()
    ai_timeout_duration = 10000 
    
    clock = pygame.time.Clock()
    
    while running:
        await asyncio.sleep(0)
        
        current_time = pygame.time.get_ticks()
        
        if game_settings["mode"] == "abridged" and current_time - last_time_check > 1000 and not game.game_paused:
            last_time_check = current_time
            if game.check_time_limit():
                print("Time limit reached and all players completed same number of laps - ending game")
                game_over_data = game.end_abridged_game()
                running = False
                continue  
        
        if game.current_player_is_ai and not game.game_paused:
            if current_time - last_ai_progress_time > ai_timeout_duration:
                print(f"AI player turn timeout reached after {ai_timeout_duration/1000} seconds")
                
                if game.logic.players and len(game.logic.players) > 0:
                    current_player = game.logic.players[game.logic.current_player_index]
                    print(f"Forcing AI player {current_player['name']} to skip their turn due to timeout")
                    
                    if game.state == "DEVELOPMENT":
                        game.state = "ROLL"
                        game.selected_property = None
                        game.development_mode = False
                        print("Closing stuck development UI due to timeout")
                    
                    game.logic.current_player_index = (game.logic.current_player_index + 1) % len(game.logic.players)
                    
                    game.state = "ROLL"
                    game.current_player_is_ai = False
                    
                    game.check_and_trigger_ai_turn()
                    
                last_ai_progress_time = current_time
        
        if not game.current_player_is_ai:
            last_ai_progress_time = current_time
        
        game.draw()
        
        if hasattr(game, 'waiting_for_animation') and game.waiting_for_animation:
            any_moving = any(player.is_moving for player in game.players)
            if not any_moving:
                game.waiting_for_animation = False
            else:
                pygame.display.flip()
                continue
        
        for game_event in pygame.event.get():
            if game_event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif game_event.type == pygame.MOUSEBUTTONDOWN:
                any_moving = any(player.is_moving for player in game.players)
                if any_moving and game.state == "AUCTION":
                    print("Animations in progress during AUCTION state - delaying click processing")
                    pygame.display.flip()
                    continue
                
                game_over_data = game.handle_click(game_event.pos)
                if game_over_data:
                    running = False
            elif game_event.type == pygame.KEYDOWN:
                print(f"Key pressed: {pygame.key.name(game_event.key)}")
                
                if game_event.key == pygame.K_ESCAPE:
                    running = False
                    return None
                    
                if game.state == "AUCTION":
                    print("Handling auction key input in main loop")
                    game.handle_auction_input(game_event)
                else:
                    game_over_data = game.handle_key(game_event)
                    if game_over_data:
                        running = False
            elif game_event.type == pygame.VIDEORESIZE:
                await apply_screen_settings((game_event.w, game_event.h))
            elif game_event.type == pygame.MOUSEMOTION:
                game.handle_motion(game_event.pos)
        
        current_time = pygame.time.get_ticks()
        if hasattr(game, 'last_debug_time') and current_time - game.last_debug_time < 1000:
            pass
        else:
            if hasattr(game, 'state'):
                print(f"Current game state: {game.state}")
                game.last_debug_time = current_time
                
                if game.state == "AUCTION" and hasattr(game.logic, 'current_auction'):
                    auction_data = game.logic.current_auction
                    if auction_data is not None:
                        print(f"\n=== Auction State Debug ===")
                        print(f"Property: {auction_data['property']['name']}")
                        print(f"Current bid: £{auction_data['current_bid']}")
                        print(f"Minimum bid: £{auction_data['minimum_bid']}")
                        
                        if auction_data["highest_bidder"]:
                            print(f"Highest bidder: {auction_data['highest_bidder']['name']}")
                        else:
                            print("No bids yet")
                            
                        print(f"Current bidder index: {auction_data['current_bidder_index']}")
                        if auction_data["active_players"]:
                            current_bidder = auction_data["active_players"][auction_data["current_bidder_index"]]
                            print(f"Current bidder: {current_bidder['name']}")
                            
                        print(f"Passed players: {auction_data.get('passed_players', set())}")
                        print(f"Active players: {[p['name'] for p in auction_data.get('active_players', [])]}")
                        print(f"Completed: {auction_data.get('completed', False)}")
                    else:
                        print("\n=== Auction State Debug ===")
                        print("No auction data available")
        
        if hasattr(game.logic, 'current_auction') and game.logic.current_auction and not game.logic.current_auction.get("completed", False):
            if game.state != "AUCTION":
                print("Auction in progress but state is not AUCTION - correcting state")
                game.state = "AUCTION"
                
        if game.state == "ROLL" and game.logic.players and not any(player.is_moving for player in game.players):
            current_player = game.logic.players[game.logic.current_player_index]
            
            ai_player = None
            for player in game.players:
                if player.name == current_player['name']:
                    ai_player = player
                    break
                    
            if ai_player and ai_player.is_ai:
                if not isinstance(ai_player.position, int) or not (1 <= ai_player.position <= 40):
                    print(f"Warning: Invalid position {ai_player.position} detected for AI {ai_player.name}, resetting to position 1")
                    ai_player.position = 1
                    current_player['position'] = 1
                    
                game_over_data = game.handle_ai_turn(current_player)
                if game_over_data:
                    running = False
        
        if game.state == "AUCTION" and hasattr(game.logic, 'current_auction') and not any(player.is_moving for player in game.players):
            auction_data = game.logic.current_auction
            
            if auction_data is not None and not auction_data.get("completed", False) and auction_data.get("active_players") and not hasattr(game, 'auction_processing'):
                game.auction_processing = True
                current_bidder_index = auction_data["current_bidder_index"]
                
                if current_bidder_index < len(auction_data["active_players"]):
                    current_bidder = auction_data["active_players"][current_bidder_index]
                    
                    bidder_obj = None
                    for player in game.players:
                        if player.name == current_bidder['name']:
                            bidder_obj = player
                            break
                    
                    if bidder_obj and bidder_obj.is_ai and current_bidder['name'] not in auction_data.get("passed_players", set()):
                        print(f"\n=== AI Auction Turn in Main Loop ===")
                        print(f"AI Player: {current_bidder['name']}")
                        print(f"Current bid: £{auction_data['current_bid']}")
                        print(f"Minimum bid: £{auction_data['minimum_bid']}")
                        print(f"AI money: £{current_bidder['money']}")
                        
                        ai_decision = random.random() > 0.5
                        if ai_decision and current_bidder['money'] >= auction_data['minimum_bid']:
                            bid_amount = min(
                                current_bidder['money'], 
                                auction_data['minimum_bid'] + random.randint(10, 50)
                            )
                            print(f"AI {current_bidder['name']} bids £{bid_amount}")
                            success, message = game.logic.process_auction_bid(current_bidder, bid_amount)
                            game.board.add_message(message)
                        else:
                            print(f"AI {current_bidder['name']} passes")
                            success, message = game.logic.process_auction_pass(current_bidder)
                            game.board.add_message(message)
                
                if hasattr(game.logic, 'current_auction') and game.logic.current_auction:
                    result_message = game.logic.check_auction_end()
                    if result_message == "auction_completed":
                        print("Auction completed in main loop - setting up delay")
                        
                        if hasattr(game.logic, 'current_auction') and game.logic.current_auction is not None:
                            if game.logic.current_auction.get("highest_bidder"):
                                winner = game.logic.current_auction["highest_bidder"]
                                property_name = game.logic.current_auction["property"]["name"]
                                bid_amount = game.logic.current_auction["current_bid"]
                                game.show_notification(f"{winner['name']} won {property_name} for £{bid_amount}", 3000)
                            else:
                                property_name = game.logic.current_auction["property"]["name"]
                                game.show_notification(f"No one bid on {property_name}", 3000)
                        
                        game.auction_end_time = pygame.time.get_ticks()
                        game.auction_end_delay = 3000
                        game.auction_completed = True
                        game.board.update_ownership(game.logic.properties)
                
                delattr(game, 'auction_processing')
        
        any_moving = any(player.is_moving for player in game.players)
        if not any_moving and game.state == "AUCTION" and hasattr(game.logic, 'current_auction') and game.logic.current_auction and game.logic.current_auction.get("completed", False):
            print("Auction marked as completed but state not updated - forcing state to ROLL")
            game.state = "ROLL"
            game.board.update_ownership(game.logic.properties)
        
        if not any_moving and game.state == "AUCTION" and (not hasattr(game.logic, 'current_auction') or game.logic.current_auction is None):
            print("State is AUCTION but no auction data exists - resetting to ROLL")
            game.state = "ROLL"
        
        if game_settings["mode"] == "full" and game.check_one_player_remains() and not game_over_data:
            print("Only one player remains - ending game")
            game_over_data = game.end_full_game()
            running = False
        
        elif game_settings["mode"] == "abridged" and game.check_one_player_remains() and not game_over_data:
            print("Only one player remains in abridged mode - ending game")
            game_over_data = game.end_abridged_game()
            running = False
    
        pygame.display.flip()
        
        clock.tick(FPS)
    
    return game_over_data

async def handle_end_game(game_over_data):
    print("Entering handle_end_game function")
    print(f"Game over data: {game_over_data}")
    
    pygame.display.flip()
    
    clock = pygame.time.Clock()
    
    end_page = EndGamePage(
        winner_name=game_over_data["winner"],
        final_assets=game_over_data.get("final_assets", {}),
        bankrupted_players=game_over_data.get("bankrupted_players", []),
        voluntary_exits=game_over_data.get("voluntary_exits", []),
        tied_winners=game_over_data.get("tied_winners", []),
        lap_count=game_over_data.get("lap_count", {})
    )
    
    print("EndGamePage created successfully")
    
    debug_drawn = False
    current_page = end_page
    
    while True:
        await asyncio.sleep(0)
        current_page.draw()
        pygame.display.flip()
        
        clock.tick(FPS)
        
        if not debug_drawn and isinstance(current_page, EndGamePage):
            print("EndGamePage drawn")
            debug_drawn = True
        
        for end_event in pygame.event.get():
            if end_event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif end_event.type == pygame.MOUSEBUTTONDOWN:
                result = current_page.handle_click(end_event.pos)
                
                if isinstance(current_page, EndGamePage):
                    if result == "play_again":
                        return True
                    elif result == "quit":
                        pygame.quit()
                        sys.exit()
                    elif result == "credits":
                        current_page = CreditsPage()
                elif isinstance(current_page, CreditsPage) and result:
                    current_page = end_page
            elif end_event.type == pygame.KEYDOWN:
                result = current_page.handle_key(end_event)
                
                if isinstance(current_page, EndGamePage):
                    if result == "play_again":
                        return True
                    elif result == "quit":
                        pygame.quit()
                        sys.exit()
                    elif result == "credits":
                        current_page = CreditsPage()
                elif isinstance(current_page, CreditsPage) and result:
                    current_page = end_page
            elif end_event.type == pygame.MOUSEMOTION:
                current_page.handle_motion(end_event.pos)

async def show_logo_screen(screen, logo_path, scale_factor=0.5):
    try:
        base_path = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(base_path, "assets/image/starterbackground.png")
        background = pygame.image.load(bg_path)
        window_size = screen.get_size()
        background = pygame.transform.scale(background, window_size)
        
        logo = pygame.image.load(logo_path)
        
        logo_width = int(window_size[0] * scale_factor)
        logo_height = int(logo_width * (logo.get_height() / logo.get_width()))
        logo = pygame.transform.scale(logo, (logo_width, logo_height))
        
        x = (window_size[0] - logo_width) // 2
        y = (window_size[1] - logo_height) // 2
        
        # Fade in
        for alpha in range(0, 255, 5):
            screen.blit(background, (0, 0))
            
            overlay = pygame.Surface(window_size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            logo_surface = pygame.Surface((logo_width, logo_height), pygame.SRCALPHA)
            logo_surface.fill((255, 255, 255, 0))
            logo_surface.blit(logo, (0, 0))
            logo_surface.set_alpha(alpha)
            screen.blit(logo_surface, (x, y))
            
            pygame.display.flip()
            await asyncio.sleep(0.01)
        
        await asyncio.sleep(1.5)
        
        for alpha in range(255, -1, -5):
            screen.blit(background, (0, 0))
            
            overlay = pygame.Surface(window_size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            logo_surface = pygame.Surface((logo_width, logo_height), pygame.SRCALPHA)
            logo_surface.fill((255, 255, 255, 0))
            logo_surface.blit(logo, (0, 0))
            logo_surface.set_alpha(alpha)
            screen.blit(logo_surface, (x, y))
            
            pygame.display.flip()
            await asyncio.sleep(0.01)
            
    except Exception as e:
        print(f"Error showing logo screen: {e}")

async def show_company_logo(screen):
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    logo_path = os.path.join(base_path, "assets/image/Watson Games 2025.png")
    await show_logo_screen(screen, logo_path, scale_factor=0.7)
    
    group_logo_path = os.path.join(base_path, "assets/image/Group 5 Persent.png")
    await show_logo_screen(screen, group_logo_path, scale_factor=0.9)

async def main():
    global WINDOW_SIZE
    text_scaler.update_scale_factor(WINDOW_SIZE[0], WINDOW_SIZE[1])
    screen = await apply_screen_settings(WINDOW_SIZE)
    
    await show_company_logo(screen)
    
    clock = pygame.time.Clock()
    
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
            
            # Limit fps
            clock.tick(FPS)

if __name__ == "__main__":
    asyncio.run(main())
