## to do : move some game.py ui stuff back to ui.py
# some of the code should not in the file
# this file should only contain the game logic

import pygame
from Board import Board
from Property import Property
from game_logic import GameLogic
from typing import Optional
import time
import math

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
        
        self.time_warning_start = 60
        self.warning_flash_rate = 500
        
        try:
            self.logic = GameLogic()
            if not self.logic.game_start():
                raise RuntimeError("Failed to initialize game data")
                
            self.board = Board()
            
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
        for i, player in enumerate(self.logic.players):
            is_current = (i == self.logic.current_player_index)
            
            if is_current:
                highlight = pygame.Surface((panel_width - 10, 40))
                highlight.set_alpha(50)
                highlight.fill(ACCENT_COLOR)
                self.screen.blit(highlight, (panel_x + 5, y))
            
            color = ACCENT_COLOR if is_current else WHITE
            text = self.font.render(player['name'], True, color)
            self.screen.blit(text, (panel_x + 10, y + 5))
            
            money_color = SUCCESS_COLOR if player['money'] > 500 else ERROR_COLOR if player['money'] < 200 else WHITE
            money_text = self.small_font.render(f"£{player['money']}", True, money_color)
            self.screen.blit(money_text, (panel_x + 180, y + 10))
            
            props = [prop for prop in self.logic.properties.values() 
                    if prop.get('owner') == player['name']]
            
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
                           hover=self.roll_button.collidepoint(pygame.mouse.get_pos()))
        elif self.state == "BUY" and self.current_property is not None:
            self.draw_property_card(self.current_property)
            
            self.draw_button(self.yes_button, "Buy", 
                           hover=self.yes_button.collidepoint(pygame.mouse.get_pos()))
            self.draw_button(self.no_button, "Pass", 
                           hover=self.no_button.collidepoint(pygame.mouse.get_pos()))

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
            
            if is_rolling:
                color = ACCENT_COLOR
            else:
                color = BLACK
            pygame.draw.rect(self.screen, color, dice_rect, 2, border_radius=10)
            
            dice_text = self.font.render(str(value), True, BLACK)
            dice_text_rect = dice_text.get_rect(center=dice_rect.center)
            self.screen.blit(dice_text, dice_text_rect)

    def draw_property_card(self, property_data):
        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.25)
        card_height = int(window_size[1] * 0.3)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2

        shadow_rect = pygame.Rect(card_x + 4, card_y + 4, card_width, card_height)
        shadow = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, shadow_rect)

        card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        pygame.draw.rect(self.screen, WHITE, card_rect, border_radius=15)

        name_text = self.font.render(property_data['name'], True, BLACK)
        name_rect = name_text.get_rect(centerx=card_rect.centerx, top=card_rect.top + 20)
        self.screen.blit(name_text, name_rect)

        price_text = self.font.render(f"Price: £{property_data['price']}", True, ACCENT_COLOR)
        price_rect = price_text.get_rect(centerx=card_rect.centerx, top=name_rect.bottom + 20)
        self.screen.blit(price_text, price_rect)

        rent_text = self.small_font.render(f"Rent: £{property_data.get('rent', 0)}", True, BLACK)
        rent_rect = rent_text.get_rect(centerx=card_rect.centerx, top=price_rect.bottom + 20)
        self.screen.blit(rent_text, rent_rect)

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
        
        self.board.update_ownership(self.logic.properties)
        
        current_player = self.logic.players[self.logic.current_player_index]
        position = str(current_player['position'])
        
        while self.logic.message_queue:
            message = self.logic.message_queue.pop(0)
            self.board.add_message(message)
        
        if position in self.logic.properties:
            space = self.logic.properties[position]
            if space["name"] == "Go to Jail":
                self.board.add_message(f"{current_player['name']} goes to Jail!")
                self.state = "ROLL"
            elif "price" in space and not space.get("owner"):
                self.state = "BUY"
                self.current_property = space
                self.board.add_message(f"{current_player['name']} landed on {space['name']}")
                self.board.add_message(f"Buy {space['name']} for £{space['price']}?")
            else:
                if space.get("owner"):
                    rent = self.logic.calculate_space_rent(space, current_player)
                    self.board.add_message(f"{current_player['name']} pays £{rent} rent to {space['owner']}")

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
        
        if current_player['position'] < old_position:
            self.rounds_completed[current_player['name']] += 1
            
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
                    return {"winner": winner,
                           "bankrupted_players": self.logic.bankrupted_players,
                           "voluntary_exits": self.logic.voluntary_exits}
                return None
                
            active_players = [p for p in self.logic.players if p['money'] > 0]
            if len(active_players) <= 1:
                winner = active_players[0]['name'] if active_players else None
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
            if self.logic.auction_property(current_player['position']):
                self.board.update_ownership(self.logic.properties)
        
        self.state = "ROLL"
        self.current_property = None

    def handle_click(self, pos):
        if self.state == "ROLL":
            if self.roll_button.collidepoint(pos):
                return self.play_turn()
        elif self.state == "BUY" and self.current_property is not None:
            if self.yes_button.collidepoint(pos):
                self.handle_buy_decision(True)
                return False
            elif self.no_button.collidepoint(pos):
                self.handle_buy_decision(False)
                return False
        return False

    def handle_motion(self, pos):
        if self.state == "ROLL":
            return self.roll_button.collidepoint(pos)
        elif self.state == "BUY":
            return self.yes_button.collidepoint(pos) or self.no_button.collidepoint(pos)
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
        return False

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
