import pygame
import pygame
import sys
from src.Board import Board
from src.Property import Property
from src.game_logic import GameLogic
from src.cards import CardType
from typing import Optional
import time
import math
import os
import random
import string
from src.ui import DevelopmentNotification
from src.text_scaler import text_scaler
from src.ui import AIEmotionUI

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(base_path, "assets", "font", "Play-Regular.ttf")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
MODERN_BG = (18, 18, 18)
ACCENT_COLOR = (75, 139, 190)
BUTTON_HOVER = (95, 159, 210)
SUCCESS_COLOR = (40, 167, 69)
ERROR_COLOR = (220, 53, 69)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

GROUP_COLORS = {
    "Brown": (139, 69, 19),    
    "Blue": (0, 0, 255),       
    "Purple": (128, 0, 128),   
    "Orange": (255, 165, 0),   
    "Red": (255, 0, 0),        
    "Yellow": (255, 255, 0),   
    "Green": (0, 255, 0),      
    "Deep Blue": (0, 0, 139)   
}

KEY_ROLL = [pygame.K_SPACE, pygame.K_RETURN]
KEY_BUY = [pygame.K_y, pygame.K_RETURN]
KEY_PASS = [pygame.K_n, pygame.K_ESCAPE]

class Game:
    def __init__(self, players, game_mode="full", time_limit=None, ai_difficulty="easy"):
        if not pygame.get_init():
            pygame.init()
            
        info = pygame.display.Info()
        self.screen = pygame.display.get_surface()
        if not self.screen:
            self.screen = pygame.display.set_mode((info.current_w, info.current_h))
        pygame.display.set_caption("Property Tycoon")

        self.font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(32))
        self.small_font = pygame.font.Font(FONT_PATH, text_scaler.get_scaled_size(24))
        
        self.game_mode = game_mode
        self.time_limit = time_limit
        self.ai_difficulty = ai_difficulty
        self.start_time = pygame.time.get_ticks() if time_limit else None
        
        if self.game_mode == "abridged" and self.time_limit:
            minutes = self.time_limit // 60
            print(f"Game initialized in Abridged mode with {minutes} minutes time limit")
            print(f"Time limit in seconds: {self.time_limit}")
        else:
            print(f"Game initialized in Full mode (no time limit)")
            
        self.rounds_completed = {player.name: 0 for player in players}
        self.lap_count = {player.name: 0 for player in players}
        
        self.game_over = False
        self.winner_index = None
        self.time_limit_reached = False
        self.final_lap = {}
        
        self.time_warning_start = 60
        self.warning_flash_rate = 500
        
        self.auction_completed = False
        self.auction_end_time = 0
        self.auction_end_delay = 3000
        
        self.dice_images = {}
        try:
            for i in range(1, 7):
                dice_path = os.path.join(base_path, "assets", "image", "Dice", f"{i}.png")
                if os.path.exists(dice_path):
                    print(f"Loading dice image: {dice_path}")
                    self.dice_images[i] = pygame.image.load(dice_path)
                else:
                    print(f"Dice image not found: {dice_path}")
        except Exception as e:
            print(f"Error loading dice images: {e}")
        
        try:
            self.logic = GameLogic()
            self.logic.game = self
            self.logic.ai_difficulty = self.ai_difficulty
            
            if self.ai_difficulty == 'hard':
                from src.ai_player_logic import HardAIPlayer
                self.logic.ai_player = HardAIPlayer()
            else:
                from src.ai_player_logic import EasyAIPlayer
                self.logic.ai_player = EasyAIPlayer()
                
            if not self.logic.game_start():
                raise RuntimeError("Failed to initialize game data")
            
            if not players:
                raise ValueError("No players provided")
            
            self.players = players
            self.board = Board(self.players)
            
            from src.cards import CardDeck, CardType
            self.pot_luck_deck = CardDeck(CardType.POT_LUCK)
            self.opportunity_deck = CardDeck(CardType.OPPORTUNITY_KNOCKS)
            
            self.board.update_board_positions()
            self.board.update_ownership(self.logic.properties)
            
            self.state = "ROLL"
            self.current_property = None
            self.last_roll = None
            self.roll_time = 0
            self.ROLL_DISPLAY_TIME = 2000
            
            self.animation_start = 0
            self.animation_duration = 1000
            self.dice_animation = False
            self.dice_values = None
            
            self.player_colors = {}
            
            for i, player in enumerate(players):
                if not self.logic.add_player(player.name):
                    raise RuntimeError(f"Failed to add player {player.name}")
                self.player_colors[player.name] = player.color

            window_size = self.screen.get_size()
            button_width = 120
            button_height = 45
            button_margin = 20
            button_y = window_size[1] - button_height - button_margin
            
            self.roll_button = pygame.Rect(
                window_size[0] - button_width - button_margin,
                button_y,
                button_width,
                button_height
            )
            
            self.quit_button = pygame.Rect(
                window_size[0] - (button_width * 2) - (button_margin * 2),
                button_y,
                button_width,
                button_height
            )
            
            self.pause_button = pygame.Rect(
                window_size[0] - (button_width * 2) - (button_margin * 2), 
                button_y - button_height - button_margin, 
                button_width,
                button_height
            )
            
            self.game_paused = False
            self.pause_start_time = 0
            self.total_pause_time = 0
            
            self.yes_button = pygame.Rect(
                window_size[0] - (button_width * 2) - (button_margin * 2),
                button_y,
                button_width,
                button_height
            )
            
            self.no_button = pygame.Rect(
                window_size[0] - button_width - button_margin,
                button_y,
                button_width,
                button_height
            )
            
            self.auction_buttons = {
                'bid': pygame.Rect(0, 0, 120, 40),
                'pass': pygame.Rect(0, 0, 120, 40)
            }
            self.auction_input = pygame.Rect(0, 0, 200, 40)
            self.auction_bid_amount = ""
            
            self.current_player_is_ai = False
            self.notification = None
            self.notification_time = 0
            self.NOTIFICATION_DURATION = 3000
            
            self.show_popup = False
            self.popup_message = None
            self.popup_title = None
            
            self.show_card = False
            self.current_card = None
            self.current_card_player = None
            self.card_display_time = 0
            self.CARD_DISPLAY_DURATION = 3000
            
            self.development_mode = False
            self.selected_property = None
            self.development_buttons = {}
            self.dev_notification = None
            
            self.free_parking_pot = 0
            
            self.emotion_uis = {}
            for player in self.players:
                if player.is_ai and self.ai_difficulty == 'hard':
                    self.emotion_uis[player.name] = AIEmotionUI(self.screen, player, self)
                    print(f"Initialized emotion UI for {player.name}")
                    
        except Exception as e:
            print(f"Error during game initialization: {e}")
            pygame.quit()
            raise
        
        self.update_current_player()

    def draw_button(self, button, text, hover=False, active=True):
        base_color = BUTTON_HOVER if hover else ACCENT_COLOR
        if not active:
            base_color = GRAY

        shadow_rect = button.copy()
        shadow_rect.y += 2
        shadow = pygame.Surface(button.size, pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=5)
        self.screen.blit(shadow, shadow_rect)

        pygame.draw.rect(self.screen, base_color, button, border_radius=5)
        gradient = pygame.Surface(button.size, pygame.SRCALPHA)
        for i in range(button.height):
            alpha = int(100 * (1 - i/button.height))
            pygame.draw.line(gradient, (255, 255, 255, alpha), 
                           (0, i), (button.width, i))
        self.screen.blit(gradient, button)

        text_shadow = self.font.render(text, True, BLACK)
        text_rect_shadow = text_shadow.get_rect(center=button.center)
        text_rect_shadow.x += 1
        text_rect_shadow.y += 1
        self.screen.blit(text_shadow, text_rect_shadow)

        text_surface = self.font.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=button.center)
        self.screen.blit(text_surface, text_rect)

    def add_message(self, text):
        self.board.add_message(text)

    def draw_time_remaining(self):
        if self.game_mode == "abridged" and self.time_limit:
            current_time = pygame.time.get_ticks()
            
            elapsed = (current_time - self.start_time - self.total_pause_time) // 1000
            
            if self.game_paused:
                current_pause_duration = current_time - self.pause_start_time
                elapsed = (current_time - self.start_time - self.total_pause_time - current_pause_duration) // 1000
            
            remaining = max(0, self.time_limit - elapsed)
            minutes = remaining // 60
            seconds = remaining % 60
            
            window_size = self.screen.get_size()
            
            if hasattr(self, 'time_limit_reached') and self.time_limit_reached and not self.game_over:
                banner_height = 40
                banner_surface = pygame.Surface((window_size[0], banner_height), pygame.SRCALPHA)
                banner_color = (255, 0, 0, 150) 
                banner_surface.fill(banner_color)
                self.screen.blit(banner_surface, (0, 0))
                
                font = pygame.font.Font(None, 28)
                text = font.render("TIME'S UP! Finishing current lap...", True, (255, 255, 255))
                text_rect = text.get_rect(center=(window_size[0] // 2, banner_height // 2))
                self.screen.blit(text, text_rect)
                
                remaining = 0
                minutes = 0
                seconds = 0
            
            if remaining <= self.time_warning_start:
                flash_alpha = abs(math.sin(current_time / self.warning_flash_rate)) * 255
                warning_surface = pygame.Surface(window_size, pygame.SRCALPHA)
                warning_color = (*ERROR_COLOR, int(flash_alpha * 0.1))
                warning_surface.fill(warning_color)
                self.screen.blit(warning_surface, (0, 0))
                
                if remaining == 60 or remaining == 30 or remaining == 10:
                    self.add_message(f"Warning: {remaining} seconds remaining!")

            panel_width = 200
            panel_height = 120
            panel_x = 10
            panel_y = 70 
            
            glow_surface = pygame.Surface((panel_width + 10, panel_height + 10), pygame.SRCALPHA)
            for i in range(5):
                alpha = int(100 * (1 - i/5))
                pygame.draw.rect(glow_surface, (*ACCENT_COLOR[:3], alpha),
                               pygame.Rect(i, i, panel_width + 10 - i*2, panel_height + 10 - i*2),
                               border_radius=10)
            self.screen.blit(glow_surface, (panel_x - 5, panel_y - 5))
            
            panel = pygame.Surface((panel_width, panel_height))
            panel.fill(MODERN_BG)
            self.screen.blit(panel, (panel_x, panel_y))
            
            panel_title = self.small_font.render("GAME STATUS", True, LIGHT_GRAY)
            panel_title_rect = panel_title.get_rect(centerx=panel_x + panel_width//2, top=panel_y + 10)
            self.screen.blit(panel_title, panel_title_rect)
            
            active_players = [p['name'] for p in self.logic.players if not p.get('exited', False)]
            min_lap = min([self.lap_count[p] for p in active_players]) if active_players else 0
            
            time_color = ERROR_COLOR if remaining < 300 else ACCENT_COLOR
            
            lap_y = panel_title_rect.bottom + 7
            lap_icon_text = "🏁"  
            lap_icon = self.small_font.render(lap_icon_text, True, LIGHT_GRAY)
            self.screen.blit(lap_icon, (panel_x + 15, lap_y))
            
            lap_text = self.font.render(f"Lap {min_lap}", True, ACCENT_COLOR)
            self.screen.blit(lap_text, (panel_x + 40, lap_y - 5))
            
            time_y = lap_y + 25
            time_icon_text = "⏱️"  
            time_icon = self.small_font.render(time_icon_text, True, LIGHT_GRAY)
            self.screen.blit(time_icon, (panel_x + 15, time_y))
            
            time_text = self.font.render(f"{minutes:02d}:{seconds:02d}", True, time_color)
            self.screen.blit(time_text, (panel_x + 40, time_y - 5))
            
            progress_width = panel_width - 30
            progress_height = 8
            progress_x = panel_x + 15
            progress_y = panel_y + panel_height - 20
            
            progress_percent = 1 - (remaining / self.time_limit)
            
            pygame.draw.rect(self.screen, GRAY, 
                           pygame.Rect(progress_x, progress_y, progress_width, progress_height),
                           border_radius=4)
            
            fill_width = int(progress_width * progress_percent)
            fill_color = ERROR_COLOR if remaining < 300 else ACCENT_COLOR
            if fill_width > 0:
                pygame.draw.rect(self.screen, fill_color, 
                               pygame.Rect(progress_x, progress_y, fill_width, progress_height),
                               border_radius=4)

    def draw(self):
        if self.game_mode == "abridged" and self.check_time_limit():
            return
            
        if not pygame.display.get_surface():
            return
            
        window_size = self.screen.get_size()
        self.screen.fill(MODERN_BG)
        gradient = pygame.Surface(window_size, pygame.SRCALPHA)
        for i in range(window_size[1]):
            alpha = int(255 * (1 - i/window_size[1]))
            pygame.draw.line(gradient, (*ACCENT_COLOR[:3], alpha), (0, i), (window_size[0], i))
        self.screen.blit(gradient, (0, 0))
        
        self.board.draw(self.screen)
        
        for emotion_ui in self.emotion_uis.values():
            emotion_ui.draw()
            
        self.synchronize_player_positions()
        self.synchronize_player_money()  
        self.synchronize_free_parking_pot()  

        for player in self.players:
            player.update_animation()
            
            if hasattr(player, 'prev_moving') and player.prev_moving and not player.is_moving:
                self.check_passing_go(player, player.move_start_position)
            player.prev_moving = player.is_moving

        any_player_moving = any(player.is_moving for player in self.players)

        if hasattr(self, 'waiting_for_animation') and self.waiting_for_animation and not any_player_moving:
            self.waiting_for_animation = False
            
            if hasattr(self, 'pending_auction_property') and self.pending_auction_property:
                print("Animations completed - starting pending auction")
                property_data = self.pending_auction_property
                self.pending_auction_property = None
                self.start_auction(property_data)

        if hasattr(self, 'auction_completed') and self.auction_completed:
            current_time = pygame.time.get_ticks()
            if current_time - self.auction_end_time > self.auction_end_delay:
                print("Auction delay timer elapsed - changing state to ROLL")
                self.state = "ROLL"
                self.auction_completed = False

        self.board.draw(self.screen)
        
        mouse_pos = pygame.mouse.get_pos()
        
        panel_width = 320
        panel_spacing = 10
        player_height = 100
        total_height = (player_height + panel_spacing) * len(self.logic.players) - panel_spacing
        panel_x = window_size[0] - panel_width - 20
        panel_y = 20

        panel_surface = pygame.Surface((panel_width, total_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (0, 0, 0, 180), panel_surface.get_rect(), border_radius=15)
        self.screen.blit(panel_surface, (panel_x, panel_y))

        current_y = panel_y
        hovered_property = None

        for i, player_data in enumerate(self.logic.players):
            is_current = (i == self.logic.current_player_index)
            player_obj = next((p for p in self.players if p.name == player_data['name']), None)
            
            player_rect = pygame.Rect(panel_x, current_y, panel_width, player_height)
            
            if is_current:
                highlight_surface = pygame.Surface((panel_width, player_height), pygame.SRCALPHA)
                highlight_color = (*ACCENT_COLOR[:3], 50)
                pygame.draw.rect(highlight_surface, highlight_color, 
                               highlight_surface.get_rect(), border_radius=15)
                self.screen.blit(highlight_surface, player_rect)

            logo_size = 60
            logo_margin = 10
            logo_rect = pygame.Rect(panel_x + logo_margin, current_y + (player_height - logo_size) // 2,
                                  logo_size, logo_size)
            
            if player_obj and player_obj.player_image:
                scaled_logo = pygame.transform.scale(player_obj.player_image, (logo_size, logo_size))
                if player_data.get('exited', False) or (player_obj and player_obj.voluntary_exit):
                    scaled_logo.set_alpha(128)
                self.screen.blit(scaled_logo, logo_rect)
            
            info_x = logo_rect.right + 15
            info_y = current_y + 10
            
            name_color = ACCENT_COLOR if is_current else WHITE
            if player_data.get('in_jail', False):
                name_text = f"{player_data['name']} [JAIL]"
                name_color = ERROR_COLOR if is_current else GRAY
            elif player_data.get('exited', False) or (player_obj and player_obj.voluntary_exit):
                name_text = f"{player_data['name']} [EXITED]"
                name_color = (200, 0, 0)  
            else:
                name_text = player_data['name']
            
            name_surface = self.font.render(name_text, True, name_color)
            self.screen.blit(name_surface, (info_x, info_y))
            
            money_y = info_y + 30
            
            money_text = f"£ {player_data['money']:,}"
            money_color = SUCCESS_COLOR if player_data['money'] > 500 else ERROR_COLOR if player_data['money'] < 200 else WHITE
            money_surface = self.small_font.render(money_text, True, money_color)
            self.screen.blit(money_surface, (info_x, money_y))

            props = [prop for prop in self.logic.properties.values() 
                    if prop.get('owner') == player_data['name']]
            
            if props:
                prop_x = info_x
                prop_y = money_y + 30
                prop_size = 15
                prop_spacing = 5
                max_props_per_row = 8
                
                for idx, prop in enumerate(props):
                    row = idx // max_props_per_row
                    col = idx % max_props_per_row
                    x = prop_x + col * (prop_size + prop_spacing)
                    y = prop_y + row * (prop_size + prop_spacing)
                    
                    prop_rect = pygame.Rect(x, y, prop_size, prop_size)
                    group = prop.get('group')
                    color = GROUP_COLORS.get(group, GRAY) if group else GRAY
                    
                    pygame.draw.rect(self.screen, color, prop_rect, border_radius=3)
                    
                    if prop.get('houses', 0) > 0 or prop.get('has_hotel', False):
                        if prop.get('has_hotel', False):
                            indicator_color = RED
                            indicator_text = "H"
                        else:
                            indicator_color = GREEN
                            indicator_text = str(prop.get('houses', 0))
                        
                        indicator_font = pygame.font.Font(None, 12)
                        indicator_surface = indicator_font.render(indicator_text, True, WHITE)
                        indicator_rect = indicator_surface.get_rect(center=prop_rect.center)
                        self.screen.blit(indicator_surface, indicator_rect)
                    
                    if prop_rect.collidepoint(mouse_pos):
                        hovered_property = prop
                        pygame.draw.rect(self.screen, WHITE, prop_rect, 1, border_radius=3)

            if i < len(self.logic.players) - 1:
                pygame.draw.line(self.screen, GRAY, 
                               (panel_x + 10, current_y + player_height - 1),
                               (panel_x + panel_width - 10, current_y + player_height - 1))

            current_y += player_height + panel_spacing

        if hovered_property:
            self.draw_property_tooltip(hovered_property, mouse_pos)

        self.draw_time_remaining()
        
        self.draw_free_parking_pot()
        
        self.draw_notification()
        
        for emotion_ui in self.emotion_uis.values():
            emotion_ui.draw()
        
        if self.state == "ROLL":
            current_player = next((p for p in self.players if p.name == self.logic.players[self.logic.current_player_index]['name']), None)
            self.current_player_is_ai = current_player and current_player.is_ai
            
            human_players_remaining = any(
                not p.is_ai and not p.voluntary_exit and not p.bankrupt 
                for p in self.players
            )
            
            if not self.current_player_is_ai:
                for emotion_ui in self.emotion_uis.values():
                    emotion_ui.draw()
                    
                self.draw_button(self.roll_button, "Roll", 
                               hover=self.roll_button.collidepoint(mouse_pos))
                
                if self.game_mode == "abridged" and self.time_limit:
                    pause_hover = self.pause_button.collidepoint(mouse_pos)
                    button_text = "Continue" if self.game_paused else "Pause"
                    self.draw_button(self.pause_button, button_text, hover=pause_hover)
                
                if human_players_remaining:
                    quit_hover = self.quit_button.collidepoint(mouse_pos)
                    base_color = BUTTON_HOVER if quit_hover else ERROR_COLOR
                    
                    shadow_rect = self.quit_button.copy()
                    shadow_rect.y += 2
                    shadow = pygame.Surface(self.quit_button.size, pygame.SRCALPHA)
                    pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=5)
                    self.screen.blit(shadow, shadow_rect)
    
                    pygame.draw.rect(self.screen, base_color, self.quit_button, border_radius=5)
                    gradient = pygame.Surface(self.quit_button.size, pygame.SRCALPHA)
                    for i in range(self.quit_button.height):
                        alpha = int(100 * (1 - i/self.quit_button.height))
                        pygame.draw.line(gradient, (255, 255, 255, alpha), 
                                       (0, i), (self.quit_button.width, i))
                    self.screen.blit(gradient, self.quit_button)
    
                    quit_text = self.font.render("Leave Game", True, WHITE)
                    text_rect = quit_text.get_rect(center=self.quit_button.center)
                    text_shadow = self.font.render("Leave Game", True, BLACK)
                    text_shadow_rect = text_shadow.get_rect(center=self.quit_button.center)
                    text_shadow_rect.x += 1
                    text_shadow_rect.y += 1
                    self.screen.blit(text_shadow, text_shadow_rect)
                    self.screen.blit(quit_text, text_rect)
                
            elif not self.dice_animation and not any_player_moving:
                self.check_and_trigger_ai_turn()
                
        elif self.state == "BUY" and self.current_property is not None:
            self.draw_property_card(self.current_property)
            self.draw_buy_options(mouse_pos)
        elif self.state == "AUCTION" and hasattr(self.logic, 'current_auction'):
            if self.logic.current_auction is None:
                print("Warning: current_auction is None - resetting state to ROLL")
                self.state = "ROLL"
                return
                
            self.draw_auction(self.logic.current_auction)
            result_message = self.logic.check_auction_end()
            if result_message == "auction_completed":
                print("Auction completed in draw method - setting up delay")
                
                if self.logic.current_auction and self.logic.current_auction.get("highest_bidder"):
                    winner = self.logic.current_auction["highest_bidder"]
                    property_name = self.logic.current_auction.get("property", {}).get("name", "Unknown property")
                    bid_amount = self.logic.current_auction.get("current_bid", 0)
                    self.show_notification(f"{winner['name']} won {property_name} for £{bid_amount}", 3000)
                else:
                    property_name = self.logic.current_auction.get("property", {}).get("name", "Unknown property")
                    self.show_notification(f"No one bid on {property_name}", 3000)
                
                self.auction_end_time = pygame.time.get_ticks()
                self.auction_end_delay = 3000
                self.auction_completed = True
                self.board.update_ownership(self.logic.properties)
        elif self.state == "DEVELOPMENT" and self.selected_property is not None:
            if hasattr(self.logic, 'current_auction') and self.logic.current_auction:
                print("Auction in progress - not showing development UI")
            else:
                current_player = self.logic.players[self.logic.current_player_index]
                player_obj = next((p for p in self.players if p.name == current_player['name']), None)
                
                if player_obj and player_obj.is_ai:
                    print(f"Auto-closing development UI for AI player {current_player['name']}")
                    self.state = "ROLL"
                    self.selected_property = None
                    self.development_mode = False
                else:
                    self.draw_development_ui(self.selected_property)
            
        if self.development_mode and not any_player_moving and not self.dice_animation:
            if hasattr(self.logic, 'current_auction') and self.logic.current_auction:
                print("Auction in progress - not showing development notification")
            else:
                current_player = self.logic.players[self.logic.current_player_index]
                owned_properties = [p for p in self.logic.properties.values() if p.get('owner') == current_player['name']]
                if owned_properties:
                    if not self.dev_notification:
                        self.dev_notification = DevelopmentNotification(self.screen, current_player['name'], self.font)
                    
                    self.dev_notification.draw(mouse_pos)
        
        current_time = pygame.time.get_ticks()
        if self.dice_animation:
            if current_time - self.animation_start < self.animation_duration:
                dice1 = ((current_time // 100) % 6) + 1
                dice2 = ((current_time // 150) % 6) + 1
                self.draw_dice(dice1, dice2, True)
            else:
                self.finish_dice_animation()
        elif self.last_roll and (current_time - self.roll_time < self.ROLL_DISPLAY_TIME):
            dice1, dice2 = self.last_roll
            self.draw_dice(dice1, dice2, False)

        if self.show_card and self.current_card and self.current_card_player:
            self.draw_card_alert(self.current_card, self.current_card_player)
            
            if current_time - self.card_display_time > self.CARD_DISPLAY_DURATION:
                self.show_card = False
                self.current_card = None
                self.current_card_player = None

        self.board.camera.handle_camera_controls(pygame.key.get_pressed())

        self.board.update_board_positions()
        
        if not self.game_over:
            game_over_data = self.check_game_over()
            if game_over_data:
                if "winner" in game_over_data:
                    self.handle_game_over(game_over_data["winner"])
        
        if self.show_popup:
            self.draw_popup_message()
            
        pygame.display.flip()

    def draw_dice(self, dice1, dice2, is_rolling):
        window_size = self.screen.get_size()
        dice_size = int(window_size[1] * 0.08)
        spacing = dice_size // 3
        start_x = window_size[0] - (dice_size * 2 + spacing) - 20
        y = window_size[1] - dice_size - 80

        for i, value in enumerate([dice1, dice2]):
            x = start_x + (dice_size + spacing) * i
            
            shadow_rect = pygame.Rect(x + 2, y + 2, dice_size, dice_size)
            shadow = pygame.Surface((dice_size, dice_size), pygame.SRCALPHA)
            pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=10)
            self.screen.blit(shadow, shadow_rect)
            
            dice_rect = pygame.Rect(x, y, dice_size, dice_size)
            pygame.draw.rect(self.screen, WHITE, dice_rect, border_radius=10)
            
            if value in self.dice_images:
                scaled_dice = pygame.transform.scale(self.dice_images[value], (dice_size - 4, dice_size - 4))
                image_rect = scaled_dice.get_rect(center=dice_rect.center)
                self.screen.blit(scaled_dice, image_rect)
            else:
                dice_text = self.font.render(str(value), True, BLACK)
                dice_text_rect = dice_text.get_rect(center=dice_rect.center)
                self.screen.blit(dice_text, dice_text_rect)
            
            color = ACCENT_COLOR if is_rolling else BLACK
            pygame.draw.rect(self.screen, color, dice_rect, 2, border_radius=10)

        if not is_rolling and dice1 == dice2:
            current_time = pygame.time.get_ticks()
            num_sparkles = 20
            for i in range(num_sparkles):
                angle = (current_time / 500 + i * (360 / num_sparkles)) % 360
                radius = 40 + math.sin(current_time / 200 + i) * 10
                sparkle_x = start_x + dice_size + spacing/2 + math.cos(math.radians(angle)) * radius
                sparkle_y = y + dice_size/2 + math.sin(math.radians(angle)) * radius
                sparkle_color = (255, 255, 0, max(0, math.sin(current_time / 200 + i) * 255))
                sparkle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(sparkle_surface, sparkle_color, (2, 2), 2)
                self.screen.blit(sparkle_surface, (sparkle_x, sparkle_y))

    def draw_property_card(self, property_data):
        if not property_data:
            return
            
        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.25)
        card_height = int(window_size[1] * 0.4)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2

        shadow_rect = pygame.Rect(card_x + 4, card_y + 4, card_width, card_height)
        shadow = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, shadow_rect)

        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, WHITE, card_rect, border_radius=15)

        if 'group' in property_data:
            header_height = 40
            header_rect = pygame.Rect(card_x, card_y, card_width, header_height)
            header_color = GROUP_COLORS.get(property_data['group'], GRAY)
            pygame.draw.rect(self.screen, header_color, header_rect, border_radius=15)
            pygame.draw.rect(self.screen, header_color, pygame.Rect(card_x, card_y + header_height - 15, card_width, 15))

        name_text = self.font.render(property_data['name'], True, BLACK)
        name_rect = name_text.get_rect(centerx=card_rect.centerx, top=card_y + 50)
        self.screen.blit(name_text, name_rect)

        y_offset = name_rect.bottom + 20
        padding = 20

        price_text = self.font.render(f"Price: £{property_data['price']}", True, ACCENT_COLOR)
        self.screen.blit(price_text, (card_x + padding, y_offset))
        y_offset += 35

        rent_text = self.small_font.render(f"Base Rent: £{property_data.get('rent', 0)}", True, BLACK)
        self.screen.blit(rent_text, (card_x + padding, y_offset))
        y_offset += 25

        if 'house_costs' in property_data:
            for i, cost in enumerate(property_data['house_costs'], 1):
                house_text = self.small_font.render(f"{i} House{'s' if i > 1 else ''}: £{cost}", True, BLACK)
                self.screen.blit(house_text, (card_x + padding, y_offset))
                y_offset += 25

        if "Station" in property_data['name']:
            rent_rules = ["1 Station: £25", "2 Stations: £50", "3 Stations: £100", "4 Stations: £200"]
            for rule in rent_rules:
                rule_text = self.small_font.render(rule, True, BLACK)
                self.screen.blit(rule_text, (card_x + padding, y_offset))
                y_offset += 25
        elif property_data['name'] in ["Tesla Power Co", "Edison Water"]:
            utility_text = self.small_font.render("Rent = 4x dice if 1 owned", True, BLACK)
            self.screen.blit(utility_text, (card_x + padding, y_offset))
            y_offset += 25
            utility_text2 = self.small_font.render("Rent = 10x dice if both owned", True, BLACK)
            self.screen.blit(utility_text2, (card_x + padding, y_offset))

    def draw_buy_options(self, mouse_pos):
        window_size = self.screen.get_size()
        button_width = 100
        button_height = 40
        spacing = 20
        
        card_width = int(window_size[0] * 0.35)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_width) // 2
        
        total_width = (button_width * 2) + spacing
        start_x = card_x + (card_width - total_width) // 2
        button_y = card_y + card_width - button_height - 20
        
        self.yes_button = pygame.Rect(start_x, button_y, button_width, button_height)
        self.no_button = pygame.Rect(start_x + button_width + spacing, button_y, button_width, button_height)
        
        yes_hover = self.yes_button.collidepoint(mouse_pos)
        no_hover = self.no_button.collidepoint(mouse_pos)
        
        pygame.draw.rect(self.screen, BUTTON_HOVER if yes_hover else ACCENT_COLOR, self.yes_button, border_radius=5)
        pygame.draw.rect(self.screen, BUTTON_HOVER if no_hover else ACCENT_COLOR, self.no_button, border_radius=5)
        
        yes_text = self.font.render("Buy", True, WHITE)
        no_text = self.font.render("Pass", True, WHITE)
        
        self.screen.blit(yes_text, (self.yes_button.centerx - yes_text.get_width()//2, 
                                   self.yes_button.centery - yes_text.get_height()//2))
        self.screen.blit(no_text, (self.no_button.centerx - no_text.get_width()//2, 
                                  self.no_button.centery - no_text.get_height()//2))

    def draw_property_tooltip(self, property_data, mouse_pos):
        padding = 10
        window_size = self.screen.get_size()
        
        tooltip_width = 250
        line_height = 25
        num_lines = 5
        if property_data.get('houses', 0) > 0 or property_data.get('has_hotel', False):
            num_lines += 1
        if property_data.get('group'):
            num_lines += 1
        tooltip_height = num_lines * line_height + padding * 2
        
        x = min(mouse_pos[0] + 20, window_size[0] - tooltip_width - padding)
        y = min(mouse_pos[1] + 20, window_size[1] - tooltip_height - padding)
        
        shadow_surface = pygame.Surface((tooltip_width + 4, tooltip_height + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 128), shadow_surface.get_rect(), border_radius=10)
        self.screen.blit(shadow_surface, (x + 2, y + 2))
        
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        pygame.draw.rect(tooltip_surface, (30, 30, 30, 240), tooltip_surface.get_rect(), border_radius=10)
        
        if property_data.get('group'):
            header_height = 30
            header_color = GROUP_COLORS.get(property_data['group'], GRAY)
            pygame.draw.rect(tooltip_surface, header_color, 
                           (0, 0, tooltip_width, header_height), border_radius=10)
            pygame.draw.rect(tooltip_surface, header_color,
                           (0, header_height - 15, tooltip_width, 15))
        
        self.screen.blit(tooltip_surface, (x, y))
        
        current_y = y + padding
        
        name_text = self.small_font.render(property_data['name'], True, WHITE)
        self.screen.blit(name_text, (x + padding, current_y))
        current_y += line_height
        
        if property_data.get('group'):
            group_text = self.small_font.render(f"Group: {property_data['group']}", True, LIGHT_GRAY)
            self.screen.blit(group_text, (x + padding, current_y))
            current_y += line_height
        
        price_text = self.small_font.render(f"Price: £{property_data.get('price', 0):,}", True, SUCCESS_COLOR)
        self.screen.blit(price_text, (x + padding, current_y))
        current_y += line_height
        
        base_rent = property_data.get('rent', 0)
        rent_text = self.small_font.render(f"Base Rent: £{base_rent:,}", True, ACCENT_COLOR)
        self.screen.blit(rent_text, (x + padding, current_y))
        current_y += line_height
        
        if property_data.get('houses', 0) > 0:
            houses = property_data['houses']
            house_text = self.small_font.render(f"Houses Built: {houses}", True, GREEN)
            self.screen.blit(house_text, (x + padding, current_y))
            current_y += line_height
        elif property_data.get('has_hotel', False):
            hotel_text = self.small_font.render("Has Hotel", True, RED)
            self.screen.blit(hotel_text, (x + padding, current_y))
            current_y += line_height
        
        if property_data.get('mortgaged', False):
            mortgage_text = self.small_font.render("[MORTGAGED]", True, ERROR_COLOR)
            self.screen.blit(mortgage_text, (x + padding, current_y))
        else:
            mortgage_value = property_data.get('price', 0) // 2
            mortgage_text = self.small_font.render(f"Mortgage Value: £{mortgage_value:,}", True, LIGHT_GRAY)
            self.screen.blit(mortgage_text, (x + padding, current_y))

        pygame.draw.rect(self.screen, ACCENT_COLOR, 
                        (x, y, tooltip_width, tooltip_height), 1, border_radius=10)

    def finish_dice_animation(self):
        if not self.dice_animation or not self.dice_values:
            return
            
        print("\n=== Dice Roll Debug ===")
        self.dice_animation = False
        dice1, dice2 = self.dice_values
        print(f"Dice roll: {dice1, dice2} (Total: {dice1 + dice2})")
        
        self.last_roll = (dice1, dice2)
        self.roll_time = pygame.time.get_ticks()
        current_player = self.logic.players[self.logic.current_player_index]
        

        print(f"Current player: {current_player['name']}")
        print(f"Current position: {current_player['position']}")

        self.wait_for_animations()

        while self.logic.message_queue:
            message = self.logic.message_queue.pop(0)
            print(f"Processing message: {message}")
            self.board.add_message(message)

        if current_player.get('in_jail', False):
            print("Player is in jail")
            if dice1 == dice2:
                print("Rolled doubles - getting out of jail")
                current_player['in_jail'] = False
                current_player['jail_turns'] = 0
                self.board.add_message(f"{current_player['name']} rolled doubles and got out of jail!")
                
                for player in self.players:
                    if player.name == current_player['name']:
                        player.in_jail = False
                        break
            else:
                print("Failed to roll doubles - staying in jail")
                self.handle_jail_turn(current_player)
                self.state = "ROLL"
                return

        position = current_player['position']
        print(f"Landing on position: {position}")
        
        self.board.update_board_positions()
        self.board.update_ownership(self.logic.properties)

        current_player_obj = next((p for p in self.players if p.name == current_player['name']), None)

        card_type = None
        if position == 3 or position == 18 or position == 34:
            print(f"Player landed on Pot Luck space {position}")
            card_type = "POT_LUCK"
            self.board.add_message(f"{current_player['name']} landed on Pot Luck")
            result = self.handle_card_draw(current_player, card_type)
            if result == "moved":
                self.wait_for_animations()
                self.board.update_board_positions()
                
        elif position == 8 or position == 23 or position == 37:
            print(f"Player landed on Opportunity Knocks space {position}")
            card_type = "OPPORTUNITY_KNOCKS"
            self.board.add_message(f"{current_player['name']} landed on Opportunity Knocks")
            result = self.handle_card_draw(current_player, card_type)
            if result == "moved":
                self.wait_for_animations()
                self.board.update_board_positions()
                
        if str(position) in self.logic.properties and not card_type:
            space = self.logic.properties[str(position)]
            print(f"\nLanded on property: {space['name']}")
            print(f"Property owner: {space.get('owner', 'None')}")
            
            if space["name"] == "Go to Jail":
                print("Go to Jail space - moving player to jail")
                self.board.add_message(f"{current_player['name']} goes to Jail!")
                current_player['in_jail'] = True
                current_player['jail_turns'] = 0
                current_player['position'] = 11
                
                if current_player_obj:
                    current_player_obj.position = 11
                    current_player_obj.in_jail = True
                    current_player_obj.just_went_to_jail = True
                
                self.logic.is_going_to_jail = True
                
                self.state = "ROLL"
                self.board.update_board_positions()
            elif "price" in space and space.get("owner") is None and not current_player.get('in_jail', False):
                if current_player.get('in_jail', False):
                    print("Player in jail - cannot buy property")
                    self.board.add_message(f"{current_player['name']} cannot buy property while in jail!")
                    self.state = "ROLL"
                else:
                    print("\nUnowned property - initiating buy sequence")
                    print(f"Property price: £{space['price']}")
                    print(f"Player money: £{current_player['money']}")
                    
                    self.board.add_message(f"{current_player['name']} landed on {space['name']}")
                    
                    if self.logic.completed_circuits.get(current_player['name'], 0) < 1:
                        message = f"{current_player['name']} must pass GO before buying property"
                        self.board.add_message(message)
                        print("Player has not completed a circuit - cannot buy property")
                        self.show_notification(message, 2000)
                        self.state = "ROLL"
                        return False
                    
                    self.board.add_message(f"Buy {space['name']} for £{space['price']}?")
                    
                    self.draw()
                    pygame.display.flip()
                    
                    pygame.time.delay(500)
                    self.state = "BUY"
                    self.current_property = space
                    print("Buy state activated")
                    
                    if current_player_obj and current_player_obj.is_ai:
                        print("\nAI player making purchase decision")
                        pygame.time.delay(1000)
                        will_buy = random.random() < 0.7 and current_player['money'] >= space['price']
                        print(f"AI decision: {'Buy' if will_buy else 'Pass'}")
                        self.handle_buy_decision(will_buy)
            else:
                print("Property already owned or not purchasable")
                self.state = "ROLL"
                
                if current_player_obj and current_player_obj.is_ai:
                    property_to_develop = self.logic.ai_player.handle_property_development(
                        current_player, self.logic.properties)
                    if property_to_develop:
                        house_cost = property_to_develop['price'] / 2
                        if current_player['money'] >= house_cost:
                            property_to_develop['houses'] = property_to_develop.get('houses', 0) + 1
                            current_player['money'] -= house_cost
                            self.board.add_message(
                                f"{current_player['name']} built a house on {property_to_develop['name']}")
                            self.board.update_ownership(self.logic.properties)
        else:
            print("Not a property space or already processed by card handling")
            self.state = "ROLL"

        self.update_current_player()
        
        self.wait_for_animations()

        while self.logic.message_queue:
            message = self.logic.message_queue.pop(0)
            print(f"Processing message: {message}")
            self.board.add_message(message)
            if "Get Out of Jail Free card" in message or "collected" in message:
                self.show_notification(message, 3000)
        
        print(f"\nFinal state: {self.state}")
        print("=== End Dice Roll Debug ===\n")
        
        self.draw()
        pygame.display.flip()
        
        self.development_mode = True
        
        current_player = self.logic.players[self.logic.current_player_index]
        owned_properties = [p for p in self.logic.properties.values() if p.get('owner') == current_player['name']]
        if not owned_properties:
            self.development_mode = False

        self.logic.is_going_to_jail = False
        
        self.handle_space(current_player)

    def play_turn(self):
        if self.game_over:
            return False
            
        if self.dice_animation:
            return False
            
        if any(player.is_moving for player in self.players):
            return False

        current_player = self.logic.players[self.logic.current_player_index]
        if not current_player:
            self.board.add_message("Error: No current player found")
            return False
            
        self.update_current_player()
        
        old_position = current_player['position']

        self.lap_count[current_player['name']] += 1
        print(f"Lap count for {current_player['name']}: {self.lap_count[current_player['name']]}")
        
        self.dice_animation = True
        self.animation_start = pygame.time.get_ticks()
        
        self.board.add_message(f"{current_player['name']}'s turn")
        
        dice1, dice2 = self.logic.play_turn()
        if dice1 is None:
            self.dice_animation = False
            return True
        
        self.dice_values = (dice1, dice2)
        
        for player in self.players:
            if player.name == current_player['name']:
                if player.position != old_position:
                    print(f"Correcting position mismatch for {player.name}: Player object: {player.position}, Game logic: {old_position}")
                    player.position = old_position
                
                spaces_to_move = (current_player['position'] - old_position) % 40
                if spaces_to_move == 0 and current_player['position'] != old_position:
                    spaces_to_move = 40
                
                self.move_player(player, spaces_to_move)
                print(f"Starting animation for {player.name} to move {spaces_to_move} spaces from {old_position} to {current_player['position']}")
                break
        
        self.wait_for_animations()
        
        self.board.update_board_positions()
        
        if current_player['position'] < old_position:
            self.rounds_completed[current_player['name']] += 1
            self.board.add_message("*** PASSED GO! ***")
            self.board.add_message(f"{current_player['name']} collected £200")
        
        self.board.add_message(f"{current_player['name']} rolled {dice1 + dice2}")
        
        if dice1 == dice2:
            self.board.add_message("Doubles! Roll again!")
        
        if self.check_game_over():
            return True
        
        return False

    def check_game_over(self):
        current_time = pygame.time.get_ticks()
        end_game_data = None
        
        if self.game_mode == "full":
            if not self.logic.players:
                if self.logic.bankrupted_players:
                    winner = self.logic.bankrupted_players[-2] if len(self.logic.bankrupted_players) > 1 else None
                    self.game_over = True
                    return {"winner": winner,
                           "bankrupted_players": self.logic.bankrupted_players,
                           "voluntary_exits": self.logic.voluntary_exits}
                return None
                
            active_players = [p for p in self.logic.players if p['money'] > 0]
            if len(active_players) <= 1:
                winner = active_players[0]['name'] if active_players else None
                self.game_over = True
                return {"winner": winner,
                        "bankrupted_players": self.logic.bankrupted_players,
                        "voluntary_exits": self.logic.voluntary_exits}
            
            human_players = [p for p in self.players if not p.is_ai and not p.bankrupt and not p.voluntary_exit]
            ai_players = [p for p in self.players if p.is_ai and not p.bankrupt and not p.voluntary_exit]
            
            if len(human_players) == 0 and len(ai_players) == 1:
                winner = ai_players[0].name
                self.game_over = True
                return {"winner": winner,
                        "bankrupted_players": self.logic.bankrupted_players,
                        "voluntary_exits": self.logic.voluntary_exits}
                
        elif self.game_mode == "abridged":
            if self.time_limit and (current_time - self.start_time) // 1000 >= self.time_limit:
                active_players = [p['name'] for p in self.logic.players if not p.get('exited', False)]
                
                if active_players:
                    min_laps = min([self.lap_count[p] for p in active_players])
                    if all(self.lap_count[p] == min_laps for p in active_players):
                        assets = {}
                        for player in self.logic.players:
                            total = player['money']
                            for prop in self.logic.properties.values():
                                if prop.get('owner') == player['name']:
                                    total += prop.get('price', 0)
                                    if 'houses' in prop:
                                        house_costs = prop.get('house_costs', [])
                                        houses_count = prop['houses']
                                        if house_costs and houses_count > 0:
                                            total += sum(house_costs[:houses_count])
                            assets[player['name']] = total
                        
                        max_asset_value = max(assets.values())
                        
                        winners = [player for player, value in assets.items() if value == max_asset_value]
                        
                        if len(winners) == 1:
                            winner = winners[0]
                        else:
                            winner = "Tie"
                            
                        self.game_over = True
                        return {
                            "winner": winner,
                            "tied_winners": winners if len(winners) > 1 else None,
                            "final_assets": assets,
                            "bankrupted_players": self.logic.bankrupted_players,
                            "voluntary_exits": self.logic.voluntary_exits
                        }
        
        return None

    def handle_buy_decision(self, wants_to_buy):
        if self.current_property is None:
            return
            
        current_player = self.logic.players[self.logic.current_player_index]
        property_data = self.current_property
        
        print("\n=== Property Purchase Debug ===")
        print(f"Current state: {self.state}")
        print(f"Player: {current_player['name']}")
        print(f"Player money: £{current_player['money']}")
        print(f"Property: {property_data['name']}")
        print(f"Property price: £{property_data['price']}")
        print(f"Wants to buy: {wants_to_buy}")
        print(f"Is AI: {self.current_player_is_ai}")
        print(f"Completed circuits: {self.logic.completed_circuits.get(current_player['name'], 0)}")
        
        if wants_to_buy:
            if current_player['money'] >= property_data['price']:
                print("\nAttempting purchase...")
                current_player['money'] -= property_data['price']
                property_data['owner'] = current_player['name']
                self.board.add_message(f"{current_player['name']} bought {property_data['name']} for £{property_data['price']}")
                print("Purchase successful")
                
                if not hasattr(self.logic, 'current_auction') or not self.logic.current_auction:
                    print("State changed to ROLL")
                    self.state = "ROLL"
                else:
                    print("Auction in progress - maintaining AUCTION state")
                    
                self.board.update_ownership(self.logic.properties)
            else:
                print("\nNot enough money for purchase")
                self.board.add_message(f"{current_player['name']} doesn't have enough money to buy {property_data['name']}")
                
                print("Starting auction due to insufficient funds")
                self.start_auction(property_data)
        else:
            print("\nPlayer passed on purchase")
            
            self.start_auction(property_data)
            
        print("\nFinal state:")
        print(f"Property owner: {property_data['owner']}")
        print(f"Player money: £{current_player['money']}")
        
        if not hasattr(self.logic, 'current_auction') or not self.logic.current_auction:
            print(f"Final state: {self.state}")
        else:
            print(f"Auction in progress - state is {self.state}")
            
    def start_auction(self, property_data):
        print(f"\n=== Starting Auction for {property_data['name']} ===")
        
        self.development_mode = False
        self.selected_property = None
        self.dev_notification = None
        
        any_eligible = False
        for player in self.logic.players:
            if self.logic.completed_circuits.get(player['name'], 0) >= 1:
                any_eligible = True
                break
                
        if not any_eligible:
            print("No players have completed a circuit - skipping auction")
            message = "No players have completed a circuit - property remains unsold"
            self.board.add_message(message)
            self.show_notification(message, 2000)
            self.state = "ROLL"
            return
            
        any_moving = any(player.is_moving for player in self.players)
        if any_moving:
            print("Animations in progress - delaying auction start")
            self.pending_auction_property = property_data
            self.waiting_for_animation = True
            return
            
        result = self.logic.auction_property(property_data['position'])
        
        if result == "auction_in_progress":
            self.state = "AUCTION"
            self.auction_bid_amount = ""
            print(f"State changed to {self.state}")
            self.auction_just_started = True
        else:
            print(f"Failed to start auction: {result}")
            self.state = "ROLL"
            print(f"State changed to {self.state}")

    def handle_space(self, current_player):
        position = str(current_player['position'])
        if position not in self.logic.properties:
            return None, None

        space = self.logic.properties[position]
        
        if "price" in space and space["owner"] is None and not current_player.get('in_jail', False):
            self.current_property = space
            self.state = "BUY"
            
            if self.logic.completed_circuits.get(current_player['name'], 0) < 1:
                self.board.add_message(f"{current_player['name']} must pass GO before buying property")
                self.start_auction(space)
                return None, None
            
            player_obj = next((p for p in self.players if p.name == current_player['name']), None)
            is_ai_player = player_obj.is_ai if player_obj else current_player.get('is_ai', False)
            
            if not is_ai_player:
                self.board.add_message(f"Would you like to buy {space['name']} for £{space['price']}?")
                return "can_buy", None
            else:
                if self.logic.ai_player.should_buy_property(space, current_player['money'], 
                    [p for p in self.logic.properties.values() if p.get('owner') == current_player['name']]):
                    self.handle_buy_decision(True)
                else:
                    self.handle_buy_decision(False)
                return None, None

        return self.logic.handle_space(current_player)

    def handle_click(self, pos):
        if self.game_over:
            return
            
        for emotion_ui in self.emotion_uis.values():
            if emotion_ui.handle_click(pos):
                return
                
        if self.show_popup:
            if self.popup_rect.collidepoint(pos):
                self.show_popup = False
            return False
            
        if self.show_card:
            self.show_card = False
            self.current_card = None
            self.current_card_player = None
            return False

        any_player_moving = any(player.is_moving for player in self.players)
        if any_player_moving:
            print("Animations in progress, delaying game state progression")
            return False

        print(f"\n=== Handle Click Debug ===")
        print(f"Current state: {self.state}")
        print(f"Development mode: {self.development_mode}")
        
        if self.development_mode and self.dev_notification and self.dev_notification.check_button_click(pos):
            print("Continuing from development mode")
            self.development_mode = False
            self.selected_property = None
            self.state = "ROLL"
            self.dev_notification = None
            self.notification = None
            self.logic.current_player_index = (self.logic.current_player_index + 1) % len(self.logic.players)
            return False
        
        if hasattr(self, 'auction_just_started') and self.auction_just_started:
            print("Auction just started - ignoring click to prevent state transition")
            self.auction_just_started = False
            return False
        
        if self.state == "ROLL":
            if not self.current_player_is_ai and self.game_mode == "abridged" and self.time_limit and self.pause_button.collidepoint(pos):
                current_time = pygame.time.get_ticks()
                
                if self.game_paused:
                    pause_duration = current_time - self.pause_start_time
                    self.total_pause_time += pause_duration
                    self.game_paused = False
                    self.add_message("Game resumed")
                    self.show_notification("Game resumed", 2000)
                else:
                    self.game_paused = True
                    self.pause_start_time = current_time
                    self.add_message("Game paused")
                    self.show_notification("Game paused - Click Continue to resume", 2000)
                
                return False
                
            if not self.current_player_is_ai and self.roll_button.collidepoint(pos):
                if self.game_mode == "abridged" and self.time_limit and self.game_paused:
                    self.show_notification("Game is paused. Click Continue to resume.", 2000)
                    return False
                else:
                    return self.play_turn()
                
            human_players_remaining = any(
                not p.is_ai and not p.voluntary_exit and not p.bankrupt 
                for p in self.players
            )
                
            if not self.current_player_is_ai and human_players_remaining and self.quit_button.collidepoint(pos):
                confirm_exit = self.show_exit_confirmation()
                
                if confirm_exit:
                    current_player = self.logic.players[self.logic.current_player_index]
                    
                    final_assets = self.calculate_player_assets(current_player)
                    
                    result = self.handle_voluntary_exit(current_player['name'], final_assets)
                    
                    if isinstance(result, dict):
                        return result
                    elif result:
                        self.board.add_message(f"{current_player['name']} has voluntarily exited the game")
                        self.show_notification(f"{current_player['name']} has voluntarily exited the game", 3000)
                        
                        game_over_result = self.check_game_over()
                        if game_over_result:
                            return game_over_result
                        
                        if len(self.logic.players) > 0:
                            self.state = "ROLL"
                            self.check_and_trigger_ai_turn()
                        else:
                            return self.check_game_over()
                return False
            
            if self.development_mode:
                if hasattr(self.logic, 'current_auction') and self.logic.current_auction:
                    print("Auction in progress - ignoring development click")
                    return False
                    
                current_player = self.logic.players[self.logic.current_player_index]
                print(f"Checking property clicks for player {current_player['name']}")
                
                property_pos = self.board.property_clicked(pos)
                if property_pos:
                    print(f"Clicked on property at position {property_pos}")
                    
                    pos_str = str(property_pos)
                    if pos_str in self.logic.properties:
                        prop_data = self.logic.properties[pos_str]
                        
                        if prop_data.get('owner') == current_player['name']:
                            print(f"Player {current_player['name']} clicked on their property {prop_data['name']}")
                            self.selected_property = prop_data
                            self.state = "DEVELOPMENT"
                            return False
                        else:
                            owner = prop_data.get('owner', 'Bank')
                            print(f"Property {prop_data['name']} is owned by {owner}, not {current_player['name']}")
                            self.board.add_message(f"Property {prop_data['name']} is owned by {owner}")
                    else:
                        print(f"No property data found for position {property_pos}")
        
        elif self.state == "BUY" and self.current_property is not None:
            current_player = self.logic.players[self.logic.current_player_index]
            if current_player.get('in_jail', False):
                self.board.add_message(f"{current_player['name']} cannot buy property while in jail!")
                self.state = "ROLL"
                return False
                
            if self.yes_button.collidepoint(pos):
                self.handle_buy_decision(True)
                return False
            elif self.no_button.collidepoint(pos):
                self.handle_buy_decision(False)
                return False
            return False
        
        elif self.state == "AUCTION":
            print("\n=== Handling Auction Click ===")
            auction_result = self.handle_auction_click(pos)
            print(f"Auction click result: {auction_result}")
            
            if auction_result == True:
                print("Auction completed - changing state to ROLL")
                self.state = "ROLL"
                self.current_property = None
                self.board.update_ownership(self.logic.properties)
            else:
                print("Auction continues - maintaining AUCTION state")
            return False
        
        elif self.state == "DEVELOPMENT" and self.selected_property:
            result = self.handle_development_click(pos, self.selected_property)
            if result:
                self.selected_property = None
                self.state = "ROLL"
            return False
            
        print(f"Final state after click: {self.state}")
        return False

    def handle_motion(self, pos):
        if self.game_over:
            return
            
        for emotion_ui in self.emotion_uis.values():
            emotion_ui.check_hover(pos)
            
        if self.state == "ROLL":
            hover_buttons = [self.roll_button.collidepoint(pos), self.quit_button.collidepoint(pos)]
            
            if self.game_mode == "abridged" and self.time_limit:
                hover_buttons.append(self.pause_button.collidepoint(pos))
                
            return any(hover_buttons)
        elif self.state == "BUY":
            return self.yes_button.collidepoint(pos) or self.no_button.collidepoint(pos)
        elif self.state == "AUCTION":
            return any(btn.collidepoint(pos) for btn in self.auction_buttons.values())
        return False

    def handle_key(self, event):
        any_player_moving = any(player.is_moving for player in self.players)
        if any_player_moving and event.key not in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
            print("Animations in progress, ignoring key input")
            return False
            
        print(f"\n=== Key Press Debug ===")
        print(f"Key: {pygame.key.name(event.key)}")
        print(f"Current state: {self.state}")
            
        if self.state == "ROLL":
            if not self.current_player_is_ai and event.key in KEY_ROLL:
                return self.play_turn()
            elif event.key == pygame.K_q and not self.current_player_is_ai:
                confirm_exit = self.show_exit_confirmation()
                
                if confirm_exit:
                    current_player = self.logic.players[self.logic.current_player_index]
                    final_assets = self.calculate_player_assets(current_player)
                    result = self.handle_voluntary_exit(current_player['name'], final_assets)
                    if result:
                        self.board.add_message(f"{current_player['name']} has voluntarily exited the game")
                        self.show_notification(f"{current_player['name']} has voluntarily exited the game", 3000)
                        if len(self.logic.players) > 0:
                            self.state = "ROLL"
                        else:
                            return self.check_game_over()
                return False
            elif event.key == pygame.K_t and self.game_mode == "abridged":
                self.show_time_stats()
        elif self.state == "BUY":
            if event.key in KEY_BUY:
                self.handle_buy_decision(True)
                return False
            elif event.key in KEY_PASS:
                self.handle_buy_decision(False)
                return False
        elif self.state == "AUCTION":
            print("Processing auction input")
            self.handle_auction_input(event)
            return False
        
        if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]:
            dx, dy = 0, 0
            if event.key == pygame.K_LEFT:
                dx = 10
            elif event.key == pygame.K_RIGHT:
                dx = -10
            elif event.key == pygame.K_UP:
                dy = 10
            elif event.key == pygame.K_DOWN:
                dy = -10
            self.board.update_offset(dx, dy)
        
        self.board.camera.handle_camera_controls(pygame.key.get_pressed())
        return None

    def show_time_stats(self):
        if self.game_mode == "abridged" and self.time_limit:
            current_time = pygame.time.get_ticks()
            elapsed = (current_time - self.start_time) // 1000
            remaining = max(0, self.time_limit - elapsed)
            minutes = remaining // 60
            seconds = remaining % 60
            
            self.board.add_message(f"Time: {minutes:02d}:{seconds:02d}")
            
            min_rounds = min(self.rounds_completed.values())
            max_rounds = max(self.rounds_completed.values())
            if min_rounds != max_rounds:
                self.board.add_message(f"Rounds: {min_rounds}-{max_rounds}")

    def handle_bankruptcy(self, player):
        if self.logic.remove_player(player['name']):
            self.board.add_message(f"{player['name']} bankrupt!")
            self.board.update_ownership(self.logic.properties)
            return True
        return False

    def draw_auction(self, auction_data):
        if self.show_card:
            print("Card is showing - not drawing auction UI")
            return
            
        if auction_data is None:
            print("Warning: Auction data is None in draw_auction")
            self.state = "ROLL"  
            return
            
        required_keys = ["property", "current_bid", "minimum_bid", "highest_bidder", 
                         "current_bidder_index", "active_players"]
        
        for key in required_keys:
            if key not in auction_data:
                print(f"Warning: Auction data missing key '{key}' - resetting to ROLL state")
                self.state = "ROLL"
                return
        
        if not isinstance(auction_data["property"], dict) or "name" not in auction_data["property"]:
            print("Warning: Auction property data is invalid - resetting to ROLL state")
            self.state = "ROLL"
            return
        
        current_bidder_index = auction_data.get("current_bidder_index", 0)
        if (current_bidder_index < len(auction_data["active_players"])):
            current_bidder = auction_data["active_players"][current_bidder_index]
            if current_bidder.get('is_ai', False):
                ai_player = current_bidder
                print(f"Auto-handling AI auction turn for {ai_player['name']}")
                self.handle_ai_turn(ai_player)
                pygame.time.delay(500)
        
        print(f"\n=== Drawing Auction UI ===")
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
            
        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.35)
        card_height = int(window_size[1] * 0.5)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2
        
        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) 
        self.screen.blit(overlay, (0, 0))
        
        for i in range(5):
            shadow_offset = 6 - i
            shadow_rect = pygame.Rect(card_x + shadow_offset, card_y + shadow_offset, 
                                    card_width, card_height)
            shadow = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            shadow_alpha = 100 - (i * 20)
            pygame.draw.rect(shadow, (*BLACK, shadow_alpha), shadow.get_rect(), border_radius=15)
            self.screen.blit(shadow, shadow_rect)
        
        pygame.draw.rect(self.screen, WHITE, (card_x, card_y, card_width, card_height), border_radius=15)
        
        current_time = pygame.time.get_ticks()
        time_remaining = max(0, (auction_data["start_time"] + auction_data["duration"] - current_time) // 1000)
        
        current_bidder = auction_data["active_players"][auction_data["current_bidder_index"]]
        current_bidder_obj = next((p for p in self.players if p.name == current_bidder['name']), None)
        
        header_color = ERROR_COLOR if time_remaining <= 10 else ACCENT_COLOR
        header_text = self.font.render(f"{current_bidder['name']}'s Turn", True, header_color)
        timer_text = self.font.render(f"Time: {time_remaining}s", True, header_color)
        
        header_y = card_y + 20
        self.screen.blit(header_text, (card_x + 20, header_y))
        self.screen.blit(timer_text, (card_x + card_width - timer_text.get_width() - 20, header_y))
        
        title_y = header_y + 50
        title = self.font.render("AUCTION", True, BLACK)
        property_name = self.font.render(auction_data["property"]["name"], True, BLACK)
        self.screen.blit(title, (card_x + (card_width - title.get_width()) // 2, title_y))
        self.screen.blit(property_name, (card_x + 20, title_y + 40))
        
        info_y = title_y + 90
        current_bid = self.font.render(f"Current Bid: £{auction_data['current_bid']}", True, BLACK)
        min_bid = self.font.render(f"Minimum Bid: £{auction_data['minimum_bid']}", True, BLACK)
        self.screen.blit(current_bid, (card_x + 20, info_y))
        self.screen.blit(min_bid, (card_x + 20, info_y + 40))
        
        if auction_data["highest_bidder"]:
            highest_y = info_y + 80
            highest_text = self.font.render(f"Highest Bidder: {auction_data['highest_bidder']['name']}", True, SUCCESS_COLOR)
            self.screen.blit(highest_text, (card_x + 20, highest_y))
        
        can_bid = current_bidder['name'] not in auction_data.get("passed_players", set())
        is_human = current_bidder_obj and not current_bidder_obj.is_ai
        
        if is_human and can_bid:
            self.auction_input = pygame.Rect(card_x + 20, card_y + card_height - 120, 200, 40)
            pygame.draw.rect(self.screen, WHITE, self.auction_input)
            pygame.draw.rect(self.screen, ACCENT_COLOR, self.auction_input, 2)
            
            if self.auction_bid_amount:
                bid_text = self.font.render(self.auction_bid_amount, True, BLACK)
            else:
                bid_text = self.small_font.render("Enter bid amount...", True, GRAY)
            self.screen.blit(bid_text, (self.auction_input.x + 10, self.auction_input.y + (self.auction_input.height - bid_text.get_height()) // 2))
            
            button_width = 100
            button_height = 40
            button_margin = 20
            
            self.auction_buttons = {
                'bid': pygame.Rect(card_x + 20, card_y + card_height - 60, button_width, button_height),
                'pass': pygame.Rect(card_x + 20 + button_width + button_margin, card_y + card_height - 60, button_width, button_height)
            }
            
            mouse_pos = pygame.mouse.get_pos()
            for btn_name, btn_rect in self.auction_buttons.items():
                mouse_over = btn_rect.collidepoint(mouse_pos)
                color = BUTTON_HOVER if mouse_over else ACCENT_COLOR
                pygame.draw.rect(self.screen, color, btn_rect, border_radius=5)
                
                btn_text = self.font.render(btn_name.title(), True, WHITE)
                self.screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width()//2, 
                                        btn_rect.centery - btn_text.get_height()//2))
        
        if auction_data.get("passed_players"):
            passed_text = self.small_font.render("Passed: " + ", ".join(auction_data["passed_players"]), True, GRAY)
            self.screen.blit(passed_text, (card_x + 20, card_y + card_height - 30))

    def handle_auction_input(self, event):
        if not hasattr(self.logic, 'current_auction') or self.logic.current_auction is None:
            print("No active auction in handle_auction_input")
            return
        
        if self.show_card:
            print("Card is showing - ignoring auction input")
            return
            
        auction_data = self.logic.current_auction
        if "active_players" not in auction_data or not auction_data["active_players"]:
            print("No active players in auction - ignoring auction input")
            return
            
        if auction_data.get("completed", False):
            print("Auction is already completed - ignoring auction input")
            return
            
        if auction_data["current_bidder_index"] >= len(auction_data["active_players"]):
            print(f"Invalid current_bidder_index: {auction_data['current_bidder_index']} (active players: {len(auction_data['active_players'])})")
            return
            
        current_bidder = auction_data["active_players"][auction_data["current_bidder_index"]]
        current_bidder_obj = next((p for p in self.players if p.name == current_bidder['name']), None)
        
        print(f"Processing auction input for {current_bidder['name']}")
        
        if current_bidder.get('in_jail', False):
            self.board.add_message(f"{current_bidder['name']} cannot bid while in jail!")
            self.show_notification(f"{current_bidder['name']} cannot bid while in jail!", 2000)
            auction_data["passed_players"].add(current_bidder['name'])
            self.logic.move_to_next_bidder()
            return
            
        if current_bidder_obj and not current_bidder_obj.is_ai:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.auction_bid_amount = self.auction_bid_amount[:-1]
                    print(f"Backspace pressed - new bid amount: {self.auction_bid_amount}")
                
                elif event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                                 pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                    if len(self.auction_bid_amount) < 6:
                        self.auction_bid_amount += event.unicode
                        print(f"Number key pressed - new bid amount: {self.auction_bid_amount}")
                
                elif event.key == pygame.K_RETURN:
                    print(f"Enter key pressed - submitting bid: {self.auction_bid_amount}")
                    self._process_auction_bid(current_bidder)
                
                elif event.key == pygame.K_ESCAPE:
                    print(f"Escape key pressed - passing")
                    success, message = self.logic.process_auction_pass(current_bidder)
                    if message:
                        self.board.add_message(message)
                        self.show_notification(message, 2000)
                    if success:
                        print(f"{current_bidder['name']} passed successfully")
                    else:
                        print(f"Pass failed: {message}")
    
    def _process_auction_bid(self, current_bidder):
        try:
            bid_amount = int(self.auction_bid_amount or "0")
            success, message = self.logic.process_auction_bid(current_bidder, bid_amount)
            if message:
                self.board.add_message(message)
                self.show_notification(message, 2000)
            if success:
                self.auction_bid_amount = ""
                print(f"Bid successful: £{bid_amount}")
            else:
                print(f"Bid failed: {message}")
        except ValueError:
            self.board.add_message("Please enter a valid number!")
            self.show_notification("Please enter a valid number!", 2000)
            print("Invalid bid amount")

    def handle_auction_click(self, pos):
        print("\n=== Auction Click Debug ===")
        
        if not hasattr(self.logic, 'current_auction') or self.logic.current_auction is None:
            print("Error: No active auction")
            self.state = "ROLL"
            return True
            
        if self.show_card:
            print("Card is showing - ignoring auction click")
            return False
            
        auction_data = self.logic.current_auction
        
        if auction_data is None:
            print("Error: Auction data is None in handle_auction_click")
            self.state = "ROLL"
            return True
            
        if "active_players" not in auction_data or not auction_data["active_players"]:
            print("No active players in auction")
            self.state = "ROLL"
            return True
            
        if auction_data.get("completed", False):
            print("Auction is already marked as completed - changing state to ROLL")
            self.state = "ROLL"
            return True
        
        current_bidder = auction_data["active_players"][auction_data["current_bidder_index"]]
        current_bidder_obj = next((p for p in self.players if p.name == current_bidder['name']), None)
        
        print(f"Current bidder: {current_bidder['name']}")
        print(f"Is AI: {current_bidder_obj.is_ai if current_bidder_obj else 'Unknown'}")
        print(f"Current bid amount input: {self.auction_bid_amount}")
        
        print(f"Bid button rect: {self.auction_buttons['bid']}")
        print(f"Pass button rect: {self.auction_buttons['pass']}")
        print(f"Click position: {pos}")
        print(f"Bid button collision: {self.auction_buttons['bid'].collidepoint(pos)}")
        print(f"Pass button collision: {self.auction_buttons['pass'].collidepoint(pos)}")
        
        if not current_bidder_obj or current_bidder_obj.is_ai:
            print("Current bidder is AI or not found - ignoring click")
            return False
        
        if self.auction_buttons['bid'].collidepoint(pos):
            print(f"Bid button clicked by {current_bidder['name']}")
            try:
                bid_amount = int(self.auction_bid_amount or "0")
                success, message = self.logic.process_auction_bid(current_bidder, bid_amount)
                if message:
                    self.board.add_message(message)
                if success:
                    self.auction_bid_amount = ""
                    print(f"Bid successful: £{bid_amount}")
                else:
                    print(f"Bid failed: {message}")
            except ValueError:
                self.board.add_message("Please enter a valid number!")
                print("Invalid bid amount")
        
        elif self.auction_buttons['pass'].collidepoint(pos):
            print(f"Pass button clicked by {current_bidder['name']}")
            success, message = self.logic.process_auction_pass(current_bidder)
            if message:
                self.board.add_message(message)
            if success:
                print(f"{current_bidder['name']} passed successfully")
            else:
                print("Pass failed: {message}")
        
        result_message = self.logic.check_auction_end()
        print(f"Auction end check result: {result_message}")
        
        if result_message == "auction_completed":
            print("Auction is completed - showing results before changing state")
            
            if hasattr(self.logic, 'current_auction') and self.logic.current_auction:
                auction_data = self.logic.current_auction
                if auction_data and auction_data.get("highest_bidder"):
                    winner = auction_data["highest_bidder"]
                    property_name = auction_data["property"]["name"]
                    bid_amount = auction_data["current_bid"]
                    self.show_notification(f"{winner['name']} won {property_name} for £{bid_amount}", 3000)
                else:
                    property_name = auction_data["property"]["name"]
                    self.show_notification(f"No one bid on {property_name}", 3000)
            
            self.auction_end_time = pygame.time.get_ticks()
            self.auction_end_delay = 3000
            self.auction_completed = True
            
            self.board.update_ownership(self.logic.properties)
            return False
        
        print("Auction continues - returning False")
        return False

    def handle_game_over(self, winner_name):
        if self.game_over:
            return
            
        self.game_over = True
        if winner_name:
            for i, player in enumerate(self.players):
                if player.name == winner_name:
                    self.winner_index = i
                    player.set_winner(True)
                    self.board.add_message(f"*** {winner_name} wins! ***")
                    break

    def draw_jail_options(self, player):
        if not player.get('in_jail', False):
            return

        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.3)
        card_height = int(window_size[1] * 0.3)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2

        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  
        self.screen.blit(overlay, (0, 0))

        shadow = pygame.Surface((card_width + 10, card_height + 10), pygame.SRCALPHA)
        for i in range(5):
            alpha = int(100 * (1 - i/5))
            pygame.draw.rect(shadow, (*ERROR_COLOR[:3], alpha),
                           (i, i, card_width + 10 - i*2, card_height + 10 - i*2),
                           border_radius=15)
        self.screen.blit(shadow, (card_x - 5, card_y - 5))

        pygame.draw.rect(self.screen, WHITE, (card_x, card_y, card_width, card_height), border_radius=10)
        
        title_text = self.font.render("JAIL OPTIONS", True, ERROR_COLOR)
        title_rect = title_text.get_rect(centerx=card_x + card_width//2, top=card_y + 20)
        self.screen.blit(title_text, title_rect)

        options = []
        if self.logic.jail_free_cards.get(player['name'], 0) > 0:
            options.append(("[1] Use Get Out of Jail Free card", pygame.K_1))
        if player['money'] >= 50:
            options.append(("[2] Pay £50 fine", pygame.K_2))
        options.append(("[3] Try rolling doubles", pygame.K_3))

        title_height = 50
        y_offset = card_y + title_height + 20
        button_height = 40
        button_margin = 10
        mouse_pos = pygame.mouse.get_pos()

        for i, (option_text, key) in enumerate(options):
            button_rect = pygame.Rect(card_x + 20, y_offset, card_width - 40, button_height)
            is_hovered = button_rect.collidepoint(mouse_pos)
            
            pygame.draw.rect(self.screen, BUTTON_HOVER if is_hovered else ACCENT_COLOR, 
                           button_rect, border_radius=5)
            
            text = self.small_font.render(option_text, True, WHITE)
            text_rect = text.get_rect(center=button_rect.center)
            self.screen.blit(text, text_rect)
            
            y_offset += button_height + button_margin

        turns_text = self.small_font.render(f"Turns in jail: {player.get('jail_turns', 0)}/3", True, ERROR_COLOR)
        turns_rect = turns_text.get_rect(centerx=card_x + card_width//2, 
                                       bottom=card_y + card_height - 20)
        self.screen.blit(turns_text, turns_rect)

    def get_jail_choice(self, player):
        player_obj = next((p for p in self.players if p.name == player['name']), None)
        if player_obj and player_obj.is_ai:
            if self.logic.jail_free_cards.get(player['name'], 0) > 0:
                return "card"
            elif player['money'] >= 50 and random.random() < 0.5:
                return "pay"
            return "roll"

        if self.game_mode == "abridged" and self.check_time_limit():
            print("Time limit reached during jail choice - automatically returning 'roll'")
            return "roll"
            
        if player['money'] < 50 and not self.logic.jail_free_cards.get(player['name'], 0):
            self.show_notification("No options available - must try rolling doubles")
            return "roll"

        waiting = True
        choice = None
        self.show_notification("Choose how to get out of jail", 5000)
        
        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.3)
        card_height = int(window_size[1] * 0.3)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2
        
        button_height = 40
        button_margin = 10
        title_height = 50
        y_start = card_y + title_height + 20
        
        options = []
        if self.logic.jail_free_cards.get(player['name'], 0) > 0:
            options.append(("[1] Use Get Out of Jail Free card", "card"))
        if player['money'] >= 50:
            options.append(("[2] Pay £50 fine", "pay"))
        options.append(("[3] Try rolling doubles", "roll"))
        
        button_rects = []
        y_offset = y_start
        for option_text, option_value in options:
            button_rect = pygame.Rect(card_x + 20, y_offset, card_width - 40, button_height)
            button_rects.append((button_rect, option_value))
            y_offset += button_height + button_margin

        need_redraw = True
        last_redraw_time = 0
        last_click_time = 0
        
        while waiting:
            if self.game_mode == "abridged" and self.check_time_limit():
                print("Time limit reached during jail choice loop - breaking out")
                choice = "roll"
                break
                
            current_time = pygame.time.get_ticks()
            
            if current_time - last_redraw_time < 16:  
                pygame.time.delay(5)
                continue
                
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1 and self.logic.jail_free_cards.get(player['name'], 0) > 0:
                        choice = "card"
                        waiting = False
                    elif event.key == pygame.K_2 and player['money'] >= 50:
                        choice = "pay"
                        waiting = False
                    elif event.key == pygame.K_3:
                        choice = "roll"
                        waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if current_time - last_click_time < 300: 
                        continue
                    last_click_time = current_time
                    
                    mouse_pos = event.pos
                    for button_rect, option_value in button_rects:
                        if button_rect.collidepoint(mouse_pos):
                            if option_value == "card" and self.logic.jail_free_cards.get(player['name'], 0) > 0:
                                choice = "card"
                                waiting = False
                            elif option_value == "pay" and player['money'] >= 50:
                                choice = "pay"
                                waiting = False
                            elif option_value == "roll":
                                choice = "roll"
                                waiting = False
                elif event.type == pygame.MOUSEMOTION:
                    need_redraw = True
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            if need_redraw:
                self.draw()
                self.draw_jail_options(player)
                pygame.display.flip()
                need_redraw = False
                last_redraw_time = current_time

        return choice or "roll"

    def handle_jail_turn(self, player):
        if not player['in_jail']:
            return False

        player_obj = next((p for p in self.players if p.name == player['name']), None)
        if not player_obj:
            print(f"Warning: Could not find player object for {player['name']}")
            return False
            
        if player_obj.is_ai:
            if self.logic.jail_free_cards.get(player['name'], 0) > 0:
                card_type = player_obj.use_jail_card()
                if card_type == CardType.POT_LUCK:
                    self.pot_luck_deck.return_jail_card(card_type)
                else:
                    self.opportunity_deck.return_jail_card(card_type)
                player['in_jail'] = False
                player['jail_turns'] = 0
                self.board.add_message(f"{player['name']} used Get Out of Jail Free card!")
                self.show_notification(f"{player['name']} used Get Out of Jail Free card!", 2000)
                return True
            elif player['money'] >= 50 and random.random() < 0.5:
                player['money'] -= 50
                self.logic.free_parking_fund += 50
                self.synchronize_free_parking_pot() 
                player['in_jail'] = False
                player['jail_turns'] = 0
                self.board.add_message(f"{player['name']} paid £50 to get out of jail!")
                self.show_notification(f"{player['name']} paid £50 to get out of jail!", 2000)
                return True
        else:
            self.draw()
            pygame.display.flip()
            
            choice = self.get_jail_choice(player)
            
            if choice == "card" and self.logic.jail_free_cards.get(player['name'], 0) > 0:
                card_type = player_obj.use_jail_card()
                if card_type == CardType.POT_LUCK:
                    self.pot_luck_deck.return_jail_card(card_type)
                else:
                    self.opportunity_deck.return_jail_card(card_type)
                player['in_jail'] = False
                player['jail_turns'] = 0
                self.board.add_message(f"{player['name']} used Get Out of Jail Free card!")
                self.show_notification(f"{player['name']} used Get Out of Jail Free card!", 2000)
                return True
            elif choice == "pay" and player['money'] >= 50:
                player['money'] -= 50
                self.logic.free_parking_fund += 50
                self.synchronize_free_parking_pot() 
                player['in_jail'] = False
                player['jail_turns'] = 0
                self.board.add_message(f"{player['name']} paid £50 to get out of jail!")
                self.show_notification(f"{player['name']} paid £50 to get out of jail!", 2000)
                return True

        player['jail_turns'] = player.get('jail_turns', 0) + 1
        if player['jail_turns'] >= 3:
            if player['money'] >= 50:
                player['money'] -= 50
                self.logic.free_parking_fund += 50
                self.synchronize_free_parking_pot() 
                self.board.add_message(f"{player['name']} paid £50 after 3 turns in jail!")
                self.show_notification(f"{player['name']} paid £50 after 3 turns in jail!", 2000)
            else:
                self.board.add_message(f"{player['name']} couldn't pay jail fine!")
                self.show_notification(f"{player['name']} couldn't pay jail fine!", 2000)
                self.handle_bankruptcy(player)
            player['in_jail'] = False
            player['jail_turns'] = 0
            return True
            
        return False

    def show_notification(self, text, duration=None):
        self.notification = text
        self.notification_time = pygame.time.get_ticks()
        if duration:
            self.NOTIFICATION_DURATION = duration

    def draw_notification(self):
        if not self.notification:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.notification_time > self.NOTIFICATION_DURATION:
            self.notification = None
            return

        window_size = self.screen.get_size()
        padding = 20
        
        notification_text = self.font.render(self.notification, True, WHITE)
        bg_width = notification_text.get_width() + padding * 2
        bg_height = notification_text.get_height() + padding * 2
        bg_surface = pygame.Surface((bg_width, bg_height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, (*ACCENT_COLOR[:3], 230), bg_surface.get_rect(), border_radius=10)
        
        for i in range(3):
            alpha = 100 - i * 30
            pygame.draw.rect(bg_surface, (*ACCENT_COLOR[:3], alpha), 
                           (-i, -i, bg_width + i*2, bg_height + i*2), 
                           border_radius=10)

        x = (window_size[0] - bg_width) // 2
        y = 20  
        
        self.screen.blit(bg_surface, (x, y))
        self.screen.blit(notification_text, (x + padding, y + padding))

    def draw_card_alert(self, card, player):
        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.4)
        card_height = int(window_size[1] * 0.3)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2
        
        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))
        
        shadow_rect = pygame.Rect(card_x + 6, card_y + 6, card_width, card_height)
        shadow = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, shadow_rect)
        
        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, WHITE, card_rect, border_radius=15)
        
        header_height = 60
        header_rect = pygame.Rect(card_x, card_y, card_width, header_height)
        pygame.draw.rect(self.screen, ACCENT_COLOR, header_rect, border_radius=15)
        pygame.draw.rect(self.screen, ACCENT_COLOR, 
                       pygame.Rect(card_x, card_y + header_height - 15, card_width, 15))
        
        header_text = self.font.render(card['type'], True, WHITE)
        header_shadow = self.font.render(card['type'], True, BLACK)
        header_rect = header_text.get_rect(center=(card_x + card_width//2, card_y + header_height//2))
        shadow_rect = header_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        self.screen.blit(header_shadow, shadow_rect)
        self.screen.blit(header_text, header_rect)
        
        player_y = card_y + header_height + 20
        player_text = self.font.render(f"Player: {player['name']}", True, BLACK)
        self.screen.blit(player_text, (card_x + 20, player_y))
        
        message_y = player_y + 40
        message_lines = self.wrap_text(card['message'], card_width - 40)
        for i, line in enumerate(message_lines):
            message_text = self.small_font.render(line, True, BLACK)
            self.screen.blit(message_text, (card_x + 20, message_y + i * 30))
            
        continue_y = card_y + card_height - 40
        continue_text = self.small_font.render("Tap or click to continue...", True, GRAY)
        continue_rect = continue_text.get_rect(centerx=card_x + card_width//2, bottom=continue_y)
        self.screen.blit(continue_text, continue_rect)
        
    def wrap_text(self, text, max_width):
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.small_font.render(test_line, True, BLACK)
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines

    def handle_card_action(self, card, player):
        print(f"Processing card action: {card.text} for player {player['name']}")
        
        self.show_card = True
        self.current_card = {
            'type': card.card_type.name,
            'message': card.text
        }
        self.current_card_player = player
        self.card_display_time = pygame.time.get_ticks()
        
        self.board.add_message(f"{player['name']} - {card.card_type.name}: {card.text}")
        
        pygame.event.clear()
        waiting = True
        while waiting:
            self.draw()
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN]:
                    waiting = False
                    self.show_card = False
                    self.current_card = None
                    self.current_card_player = None
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            pygame.time.wait(30)

        result = card.action(player, self)
        
        if "jail free" in card.text.lower():
            self.show_notification(f"{player['name']} received a Get Out of Jail Free card!", 3000)
        elif "collect" in card.text.lower():
            self.show_notification(f"{player['name']} collected money!", 2000)
        elif "pay" in card.text.lower():
            self.show_notification(f"{player['name']} paid money!", 2000)
        elif "advance" in card.text.lower() or "go to" in card.text.lower():
            self.show_notification(f"{player['name']} is moving!", 2000)
            
        return result

    def draw_popup_message(self):
        window_size = self.screen.get_size()
        
        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        popup_width = int(window_size[0] * 0.4)
        popup_height = int(window_size[1] * 0.25)
        popup_x = (window_size[0] - popup_width) // 2
        popup_y = (window_size[1] - popup_height) // 2
        
        shadow_offset = 4
        shadow = pygame.Surface((popup_width, popup_height))
        shadow.fill(BLACK)
        self.screen.blit(shadow, (popup_x + shadow_offset, popup_y + shadow_offset))
        
        pygame.draw.rect(self.screen, WHITE, (popup_x, popup_y, popup_width, popup_height))
        pygame.draw.rect(self.screen, ACCENT_COLOR, (popup_x, popup_y, popup_width, popup_height), 2)
        
        if self.popup_title:
            title_surface = self.font.render(self.popup_title, True, ACCENT_COLOR)
            title_rect = title_surface.get_rect(centerx=popup_x + popup_width//2, top=popup_y + 20)
            self.screen.blit(title_surface, title_rect)
            
        if self.popup_message:
            words = self.popup_message.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                test_surface = self.small_font.render(test_line, True, BLACK)
                if test_surface.get_width() <= popup_width - 40:
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            
            y_offset = popup_y + 80
            for line in lines:
                text_surface = self.small_font.render(line, True, BLACK)
                text_rect = text_surface.get_rect(centerx=popup_x + popup_width//2, top=y_offset)
                self.screen.blit(text_surface, text_rect)
                y_offset += 30
        
        button_width = 100
        button_height = 40
        button_x = popup_x + (popup_width - button_width) // 2
        button_y = popup_y + popup_height - 60
        
        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        button_color = BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else ACCENT_COLOR
        
        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=5)
        button_text = self.small_font.render("OK", True, WHITE)
        text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, text_rect)

    def show_card_popup(self, card_type, message):
        self.show_card = True
        self.current_card = {
            'type': card_type,
            'message': message
        }
        self.current_card_player = self.logic.players[self.logic.current_player_index]
        self.card_display_time = pygame.time.get_ticks()
        
        self.board.add_message(f"{self.current_card_player['name']} - {card_type}: {message}")
        
        print(f"Showing card popup: {card_type} - {message}")

    def handle_card_draw(self, player, card_type):
        self.show_card_popup(card_type, f"{player['name']} drew a {card_type} card")
        
        result = self.logic.handle_card_draw(player, card_type)
        
        return result

    def check_one_player_remains(self):
        active_player_objects = [p for p in self.players if not p.bankrupt and not p.voluntary_exit]
        active_player_data = [p for p in self.logic.players if p["money"] > 0 and not p.get('exited', False)]
        
        if len(active_player_objects) == 1 and len(active_player_data) == 1:
            if active_player_objects[0].is_ai:
                self.game_over = True
                winner = active_player_objects[0]
                self.handle_game_over(winner.name)
                return True
            return True
        
        return len(active_player_objects) <= 1 and len(active_player_data) <= 1
        
    def check_time_limit(self):
        if not self.time_limit or not self.start_time:
            return False
        
        current_time = pygame.time.get_ticks()
        
        elapsed_time_ms = current_time - self.start_time - self.total_pause_time
        if self.game_paused:
            current_pause_duration = current_time - self.pause_start_time
            elapsed_time_ms -= current_pause_duration
            
        time_limit_ms = self.time_limit * 1000
        
        if elapsed_time_ms >= time_limit_ms:
            if not hasattr(self, '_time_limit_notified') or not self._time_limit_notified:
                minutes = self.time_limit // 60
                print(f"\n\n!!!TIME LIMIT REACHED!!!: {minutes} minutes have elapsed!")
                print("Game will end after all players complete their current lap...")
                
                self.show_notification(f"TIME'S UP! Game will end after this lap.", 5000)
                
                if self.state == "AUCTION" and hasattr(self.logic, 'current_auction') and self.logic.current_auction:
                    print("Time limit reached during auction - canceling auction")
                    if isinstance(self.logic.current_auction, dict) and 'property' in self.logic.current_auction:
                        property_name = self.logic.current_auction.get('property', {}).get('name', 'Unknown')
                        print(f"Auction for {property_name} canceled due to time limit")
                    self.logic.current_auction = None
                
                print("Clearing UI states to continue the game...")
                self.state = "ROLL"  
                self.auction_data = None  
                self.jail_options_visible = False  
                self.confirmation_dialog_visible = False 
                self.popup_message = None  
                self.card_alert_visible = False  
                self.development_ui_visible = False  
                
                self._time_limit_notified = True
                self.time_limit_reached = True
                
                self.final_lap = {}
                for player_name, lap in self.lap_count.items():
                    player_obj = next((p for p in self.players if p.name == player_name), None)
                    if player_obj and not player_obj.bankrupt and not player_obj.voluntary_exit:
                        self.final_lap[player_name] = lap
                
                print("\n===== CURRENT GAME STATE =====")
                print(f"Active players: {len([p for p in self.players if not p.bankrupt and not p.voluntary_exit])}")
                print(f"Current lap counts: {self.final_lap}")
                print("Game will end after all players complete their current lap")
                
                print("\nCurrent Player Assets:")
                try:
                    for logic_player in self.logic.players:
                        player_name = logic_player['name']
                        player_obj = next((p for p in self.players if p.name == player_name), None)
                        
                        if player_obj and player_obj.voluntary_exit:
                            assets = player_obj.final_assets
                            status = "Voluntarily Exited"
                        elif player_obj and player_obj.bankrupt:
                            assets = 0
                            status = "Bankrupt"
                        else:
                            try:
                                assets = self.calculate_player_assets(logic_player)
                                status = "Active"
                            except Exception as e:
                                print(f"Error calculating assets for {player_name}: {e}")
                                assets = logic_player.get('money', 0)
                                status = "Active (Fallback)"
                        
                        print(f"  {player_name}: £{assets} ({status})")
                        print(f"  Lap count: {self.lap_count.get(player_name, 0)}")
                except Exception as e:
                    print(f"Error listing player assets: {e}")
                print("============================\n")
            
            if hasattr(self, 'final_lap'):
                all_completed = True
                active_players = [p.name for p in self.players if not p.bankrupt and not p.voluntary_exit]
                
                for player_name in active_players:
                    if player_name in self.final_lap:
                        current_lap = self.lap_count.get(player_name, 0)
                        final_lap = self.final_lap.get(player_name, 0)
                        
                        if current_lap <= final_lap:
                            all_completed = False
                            print(f"Waiting for {player_name} to complete their turn (lap {current_lap}, final lap {final_lap})")
                            break
                
                if all_completed:
                    print("All players have completed their final lap - ending game")
                    self.game_over = True
                    return True
                else:
                    return False
            
            return False
        
        return False
        
    def end_full_game(self):
        active_players = [p for p in self.players if not p.bankrupt and not p.voluntary_exit]
        winner = active_players[0] if active_players else None
        
        final_assets = {}
        
        for logic_player in self.logic.players:
            player_name = logic_player['name']
            player_obj = next((p for p in self.players if p.name == player_name), None)
            
            if player_obj and player_obj.voluntary_exit:
                final_assets[player_name] = player_obj.final_assets
            else:
                final_assets[player_name] = self.calculate_player_assets(logic_player)
        
        print(f"End full game assets: {final_assets}")
        
        return {
            "winner": winner.name if winner else "No winner",
            "final_assets": final_assets,
            "bankrupted_players": [p.name for p in self.players if p.bankrupt],
            "voluntary_exits": [p.name for p in self.players if p.voluntary_exit],
            "tied_winners": []
        }
        
    def end_abridged_game(self):
        self.auction_data = None
        self.jail_options_visible = False
        self.confirmation_dialog_visible = False
        self.popup_message = None
        self.card_alert_visible = False
        self.development_ui_visible = False
        self.state = "ROLL"
        self.game_over = True
        
        final_assets = {}
        
        for logic_player in self.logic.players:
            player_name = logic_player['name']
            player_obj = next((p for p in self.players if p.name == player_name), None)
            
            if player_obj and player_obj.voluntary_exit:
                final_assets[player_name] = player_obj.final_assets
            else:
                final_assets[player_name] = self.calculate_player_assets(logic_player)
        
        active_players = [p for p in self.players if not p.bankrupt and not p.voluntary_exit]
        
        if active_players:
            active_player_assets = {p.name: final_assets.get(p.name, 0) for p in active_players}
            
            if active_player_assets:
                max_assets = max(active_player_assets.values()) if active_player_assets else 0
                players_with_max_assets = [name for name, assets in active_player_assets.items() if assets == max_assets]
                
                if len(players_with_max_assets) > 1:
                    winner_name = "Tie"
                    tied_winners = players_with_max_assets
                else:
                    winner_name = players_with_max_assets[0] if players_with_max_assets else "No winner"
                    tied_winners = []
            else:
                winner_name = "No winner"
                tied_winners = []
        else:
            winner_name = "No winner"
            tied_winners = []
        
        print(f"End game assets: {final_assets}")
        print(f"Winner: {winner_name}")
        print(f"Tied winners: {tied_winners}")
        
        return {
            "winner": winner_name,
            "final_assets": final_assets,
            "bankrupted_players": [p.name for p in self.players if p.bankrupt],
            "voluntary_exits": [p.name for p in self.players if p.voluntary_exit],
            "tied_winners": tied_winners,
            "lap_count": self.lap_count 
        }
        
    def calculate_player_assets(self, player):
        try:
            if not player or not isinstance(player, dict):
                print(f"Warning: Invalid player object in calculate_player_assets: {player}")
                return 0
                
            total = player.get('money', 0)
            
            if not hasattr(self.logic, 'properties') or not self.logic.properties:
                print("Warning: No properties found in game logic")
                return total
                
            for prop_id, prop in self.logic.properties.items():
                if not isinstance(prop, dict):
                    continue
                    
                if prop.get('owner') == player.get('name'):
                    total += prop.get('price', 0)
                    
                    if 'houses' in prop and prop['houses'] > 0:
                        house_costs = prop.get('house_costs', [])
                        
                        if isinstance(house_costs, list) and house_costs:
                            houses_count = min(prop['houses'], len(house_costs))
                            for i in range(houses_count):
                                total += house_costs[i]
                        elif isinstance(house_costs, (int, float)):
                            total += house_costs * prop['houses']
            
            return total
            
        except Exception as e:
            print(f"Error in calculate_player_assets: {e}")
            return player.get('money', 0)
        
    def handle_voluntary_exit(self, player_name, final_assets):
        print(f"\n=== Voluntary Exit Debug ===")
        print(f"Player {player_name} is exiting the game")
        
        logic_player = next((p for p in self.logic.players if p['name'] == player_name), None)
        if logic_player:
            actual_final_assets = self.calculate_player_assets(logic_player)
            print(f"Final assets calculated from game logic: {actual_final_assets}")
        else:
            actual_final_assets = final_assets
            print(f"Using provided final assets: {final_assets}")
        
        print(f"Current number of players: {len(self.logic.players)}")
        print(f"Current player index before exit: {self.logic.current_player_index}")
        
        self.board.add_message(f"{player_name} exits game")
        
        player_obj = next((p for p in self.players if p.name == player_name), None)
        if not player_obj:
            print(f"Error: Could not find player object for {player_name}")
            return False
            
        print(f"Found player object: {player_obj.name}")
        
        player_properties = [p for p in self.logic.properties.values() 
                           if p.get('owner') == player_name]
        print(f"Player has {len(player_properties)} properties that will be returned to bank")
        
        if hasattr(player_obj, 'handle_voluntary_exit'):
            print(f"Setting voluntary_exit flag for {player_name}")
            player_obj.final_assets = actual_final_assets
            player_obj.handle_voluntary_exit()
        
        result = self.logic.remove_player(player_name, voluntary=True)
        print(f"Game logic marked player as exited: {result}")
        
        if result:
            exited_player = next((p for p in self.logic.players if p['name'] == player_name), None)
            if exited_player and exited_player.get('exited', False):
                print(f"Player {player_name} successfully marked as exited")
            else:
                print(f"Warning: Player {player_name} not properly marked as exited")
            
            self.board.update_ownership(self.logic.properties)
            
            active_players = [p for p in self.logic.players if not p.get('exited', False)]
            print(f"Active players after exit: {[p['name'] for p in active_players]}")
            
            next_player_found = False
            original_index = self.logic.current_player_index
            
            while not next_player_found and active_players:
                self.logic.current_player_index = (self.logic.current_player_index + 1) % len(self.logic.players)
                
                if self.logic.current_player_index == original_index:
                    break
                
                current_player = self.logic.players[self.logic.current_player_index]
                if not current_player.get('exited', False):
                    next_player_found = True
                    print(f"Next active player: {current_player['name']} (index: {self.logic.current_player_index})")
            
            print(f"Current player index after exit: {self.logic.current_player_index}")
            
            if len(active_players) <= 1:
                print(f"Only {len(active_players)} active player(s) left - game should end soon")
                if self.check_one_player_remains():
                    print("Game ending due to only one player remaining")
                    game_over_data = self.end_full_game()
                    return game_over_data
                
            self.show_notification(f"{player_name} has left the game. Their properties return to the bank.", 3000)
            
            self.state = "ROLL"
            print("Checking if next player is an AI...")
            self.check_and_trigger_ai_turn()
            
            return True
        else:
            print("Failed to mark player as exited in game logic")
            return False

    def move_player(self, player, spaces):
        try:
            if not isinstance(player.position, int) or not (1 <= player.position <= 40):
                print(f"Warning: Invalid position {player.position} detected for {player.name} in move_player, resetting to position 1")
                player.position = 1
                
            old_position = player.position
            
            if not isinstance(spaces, int):
                print(f"Warning: Invalid spaces value {spaces} for {player.name}, defaulting to 0")
                spaces = 0
            elif spaces < 0 or spaces > 40:
                print(f"Warning: Spaces value {spaces} out of range for {player.name}, adjusting to valid range")
                spaces = max(0, min(spaces, 40))
                
            new_position = (old_position + spaces) % 40
            if new_position == 0:
                new_position = 40
                
            if not (1 <= new_position <= 40):
                print(f"Warning: Invalid new position {new_position} calculated for {player.name}, correcting")
                new_position = max(1, min(new_position, 40))
            
            print(f"Player.move: {player.name} from {old_position} to {new_position} ({spaces} steps)")
            
            path = []
            for i in range(1, spaces + 1):
                step_pos = (old_position + i) % 40
                if step_pos == 0:
                    step_pos = 40
                path.append(step_pos)
                
            if path:
                print(f"Generated move path for {player.name}: {path}")
            
            player.start_move(path)
            
            found = False
            for logic_player in self.logic.players:
                if logic_player['name'] == player.name:
                    logic_player['position'] = new_position
                    found = True
                    break
                    
            if not found:
                print(f"Warning: Could not find logic player for {player.name} during move_player")
                
            return new_position
        except Exception as e:
            print(f"Error in move_player: {e}")
            return player.position

    def wait_for_animations(self):
        any_player_moving = any(player.is_moving for player in self.players)
        
        if not any_player_moving:
            return
            
        print(f"Animations in progress, delaying game state progression")
        
        for player in self.players:
            if player.is_moving:
                player.update_animation()
                
        self.draw()
        pygame.display.flip()
                
        self.waiting_for_animation = True

    def check_passing_go(self, player, old_position):
        new_position = player.position
        
        if new_position < old_position and not self.logic.is_going_to_jail:
            player_dict = next(p for p in self.logic.players if p['name'] == player.name)
            player_dict['money'] += 200
            self.logic.bank_money -= 200
            self.board.add_message(f"{player.name} collected £200 for passing GO")

    def synchronize_player_positions(self):
        try:
            for player in self.players:
                if player.bankrupt or player.voluntary_exit:
                    continue
                    
                if not isinstance(player.position, int) or not (1 <= player.position <= 40):
                    print(f"Fixing invalid position {player.position} for {player.name} in player object")
                    player.position = 1 
                
            for logic_player in self.logic.players:
                if not isinstance(logic_player.get('position'), int) or not (1 <= logic_player.get('position', 0) <= 40):
                    print(f"Fixing invalid position {logic_player.get('position')} for {logic_player['name']} in game logic")
                    logic_player['position'] = 1 
                    
            for player in self.players:
                if player.bankrupt or player.voluntary_exit:
                    continue
                    
                found = False
                for logic_player in self.logic.players:
                    if player.name == logic_player['name']:
                        found = True
                        
                        if player.position != logic_player['position']:
                            print(f"Position mismatch for {player.name}: Player object: {player.position}, Game logic: {logic_player['position']}")
                            
                            if player.is_ai:
                                old_pos = player.position
                                player.position = logic_player['position']
                                print(f"Correcting position mismatch for AI {player.name}: Player object: {old_pos} -> {logic_player['position']}")
                            else:
                                if abs(player.position - logic_player['position']) <= 3:
                                    old_pos = logic_player['position']
                                    logic_player['position'] = player.position
                                    print(f"Correcting position mismatch for human {player.name}: Game logic: {old_pos} -> {player.position}")
                                else:
                                    print(f"Large position discrepancy detected for {player.name} - monitoring")
                        
                        break
                        
                if not found and not player.bankrupt and not player.voluntary_exit:
                    print(f"Warning: Player {player.name} exists in UI but not in game logic")
                    
            for logic_player in self.logic.players:
                found = False
                for player in self.players:
                    if logic_player['name'] == player.name:
                        found = True
                        break
                        
                if not found:
                    print(f"Warning: Player {logic_player['name']} exists in game logic but not in UI")
        except Exception as e:
            print(f"Error in synchronize_player_positions: {e}")

    def handle_ai_turn(self, ai_player):
        MAX_ITERATIONS = 100
        iteration_count = 0
        
        try:
            player_obj = next((player for player in self.players if player.name == ai_player['name']), None)
                
            if not player_obj:
                print(f"Error: Could not find player object for AI {ai_player['name']}")
                return None
                
            if not player_obj.is_ai:
                print(f"Error: Player {ai_player['name']} is not an AI player")
                return None
                
            player_pos_valid = isinstance(player_obj.position, int) and 1 <= player_obj.position <= 40
            logic_pos_valid = isinstance(ai_player.get('position'), int) and 1 <= ai_player.get('position', 0) <= 40
                
            if not player_pos_valid and logic_pos_valid:
                print(f"Warning: Invalid position {player_obj.position} detected for AI {player_obj.name}, fixing from game logic")
                player_obj.position = ai_player['position']
            elif player_pos_valid and not logic_pos_valid:
                print(f"Warning: Invalid position {ai_player.get('position')} in game logic for AI {player_obj.name}, fixing from player object")
                ai_player['position'] = player_obj.position
            elif not player_pos_valid and not logic_pos_valid:
                print(f"Warning: Both positions invalid for {player_obj.name}, resetting to position 1")
                player_obj.position = 1
                ai_player['position'] = 1
            elif player_obj.position != ai_player['position']:

                print(f"Synchronizing position for AI {player_obj.name}: Player object: {player_obj.position}, Game logic: {ai_player['position']}")
                player_obj.position = ai_player['position']
        except Exception as e:
            print(f"Error handling AI turn: {e}")
            return None
        
   
        if self.state == "ROLL":
            self.play_turn()
            

            start_time = pygame.time.get_ticks()
            while self.state == "BUY" and self.current_property:

                current_time = pygame.time.get_ticks()
                if current_time - start_time > 5000:  
                    print(f"Timeout reached for AI {ai_player['name']} in BUY state - forcing decision")
                    self.handle_buy_decision(False)  
                    break
                    
                iteration_count += 1
                if iteration_count > MAX_ITERATIONS:
                    print(f"Maximum iterations reached for AI {ai_player['name']} in BUY state - forcing decision")
                    self.handle_buy_decision(False)
                    break
                
                print(f"\n=== AI Purchase Decision ===")
                print(f"AI Player: {ai_player['name']}")
                print(f"Property: {self.current_property['name']}")
                print(f"Price: £{self.current_property['price']}")
                print(f"AI Money: £{ai_player['money']}")
                
                try:
                    should_buy = self.logic.ai_player.should_buy_property(
                        self.current_property, 
                        ai_player['money'], 
                        [p for p in self.logic.properties.values() if p.get('owner') == ai_player['name']]
                    )
                    
                    if should_buy:
                        print("AI Decision: Buy")
                        self.handle_buy_decision(True)
                    else:
                        print("AI Decision: Pass")
                        self.handle_buy_decision(False)
                except Exception as e:
                    print(f"Error in AI purchase decision: {e}")
                    self.handle_buy_decision(False)
                break  
        
        elif self.state == "AUCTION" and hasattr(self.logic, 'current_auction'):
            auction_data = self.logic.current_auction
            
            if auction_data is None:
                print("Warning: Auction data is None in handle_ai_turn")
                return None
            
            start_time = pygame.time.get_ticks()
            while auction_data["active_players"][auction_data["current_bidder_index"]]['name'] == ai_player['name']:
                current_time = pygame.time.get_ticks()
                if current_time - start_time > 5000: 
                    print(f"Timeout reached for AI {ai_player['name']} in AUCTION state - forcing pass")
                    success, message = self.logic.process_auction_pass(ai_player)
                    if message:
                        self.board.add_message(message)
                    break
                    
                iteration_count += 1
                if iteration_count > MAX_ITERATIONS:
                    print(f"Maximum iterations reached for AI {ai_player['name']} in AUCTION state - forcing pass")
                    success, message = self.logic.process_auction_pass(ai_player)
                    if message:
                        self.board.add_message(message)
                    break
                
                print(f"\n=== AI Auction Turn ===")
                print(f"AI Player: {ai_player['name']}")
                print(f"Property: {auction_data['property']['name']}")
                print(f"Current bid: £{auction_data['current_bid']}")
                print(f"Minimum bid: £{auction_data['minimum_bid']}")
                
                if ai_player['name'] in auction_data.get("passed_players", set()):
                    print(f"AI {ai_player['name']} has already passed")
                    break
                
                try:
                    bid_amount = self.logic.get_ai_auction_bid(ai_player, auction_data['property'], auction_data['current_bid'])
                    
                    if bid_amount and bid_amount >= auction_data['minimum_bid']:
                        print(f"AI Decision: Bid £{bid_amount}")
                        success, message = self.logic.process_auction_bid(ai_player, bid_amount)
                        if message:
                            self.board.add_message(message)
                    else:
                        print("AI Decision: Pass")
                        success, message = self.logic.process_auction_pass(ai_player)
                        if message:
                            self.board.add_message(message)
                except Exception as e:
                    print(f"Error in AI auction decision: {e}")
                    success, message = self.logic.process_auction_pass(ai_player)
                    if message:
                        self.board.add_message(message)
                
                result_message = self.logic.check_auction_end()
                if result_message:
                    self.board.add_message(result_message)
                    self.state = "ROLL"
                    self.board.update_ownership(self.logic.properties)
                break 
                
        return None

    def draw_development_ui(self, property_data):
        print("\n=== Property Development Debug ===")
        print(f"Drawing development UI for {property_data.get('name', 'Unknown')}")
        
        if not property_data:
            print("Warning: Property data is None in draw_development_ui")
            return
        
        current_player = self.logic.players[self.logic.current_player_index]
        player_obj = next((p for p in self.players if p.name == current_player['name']), None)
        
        if player_obj and player_obj.is_ai:
            print(f"Auto-handling development decision for AI player {current_player['name']}")
            self.state = "ROLL"
            self.selected_property = None
            self.development_mode = False
            return
        
        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.35)
        card_height = int(window_size[1] * 0.5)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2
        
        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        
        shadow_rect = pygame.Rect(card_x + 6, card_y + 6, card_width, card_height)
        shadow = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, shadow_rect)
        
        pygame.draw.rect(self.screen, WHITE, (card_x, card_y, card_width, card_height), border_radius=15)
        
        current_player = self.logic.players[self.logic.current_player_index]
        
        header_text = self.font.render(f"Develop {property_data['name']}", True, ACCENT_COLOR)
        self.screen.blit(header_text, (card_x + 20, card_y + 20))
        
        y_offset = card_y + 70
        padding = 20
        
        price_text = self.font.render(f"Price: £{property_data['price']}", True, BLACK)
        self.screen.blit(price_text, (card_x + padding, y_offset))
        y_offset += 35
        
        houses = property_data.get('houses', 0)
        house_text = self.font.render(f"Houses: {houses if houses < 5 else '0 (Hotel)'}", True, BLACK)
        self.screen.blit(house_text, (card_x + padding, y_offset))
        y_offset += 35
        
        hotel_status = "Yes" if houses == 5 else "No"
        hotel_text = self.font.render(f"Hotel: {hotel_status}", True, BLACK)
        self.screen.blit(hotel_text, (card_x + padding, y_offset))
        y_offset += 50
        
        button_width = card_width - 40
        button_height = 40
        button_margin = 10
        
        self.development_buttons = {}
        
        house_cost = property_data.get('house_cost', 0)
        can_build_house = False
        can_build_hotel = False
        
        if houses < 4:
            can_build_house, error = self.logic.can_build_house(property_data, current_player)
            upgrade_text = f"Upgrade (-£{house_cost})"
            upgrade_color = ACCENT_COLOR if can_build_house else GRAY
        else:
            can_build_hotel, error = self.logic.can_build_hotel(property_data, current_player)
            upgrade_text = f"Build Hotel (-£{house_cost})"
            upgrade_color = ACCENT_COLOR if can_build_hotel else GRAY
        
        self.development_buttons['upgrade'] = pygame.Rect(
            card_x + 20, y_offset, button_width, button_height
        )
        mouse_pos = pygame.mouse.get_pos()
        hover = self.development_buttons['upgrade'].collidepoint(mouse_pos) and (can_build_house or can_build_hotel)
        color = BUTTON_HOVER if hover else upgrade_color
        pygame.draw.rect(self.screen, color, self.development_buttons['upgrade'], border_radius=5)
        
        btn_text = self.small_font.render(upgrade_text, True, WHITE)
        text_rect = btn_text.get_rect(center=self.development_buttons['upgrade'].center)
        self.screen.blit(btn_text, text_rect)
        y_offset += button_height + button_margin
        
        self.development_buttons['auction'] = pygame.Rect(
            card_x + 20, y_offset, button_width, button_height
        )
        hover = self.development_buttons['auction'].collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, BUTTON_HOVER if hover else ACCENT_COLOR, 
                       self.development_buttons['auction'], border_radius=5)
        
        btn_text = self.small_font.render("Auction to Player", True, WHITE)
        text_rect = btn_text.get_rect(center=self.development_buttons['auction'].center)
        self.screen.blit(btn_text, text_rect)
        y_offset += button_height + button_margin
        
        mortgage_value = property_data.get('price', 0) // 2
        is_mortgaged = property_data.get('is_mortgaged', False)
        
        if is_mortgaged:
            unmortgage_cost = int(mortgage_value * 1.1)
            can_unmortgage = current_player['money'] >= unmortgage_cost
            mortgage_text = f"Unmortgage (-£{unmortgage_cost})" if can_unmortgage else "Cannot Unmortgage"
            mortgage_color = ACCENT_COLOR if can_unmortgage else GRAY
        else:
            can_mortgage = property_data.get('houses', 0) == 0
            mortgage_text = f"Mortgage (+£{mortgage_value})" if can_mortgage else "Cannot Mortgage"
            mortgage_color = ACCENT_COLOR if can_mortgage else GRAY
        
        self.development_buttons['mortgage'] = pygame.Rect(
            card_x + 20, y_offset, button_width, button_height
        )
        
        if is_mortgaged:
            hover = self.development_buttons['mortgage'].collidepoint(mouse_pos) and can_unmortgage
        else:
            hover = self.development_buttons['mortgage'].collidepoint(mouse_pos) and can_mortgage
            
        color = BUTTON_HOVER if hover else mortgage_color
        pygame.draw.rect(self.screen, color, self.development_buttons['mortgage'], border_radius=5)
        
        btn_text = self.small_font.render(mortgage_text, True, WHITE)
        text_rect = btn_text.get_rect(center=self.development_buttons['mortgage'].center)
        self.screen.blit(btn_text, text_rect)
        y_offset += button_height + button_margin
        
        can_sell = houses > 0
        sell_value = house_cost // 2
        sell_text = f"Sell House (+£{sell_value})" if houses > 0 and houses < 5 else f"Sell Hotel (+£{sell_value * 5})" if houses == 5 else "Nothing to Sell"
        
        self.development_buttons['sell'] = pygame.Rect(
            card_x + 20, y_offset, button_width, button_height
        )
        hover = self.development_buttons['sell'].collidepoint(mouse_pos) and can_sell
        color = BUTTON_HOVER if hover else (ACCENT_COLOR if can_sell else GRAY)
        pygame.draw.rect(self.screen, color, self.development_buttons['sell'], border_radius=5)
        
        btn_text = self.small_font.render(sell_text, True, WHITE)
        text_rect = btn_text.get_rect(center=self.development_buttons['sell'].center)
        self.screen.blit(btn_text, text_rect)
        y_offset += button_height + button_margin
        
        self.development_buttons['close'] = pygame.Rect(
            card_x + 20, y_offset, button_width, button_height
        )
        hover = self.development_buttons['close'].collidepoint(mouse_pos)
        pygame.draw.rect(self.screen, BUTTON_HOVER if hover else ERROR_COLOR, 
                       self.development_buttons['close'], border_radius=5)
        
        btn_text = self.small_font.render("Close", True, WHITE)
        text_rect = btn_text.get_rect(center=self.development_buttons['close'].center)
        self.screen.blit(btn_text, text_rect)
    
    def handle_development_click(self, pos, property_data):
        print("\n=== Development Click Debug ===")
        
        if not property_data:
            print("Error: No property selected")
            return False
        
        current_player = self.logic.players[self.logic.current_player_index]
        print(f"Player: {current_player['name']}")
        print(f"Property: {property_data['name']}")
        print(f"Houses: {property_data.get('houses', 0)}")
        
        for action, button in self.development_buttons.items():
            if button.collidepoint(pos):
                print(f"Button clicked: {action}")
                
                if action == 'close':
                    self.selected_property = None
                    self.state = "ROLL"
                    print("Closing development UI")
                    return True
                
                elif action == 'upgrade':
                    houses = property_data.get('houses', 0)
                    if houses < 4:
                        result = self.logic.build_house(property_data, current_player)
                        if result:
                            self.board.add_message(f"{current_player['name']} built a house on {property_data['name']}")
                            print(f"House built successfully on {property_data['name']}")
                        else:
                            print("Failed to build house")
                    else:
                        result = self.logic.build_hotel(property_data, current_player)
                        if result:
                            self.board.add_message(f"{current_player['name']} built a hotel on {property_data['name']}")
                            print(f"Hotel built successfully on {property_data['name']}")
                        else:
                            print("Failed to build hotel")
                    
                    print(f"Upgrade result: {result}")
                    self.board.update_ownership(self.logic.properties)
                    return False
                
                elif action == 'mortgage':
                    is_mortgaged = property_data.get('is_mortgaged', False)
                    if is_mortgaged:
                        result = self.logic.unmortgage_property(property_data, current_player)
                        if result:
                            self.board.add_message(f"{current_player['name']} unmortgaged {property_data['name']}")
                            print(f"Property unmortgaged successfully: {property_data['name']}")
                        else:
                            print("Failed to unmortgage property")
                    else:
                        result = self.logic.mortgage_property(property_data, current_player)
                        if result:
                            self.board.add_message(f"{current_player['name']} mortgaged {property_data['name']}")
                            print(f"Property mortgaged successfully: {property_data['name']}")
                        else:
                            print("Failed to mortgage property")
                    
                    print(f"Mortgage/Unmortgage result: {result}")
                    self.board.update_ownership(self.logic.properties)
                    return False
                
                elif action == 'sell':
                    houses = property_data.get('houses', 0)
                    if houses == 5:
                        result = self.logic.sell_hotel(property_data, current_player)
                        if result:
                            self.board.add_message(f"{current_player['name']} sold a hotel from {property_data['name']}")
                            print(f"Hotel sold successfully from {property_data['name']}")
                        else:
                            print("Failed to sell hotel")
                    elif houses > 0:
                        result = self.logic.sell_house(property_data, current_player)
                        if result:
                            self.board.add_message(f"{current_player['name']} sold a house from {property_data['name']}")
                            print(f"House sold successfully from {property_data['name']}")
                        else:
                            print("Failed to sell house")
                    else:
                        self.board.add_message("No houses/hotels to sell")
                        result = False
                        print("Nothing to sell: property has no houses or hotels")
                    
                    print(f"Sell result: {result}")
                    self.board.update_ownership(self.logic.properties)
                    return False
                
                elif action == 'auction':
                    current_player = self.logic.players[self.logic.current_player_index]
                    
                    property_data['owner'] = None
                    
                    self.board.add_message(f"{current_player['name']} put {property_data['name']} up for auction")
                    print(f"Player {current_player['name']} is auctioning {property_data['name']}")
                    
                    self.start_auction(property_data)
                    
                    self.board.update_ownership(self.logic.properties)
                    
                    return False
        
        return False

    def draw_free_parking_pot(self):
        window_size = self.screen.get_size()
        
        panel_width = 200
        panel_height = 100
        panel_x = 10
        panel_y = 230
        
        glow_surface = pygame.Surface((panel_width + 10, panel_height + 10), pygame.SRCALPHA)
        for i in range(5):
            alpha = int(100 * (1 - i/5))
            pygame.draw.rect(glow_surface, (*ACCENT_COLOR[:3], alpha),
                           pygame.Rect(i, i, panel_width + 10 - i*2, panel_height + 10 - i*2),
                           border_radius=10)
        self.screen.blit(glow_surface, (panel_x - 5, panel_y - 5))
        
        panel = pygame.Surface((panel_width, panel_height))
        panel.fill(MODERN_BG)
        self.screen.blit(panel, (panel_x, panel_y))
        
        title_text = self.small_font.render("Free Parking Pot", True, LIGHT_GRAY)
        title_rect = title_text.get_rect(centerx=panel_x + panel_width//2, top=panel_y + 10)
        self.screen.blit(title_text, title_rect)
        
        money_color = SUCCESS_COLOR if self.free_parking_pot > 0 else LIGHT_GRAY
        money_text = self.font.render(f"£{self.free_parking_pot:,}", True, money_color)
        money_rect = money_text.get_rect(centerx=panel_x + panel_width//2, top=title_rect.bottom + 10)
        self.screen.blit(money_text, money_rect)
        

    def add_to_free_parking(self, amount):
        self.free_parking_pot += amount
        self.board.add_message(f"£{amount} added to Free Parking pot (Total: £{self.free_parking_pot})")

    def collect_free_parking(self, player):
        if self.free_parking_pot > 0:
            amount = self.free_parking_pot
            player['money'] += amount
            self.free_parking_pot = 0
            self.board.add_message(f"{player['name']} collected £{amount} from Free Parking!")
            return True
        return False

    def handle_fine_payment(self, player, amount, reason="fine"):
        if player['money'] >= amount:
            player['money'] -= amount
            self.add_to_free_parking(amount)
            self.board.add_message(f"{player['name']} paid £{amount} {reason}")
            return True
        else:
            self.board.add_message(f"{player['name']} cannot pay £{amount} {reason}")
            return False

    def synchronize_free_parking_pot(self):
        if hasattr(self.logic, 'free_parking_fund'):
            self.free_parking_pot = self.logic.free_parking_fund

    def show_exit_confirmation(self):
        window_size = self.screen.get_size()
        
        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        
        dialog_width = int(window_size[0] * 0.4)
        dialog_height = int(window_size[1] * 0.25)
        dialog_x = (window_size[0] - dialog_width) // 2
        dialog_y = (window_size[1] - dialog_height) // 2
        
        shadow_rect = pygame.Rect(dialog_x + 6, dialog_y + 6, dialog_width, dialog_height)
        shadow = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
        
        button_width = 100
        button_height = 40
        button_spacing = 30
        total_width = (button_width * 2) + button_spacing
        start_x = dialog_x + (dialog_width - total_width) // 2
        button_y = dialog_y + dialog_height - 60
        
        yes_button = pygame.Rect(start_x, button_y, button_width, button_height)
        no_button = pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height)
        
        title_text = self.font.render("Leave Game?", True, ERROR_COLOR)
        title_rect = title_text.get_rect(centerx=dialog_x + dialog_width//2, top=dialog_y + 20)
        
        warning_text = self.small_font.render("Warning: You will lose the game if you leave!", True, BLACK)
        warning_rect = warning_text.get_rect(centerx=dialog_x + dialog_width//2, top=title_rect.bottom + 20)
        
        message_text = self.small_font.render("All your properties will be returned to the bank.", True, BLACK)
        message_rect = message_text.get_rect(centerx=dialog_x + dialog_width//2, top=warning_rect.bottom + 10)
        
        yes_text = self.font.render("Yes", True, WHITE)
        no_text = self.font.render("No", True, WHITE)
        
        last_yes_hover = False
        last_no_hover = False
        
        def draw_dialog(force_redraw=False, yes_hover=False, no_hover=False):
            if force_redraw or yes_hover != last_yes_hover or no_hover != last_no_hover:
                screen_backup = self.screen.copy()
                
                self.screen.blit(overlay, (0, 0))
                
                self.screen.blit(shadow, shadow_rect)
                pygame.draw.rect(self.screen, WHITE, (dialog_x, dialog_y, dialog_width, dialog_height), border_radius=15)
                self.screen.blit(title_text, title_rect)
                self.screen.blit(warning_text, warning_rect)
                self.screen.blit(message_text, message_rect)
                
                pygame.draw.rect(self.screen, BUTTON_HOVER if yes_hover else ERROR_COLOR, yes_button, border_radius=5)
                pygame.draw.rect(self.screen, BUTTON_HOVER if no_hover else ACCENT_COLOR, no_button, border_radius=5)
                
                yes_rect = yes_text.get_rect(center=yes_button.center)
                self.screen.blit(yes_text, yes_rect)
                
                no_rect = no_text.get_rect(center=no_button.center)
                self.screen.blit(no_text, no_rect)
                
                pygame.display.flip()
                return yes_hover, no_hover
            return last_yes_hover, last_no_hover
        
        last_yes_hover, last_no_hover = draw_dialog(force_redraw=True)
        
        waiting = True
        confirm_exit = False
        last_update_time = pygame.time.get_ticks()
        
        while waiting:
            current_time = pygame.time.get_ticks()
            
            if current_time - last_update_time < 16: 
                pygame.time.wait(5)
                continue
                
            last_update_time = current_time
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_button.collidepoint(event.pos):
                        confirm_exit = True
                        waiting = False
                    elif no_button.collidepoint(event.pos):
                        confirm_exit = False
                        waiting = False
                        
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        confirm_exit = True
                        waiting = False
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        confirm_exit = False
                        waiting = False
                
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = pygame.mouse.get_pos()
                    yes_hover = yes_button.collidepoint(mouse_pos)
                    no_hover = no_button.collidepoint(mouse_pos)
                    last_yes_hover, last_no_hover = draw_dialog(force_redraw=False, yes_hover=yes_hover, no_hover=no_hover)
        
        pygame.time.wait(100)
        
        self.draw()
        pygame.display.flip()
        
        return confirm_exit

    def synchronize_player_money(self):
        for player in self.players:                
            for logic_player in self.logic.players:
                if player.name == logic_player['name']:
                    if hasattr(player, 'money') and player.money != logic_player.get('money', 0):
                        old_money = player.money
                        player.money = logic_player.get('money', 0)
                        print(f"Money synchronized for {player.name}: {old_money} -> {player.money}")
                    break

    def check_and_trigger_ai_turn(self, recursion_depth=0):
        if recursion_depth > len(self.logic.players):
            print("Maximum recursion depth reached in check_and_trigger_ai_turn, aborting")
            return False
            
        if self.state != "ROLL":
            print("Not in ROLL state, skipping AI turn check")
            return False
            
        if not self.logic.players:
            print("No players left in the game")
            return False
            
        if self.logic.current_player_index >= len(self.logic.players):
            print(f"Invalid current_player_index: {self.logic.current_player_index}, max: {len(self.logic.players) - 1}")
            self.logic.current_player_index = 0
            
        current_player = self.logic.players[self.logic.current_player_index]
        
        if current_player.get('exited', False):
            print(f"Current player {current_player['name']} has exited, moving to next player")
            self.logic.current_player_index = (self.logic.current_player_index + 1) % len(self.logic.players)
            return self.check_and_trigger_ai_turn(recursion_depth + 1)  
            
        player_obj = next((p for p in self.players if p.name == current_player['name']), None)
        
        if not player_obj:
            print(f"Could not find Player object for {current_player['name']}")
            self.logic.current_player_index = (self.logic.current_player_index + 1) % len(self.logic.players)
            return self.check_and_trigger_ai_turn(recursion_depth + 1)
            
        if player_obj.is_ai:
            print(f"Player {current_player['name']} is an AI - automatically triggering their turn")
            self.current_player_is_ai = True
            pygame.time.delay(500)
            try:
                if self.state == "DEVELOPMENT":
                    print(f"Closing development UI for AI player {current_player['name']}")
                    self.state = "ROLL"
                    self.selected_property = None
                    self.development_mode = False
                
                self.play_turn()
                return True
            except Exception as e:
                print(f"Error in AI turn for {current_player['name']}: {e}")
                self.logic.current_player_index = (self.logic.current_player_index + 1) % len(self.logic.players)
                return False
        else:
            print(f"Player {current_player['name']} is not an AI - waiting for user input")
            self.current_player_is_ai = False
            return False

    def update_ai_mood(self, ai_player_name, is_happy):

        ai_player_obj = next((p for p in self.players if p.name == ai_player_name and p.is_ai), None)
        
        if not ai_player_obj:
            print(f"Warning: Could not find AI player object for {ai_player_name}")
            return False
        
        any_updated = False
        
        for player in self.players:
            if player.is_ai and hasattr(player, 'ai_controller') and hasattr(player.ai_controller, 'update_mood'):
                player.ai_controller.update_mood(is_happy)
                any_updated = True
        
        if any_updated:
            mood_text = "happier" if is_happy else "angrier"
            self.board.add_message(f"All AI players are getting {mood_text}!")
            self.show_notification(f"All AI players are getting {mood_text}!", 1500)
            return True
            
        return False

    def update_current_player(self):
        current_player = next((p for p in self.players if p.name == self.logic.players[self.logic.current_player_index]['name']), None)
        self.current_player_is_ai = current_player and current_player.is_ai
        
        for name, emotion_ui in self.emotion_uis.items():
            if not self.current_player_is_ai:
                print(f"Showing emotion UI for {name} during human turn")
                emotion_ui.show()
            else:
                print(f"Hiding emotion UI for {name} during AI turn")
                emotion_ui.hide()
                
        if current_player:
            print(f"Current player: {current_player.name} (AI: {current_player.is_ai})")
            if current_player.is_ai and hasattr(current_player, 'ai_controller'):
                print(f"AI type: {type(current_player.ai_controller).__name__}")
                if hasattr(current_player.ai_controller, 'mood_modifier'):
                    print(f"Current mood: {current_player.ai_controller.mood_modifier}")

    def handle_turn_end(self):
        self.logic.current_player_index = (self.logic.current_player_index + 1) % len(self.logic.players)
        
        self.update_current_player()
        
        self.state = "ROLL"
        self.current_property = None
        self.last_roll = None
        self.roll_time = 0
        self.dice_animation = False
        self.dice_values = None
