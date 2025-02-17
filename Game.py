import pygame
from Board import Board
from Property import Property
from game_logic import GameLogic
from typing import Optional
import time
import math
import os

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
MODERN_BG = (18, 18, 18)
ACCENT_COLOR = (75, 139, 190)
BUTTON_HOVER = (95, 159, 210)
SUCCESS_COLOR = (40, 167, 69)
ERROR_COLOR = (220, 53, 69)

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
    def __init__(self, players, game_mode="full", time_limit=None):
        if not pygame.get_init():
            pygame.init()
            
        info = pygame.display.Info()
        self.screen = pygame.display.get_surface()
        if not self.screen:
            self.screen = pygame.display.set_mode((info.current_w, info.current_h))
        pygame.display.set_caption("Property Tycoon")
        self.font = pygame.font.Font(None, 42)
        self.small_font = pygame.font.Font(None, 32)
        
        self.game_mode = game_mode
        self.time_limit = time_limit
        self.start_time = pygame.time.get_ticks() if time_limit else None
        self.rounds_completed = {player.name: 0 for player in players}
        
        self.game_over = False
        self.winner_index = None
        
        self.time_warning_start = 60
        self.warning_flash_rate = 500
        
        self.dice_images = {}
        try:
            for i in range(1, 7):
                dice_path = os.path.join("assets", "image", "Dice", f"{i}.png")
                if os.path.exists(dice_path):
                    print(f"Loading dice image: {dice_path}")
                    self.dice_images[i] = pygame.image.load(dice_path)
                else:
                    print(f"Dice image not found: {dice_path}")
        except Exception as e:
            print(f"Error loading dice images: {e}")
        
        try:
            self.logic = GameLogic()
            if not self.logic.game_start():
                raise RuntimeError("Failed to initialize game data")
                
            self.players = players
            self.board = Board(self.players)
            
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
                    
        except Exception as e:
            print(f"Error during game initialization: {e}")
            pygame.quit()
            raise

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
            elapsed = (current_time - self.start_time) // 1000
            remaining = max(0, self.time_limit - elapsed)
            minutes = remaining // 60
            seconds = remaining % 60
            
            window_size = self.screen.get_size()
            
            if remaining <= self.time_warning_start:
                flash_alpha = abs(math.sin(current_time / self.warning_flash_rate)) * 255
                warning_surface = pygame.Surface(window_size, pygame.SRCALPHA)
                warning_color = (*ERROR_COLOR, int(flash_alpha * 0.1))
                warning_surface.fill(warning_color)
                self.screen.blit(warning_surface, (0, 0))
                
                if remaining == 60 or remaining == 30 or remaining == 10:
                    self.add_message(f"Warning: {remaining} seconds remaining!")

            panel_width = 200
            panel_height = 100
            panel_x = 10
            panel_y = 120
            
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
            
            title_text = self.small_font.render("Time Remaining", True, LIGHT_GRAY)
            title_rect = title_text.get_rect(centerx=panel_x + panel_width//2, top=panel_y + 10)
            self.screen.blit(title_text, title_rect)
            
            time_color = ERROR_COLOR if remaining < 300 else ACCENT_COLOR
            time_text = self.font.render(f"{minutes:02d}:{seconds:02d}", True, time_color)
            time_rect = time_text.get_rect(centerx=panel_x + panel_width//2, top=title_rect.bottom + 10)
            self.screen.blit(time_text, time_rect)
            
            if remaining < 300:
                rules_text = "Game will end when all players complete equal rounds"
                rules_surface = self.small_font.render(rules_text, True, LIGHT_GRAY)
                rules_rect = rules_surface.get_rect(
                    centerx=panel_x + panel_width//2, 
                    bottom=panel_y + panel_height - 25
                )
                self.screen.blit(rules_surface, rules_rect)
            
            progress_width = panel_width - 40
            progress_height = 8
            progress_x = panel_x + 20
            progress_y = panel_y + panel_height - 15
            
            pygame.draw.rect(self.screen, GRAY, 
                           pygame.Rect(progress_x, progress_y, progress_width, progress_height),
                           border_radius=4)
            
            progress = remaining / self.time_limit
            if progress > 0:
                progress_color = time_color
                pygame.draw.rect(self.screen, progress_color,
                               pygame.Rect(progress_x, progress_y, 
                                         int(progress_width * progress), progress_height),
                               border_radius=4)

    def draw(self):
        window_size = self.screen.get_size()
        self.screen.fill(MODERN_BG)
        gradient = pygame.Surface(window_size, pygame.SRCALPHA)
        for i in range(window_size[1]):
            alpha = int(255 * (1 - i/window_size[1]))
            pygame.draw.line(gradient, (*ACCENT_COLOR[:3], alpha), (0, i), (window_size[0], i))
        self.screen.blit(gradient, (0, 0))

        for i, player in enumerate(self.players):
            player.update_animation()
            player.set_active(i == self.logic.current_player_index)
            if self.game_over and i == self.winner_index:
                player.set_winner(True)

        self.board.draw(self.screen)
        
        self.draw_time_remaining()

        panel_height = 45 * len(self.logic.players)
        panel_width = 280
        panel_x = window_size[0] - panel_width - 10
        panel_y = 10
        
        s = pygame.Surface((panel_width, panel_height))
        s.set_alpha(180)
        s.fill(BLACK)
        self.screen.blit(s, (panel_x, panel_y))
        
        mouse_pos = pygame.mouse.get_pos()
        y = panel_y + 5
        
        for i, player_data in enumerate(self.logic.players):
            is_current = (i == self.logic.current_player_index)
            
            if is_current:
                highlight = pygame.Surface((panel_width - 10, 40))
                highlight.set_alpha(50)
                highlight.fill(ACCENT_COLOR)
                self.screen.blit(highlight, (panel_x + 5, y))
            
            player_obj = next((p for p in self.players if p.name == player_data['name']), None)
            
            if player_obj and player_obj.player_image:
                logo_size = 30
                logo_rect = pygame.Rect(panel_x + 10, y + 5, logo_size, logo_size)
                self.screen.blit(pygame.transform.scale(player_obj.player_image, (logo_size, logo_size)), logo_rect)
                name_x = panel_x + logo_size + 20
            else:
                name_x = panel_x + 10

            jail_free_cards = self.logic.jail_free_cards.get(player_data['name'], 0)
            if player_data.get('in_jail', False):
                name_with_status = f"{player_data['name']} (In Jail)"
                color = ERROR_COLOR if is_current else GRAY
                
                jail_turns = player_data.get('jail_turns', 0)
                jail_status = f"Turns in jail: {jail_turns}/3"
                if jail_free_cards > 0:
                    jail_status += f" (Has Jail Free Card)"
                jail_text = self.small_font.render(jail_status, True, ERROR_COLOR)
                self.screen.blit(jail_text, (name_x, y + 28))
                y += 20
            else:
                name_with_status = player_data['name']
                if jail_free_cards > 0:
                    name_with_status += f" ({jail_free_cards} Jail Free)"
                color = ACCENT_COLOR if is_current else WHITE

            text = self.font.render(name_with_status, True, color)
            self.screen.blit(text, (name_x, y + 5))
            
            money_color = SUCCESS_COLOR if player_data['money'] > 500 else ERROR_COLOR if player_data['money'] < 200 else WHITE
            money_text = self.small_font.render(f"£{player_data['money']}", True, money_color)
            self.screen.blit(money_text, (panel_x + 180, y + 10))

            if player_data.get('in_jail', False):
                jail_turns = player_data.get('jail_turns', 0)
                jail_text = self.small_font.render(f"Turns in jail: {jail_turns}/3", True, ERROR_COLOR)
                self.screen.blit(jail_text, (name_x, y + 28))
                y += 20
            
            props = [prop for prop in self.logic.properties.values() 
                    if prop.get('owner') == player_data['name']]
            
            if props:
                card_width = 60
                card_height = 30
                card_spacing = 5
                card_y = y + 35
                
                for idx, prop in enumerate(props):
                    card_x = panel_x + 20 + idx * (card_width + card_spacing)
                    card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
                    
                    group = prop.get('group')
                    card_color = GROUP_COLORS.get(group, GRAY) if group else GRAY
                    pygame.draw.rect(self.screen, card_color, card_rect, border_radius=3)
                    pygame.draw.rect(self.screen, WHITE, card_rect, 1, border_radius=3)
                    
                    if card_rect.collidepoint(mouse_pos):
                        self.draw_property_tooltip(prop, mouse_pos)
            
            y += 45 + (30 if props else 0)

        if self.state == "ROLL":
            self.draw_button(self.roll_button, "Roll", 
                           hover=self.roll_button.collidepoint(mouse_pos))
        elif self.state == "BUY" and self.current_property is not None:
            self.draw_property_card(self.current_property)
            
            self.draw_button(self.yes_button, "Buy", 
                           hover=self.yes_button.collidepoint(mouse_pos))
            self.draw_button(self.no_button, "Pass", 
                           hover=self.no_button.collidepoint(mouse_pos))
        elif self.state == "AUCTION" and hasattr(self.logic, 'current_auction'):
            self.draw_auction(self.logic.current_auction)
            result_message = self.logic.check_auction_end()
            if result_message:
                self.board.add_message(result_message)
                self.state = "ROLL"
                self.board.update_ownership(self.logic.properties)

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

        self.board.camera.handle_camera_controls(pygame.key.get_pressed())

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

    def draw_property_tooltip(self, property_data, mouse_pos):
        padding = 10
        window_size = self.screen.get_size()
        
        tooltip_width = 200
        tooltip_height = 80
        
        x = min(mouse_pos[0] + 10, window_size[0] - tooltip_width - padding)
        y = min(mouse_pos[1] + 10, window_size[1] - tooltip_height - padding)
        
        shadow = pygame.Surface((tooltip_width + 4, tooltip_height + 4), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=5)
        self.screen.blit(shadow, (x + 2, y + 2))
        
        tooltip = pygame.Surface((tooltip_width, tooltip_height))
        tooltip.fill(MODERN_BG)
        self.screen.blit(tooltip, (x, y))
        pygame.draw.rect(self.screen, WHITE, pygame.Rect(x, y, tooltip_width, tooltip_height), 1, border_radius=5)
        
        name_text = self.small_font.render(property_data['name'], True, WHITE)
        price_text = self.small_font.render(f"Price: £{property_data['price']}", True, ACCENT_COLOR)
        rent_text = self.small_font.render(f"Rent: £{property_data.get('rent', 0)}", True, LIGHT_GRAY)
        
        self.screen.blit(name_text, (x + padding, y + padding))
        self.screen.blit(price_text, (x + padding, y + padding + 25))
        self.screen.blit(rent_text, (x + padding, y + padding + 50))

    def finish_dice_animation(self):
        self.dice_animation = False
        dice1, dice2 = self.dice_values
        self.last_roll = (dice1, dice2)
        self.roll_time = pygame.time.get_ticks()

        current_player = self.logic.players[self.logic.current_player_index]
        position = current_player['position']
        
        self.board.update_board_positions()
        self.board.update_ownership(self.logic.properties)

        while self.logic.message_queue:
            message = self.logic.message_queue.pop(0)
            self.board.add_message(message)

        if str(position) in self.logic.properties:
            space = self.logic.properties[str(position)]
            if space["name"] == "Go to Jail":
                self.board.add_message(f"{current_player['name']} goes to Jail!")
                current_player['in_jail'] = True
                current_player['jail_turns'] = 0
                current_player['position'] = 11
                self.state = "ROLL"
                self.board.update_board_positions()
            elif "price" in space and not space.get("owner"):
                if current_player.get('in_jail', False):
                    self.board.add_message(f"{current_player['name']} cannot buy property while in jail!")
                    self.state = "ROLL"
                else:
                    self.state = "BUY"
                    self.current_property = space
                    self.board.add_message(f"{current_player['name']} landed on {space['name']}")
                    self.board.add_message(f"Buy {space['name']} for £{space['price']}?")
            else:
                self.state = "ROLL"
        else:
            self.state = "ROLL"

    def play_turn(self):
        if self.dice_animation:
            return False

        current_player = self.logic.players[self.logic.current_player_index]
        old_position = current_player['position']

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
                player.position = current_player['position']
                print(f"Moving {player.name} to position {player.position}")
                break
        
        self.board.update_board_positions()
        
        if current_player['position'] < old_position:
            self.rounds_completed[current_player['name']] += 1
            self.board.add_message("🎉 PASSED GO! 🎉")
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
                
        elif self.game_mode == "abridged":
            if self.time_limit and (current_time - self.start_time) // 1000 >= self.time_limit:
                min_rounds = min(self.rounds_completed.values())
                if all(rounds == min_rounds for rounds in self.rounds_completed.values()):
                    assets = {}
                    for player in self.logic.players:
                        total = player['money']
                        for prop in self.logic.properties.values():
                            if prop.get('owner') == player['name']:
                                total += prop.get('price', 0)
                                if 'houses' in prop:
                                    total += sum(prop.get('house_costs', []))[:prop['houses']]
                        assets[player['name']] = total
                    
                    winner = max(assets.items(), key=lambda x: x[1])[0]
                    self.game_over = True
                    return {"winner": winner,
                            "final_assets": assets,
                            "bankrupted_players": self.logic.bankrupted_players,
                            "voluntary_exits": self.logic.voluntary_exits}
        
        return None

    def handle_buy_decision(self, wants_to_buy):
        current_player = self.logic.players[self.logic.current_player_index]
        if wants_to_buy:
            if self.logic.buy_property(current_player):
                self.board.add_message(f"{current_player['name']} bought {self.current_property['name']}")
                self.board.update_ownership(self.logic.properties)
            else:
                self.board.add_message(f"{current_player['name']} cannot afford {self.current_property['name']}")
        else:
            self.board.add_message(f"{current_player['name']} passed on {self.current_property['name']}")
            result = self.logic.auction_property(current_player['position'])
            if result == "auction_in_progress":
                self.state = "AUCTION"
                self.auction_bid_amount = ""
                return
            self.board.update_ownership(self.logic.properties)
        
        self.state = "ROLL"
        self.current_property = None

    def handle_click(self, pos):
        if self.state == "ROLL":
            if self.roll_button.collidepoint(pos):
                return self.play_turn()
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
        elif self.state == "AUCTION":
            current_bidder = self.logic.current_auction["active_players"][self.logic.current_auction["current_bidder_index"]]
            if current_bidder.get('in_jail', False):
                self.board.add_message(f"{current_bidder['name']} cannot participate in auction while in jail!")
                self.logic.current_auction["passed_players"].add(current_bidder['name'])
                self.logic.move_to_next_bidder()
                return False
                
            if self.handle_auction_click(pos):
                result = self.logic.auction_property(self.logic.players[self.logic.current_player_index]['position'])
                if result == "auction_completed":
                    self.state = "ROLL"
                    self.current_property = None
                    self.board.update_ownership(self.logic.properties)
        return False

    def handle_motion(self, pos):
        if self.state == "ROLL":
            return self.roll_button.collidepoint(pos)
        elif self.state == "BUY":
            return self.yes_button.collidepoint(pos) or self.no_button.collidepoint(pos)
        elif self.state == "AUCTION":
            return any(btn.collidepoint(pos) for btn in self.auction_buttons.values())
        return False

    def handle_key(self, event):
        if self.state == "ROLL":
            if event.key in KEY_ROLL:
                return self.play_turn()
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
            self.handle_auction_input(event)
        
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

    def handle_voluntary_exit(self, player_name):
        if self.game_mode != "full":
            self.board.add_message("Exit only in full mode")
            return False
            
        self.board.add_message(f"{player_name} exits game")
        
        if self.logic.remove_player(player_name, voluntary=True):
            self.board.update_ownership(self.logic.properties)
            return True
        return False

    def handle_bankruptcy(self, player):
        if self.logic.remove_player(player['name']):
            self.board.add_message(f"{player['name']} bankrupt!")
            self.board.update_ownership(self.logic.properties)
            return True
        return False

    def draw_auction(self, auction_data):
        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.35)
        card_height = int(window_size[1] * 0.5)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2
        
        shadow_rect = pygame.Rect(card_x + 6, card_y + 6, card_width, card_height)
        shadow = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
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
            self.auction_buttons['bid'].topleft = (card_x + 20, card_y + card_height - 60)
            self.auction_buttons['pass'].topleft = (card_x + 150, card_y + card_height - 60)
            
            pygame.draw.rect(self.screen, WHITE, self.auction_input)
            pygame.draw.rect(self.screen, ACCENT_COLOR, self.auction_input, 2)
            
            if self.auction_bid_amount:
                bid_text = self.font.render(self.auction_bid_amount, True, BLACK)
            else:
                bid_text = self.small_font.render("Enter bid amount...", True, GRAY)
            self.screen.blit(bid_text, (self.auction_input.x + 10, self.auction_input.y + (self.auction_input.height - bid_text.get_height()) // 2))
            
            for btn_name, btn_rect in self.auction_buttons.items():
                mouse_over = btn_rect.collidepoint(pygame.mouse.get_pos())
                color = BUTTON_HOVER if mouse_over else ACCENT_COLOR
                pygame.draw.rect(self.screen, color, btn_rect, border_radius=5)
                
                btn_text = self.font.render(btn_name.title(), True, WHITE)
                self.screen.blit(btn_text, (btn_rect.centerx - btn_text.get_width()//2, 
                                        btn_rect.centery - btn_text.get_height()//2))
        
        if auction_data.get("passed_players"):
            passed_text = self.small_font.render("Passed: " + ", ".join(auction_data["passed_players"]), True, GRAY)
            self.screen.blit(passed_text, (card_x + 20, card_y + card_height - 30))

    def handle_auction_input(self, event):
        if not hasattr(self.logic, 'current_auction'):
            return
            
        current_bidder = self.logic.current_auction["active_players"][self.logic.current_auction["current_bidder_index"]]
        current_bidder_obj = next((p for p in self.players if p.name == current_bidder['name']), None)
        
        if current_bidder.get('in_jail', False):
            self.board.add_message(f"{current_bidder['name']} cannot bid while in jail!")
            self.logic.current_auction["passed_players"].add(current_bidder['name'])
            self.logic.move_to_next_bidder()
            return
            
        if current_bidder_obj and not current_bidder_obj.is_ai:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.auction_bid_amount = self.auction_bid_amount[:-1]
                elif event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                                 pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                    self.auction_bid_amount += event.unicode

    def handle_auction_click(self, pos):
        if not hasattr(self.logic, 'current_auction'):
            return False
            
        current_bidder = self.logic.current_auction["active_players"][self.logic.current_auction["current_bidder_index"]]
        current_bidder_obj = next((p for p in self.players if p.name == current_bidder['name']), None)
        
        if not current_bidder_obj or current_bidder_obj.is_ai:
            return False
        
        if self.auction_buttons['bid'].collidepoint(pos):
            try:
                bid_amount = int(self.auction_bid_amount or "0")
                success, message = self.logic.process_auction_bid(current_bidder, bid_amount)
                self.board.add_message(message)
                if success:
                    self.auction_bid_amount = ""
            except ValueError:
                self.board.add_message("Please enter a valid number!")
        
        elif self.auction_buttons['pass'].collidepoint(pos):
            success, message = self.logic.process_auction_pass(current_bidder)
            self.board.add_message(message)
        
        result_message = self.logic.check_auction_end()
        if result_message:
            self.board.add_message(result_message)
            self.state = "ROLL"
            self.board.update_ownership(self.logic.properties)
            return True
        
        return False

    def handle_game_over(self, winner_name):
        for i, player in enumerate(self.players):
            if player.name == winner_name:
                self.winner_index = i
                player.set_winner(True)
                break

    def draw_jail_options(self, player):
        if not player.get('in_jail', False):
            return

        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.25)
        card_height = int(window_size[1] * 0.25)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2

        pygame.draw.rect(self.screen, WHITE, pygame.Rect(card_x, card_y, card_width, card_height), border_radius=10)
        
        title_text = self.font.render("Jail Options", True, BLACK)
        title_rect = title_text.get_rect(centerx=card_x + card_width//2, top=card_y + 20)
        self.screen.blit(title_text, title_rect)

        options = []
        if self.logic.jail_free_cards.get(player['name'], 0) > 0:
            options.append("Use Get Out of Jail Free card")
        if player['money'] >= 50:
            options.append("Pay £50 fine")
        options.append("Try rolling doubles")

        y_offset = title_rect.bottom + 20
        for i, option in enumerate(options):
            text = self.small_font.render(option, True, BLACK)
            text_rect = text.get_rect(left=card_x + 20, top=y_offset)
            self.screen.blit(text, text_rect)
            y_offset += 30

        turns_text = self.small_font.render(f"Turns in jail: {player.get('jail_turns', 0)}/3", True, ERROR_COLOR)
        turns_rect = turns_text.get_rect(left=card_x + 20, bottom=card_y + card_height - 20)
        self.screen.blit(turns_text, turns_rect)
