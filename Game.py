## to do : move some game.py ui stuff back to ui.py
# some of the code should not in the file
import pygame
from Board import Board
from Property import Property
from game_logic import GameLogic
from typing import Optional
import time

WINDOW_SIZE = (1280, 720)
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
    def __init__(self, players):
        if not pygame.get_init():
            pygame.init()
            
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("Property Tycoon")
        self.font = pygame.font.Font(None, 42)
        self.small_font = pygame.font.Font(None, 32)
        
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
            
            self.player_emojis = ["😎", "🤠", "🤓", "😊", "🥳"]
            self.player_colors = {}
            
            for i, player in enumerate(players):
                if not self.logic.add_player(player.name):
                    raise RuntimeError(f"Failed to add player {player.name}")
                self.player_colors[player.name] = player.color

            self.message = None
            self.message_time = 0
            self.MESSAGE_DISPLAY_TIME = 2000

            self.button_animations = {}
            self.notification_queue = []
            self.notification_time = 0
            self.NOTIFICATION_DURATION = 3000
            
            button_width = 120
            button_height = 45
            button_margin = 20
            button_y = WINDOW_SIZE[1] - button_height - button_margin
            
            self.roll_button = pygame.Rect(
                WINDOW_SIZE[0] - button_width - button_margin,
                button_y,
                button_width,
                button_height
            )
            
            self.yes_button = pygame.Rect(
                WINDOW_SIZE[0] - (button_width * 2) - (button_margin * 2),
                button_y,
                button_width,
                button_height
            )
            
            self.no_button = pygame.Rect(
                WINDOW_SIZE[0] - button_width - button_margin,
                button_y,
                button_width,
                button_height
            )
            
            self.messages = []
            self.message_duration = 5000
            self.message_fade_time = 1000
            self.message_spacing = 70
            self.max_messages = 4
            self.message_times = []
                    
        except Exception as e:
            print(f"Error during game initialization: {e}")
            pygame.quit()
            raise

    def add_notification(self, text, color=WHITE):
        self.notification_queue.append({"text": text, "color": color})
        self.notification_time = pygame.time.get_ticks()

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
        self.messages.append(text)
        self.message_times.append(pygame.time.get_ticks())

    def draw(self):
        self.screen.fill(MODERN_BG)
        gradient = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        for i in range(WINDOW_SIZE[1]):
            alpha = int(255 * (1 - i/WINDOW_SIZE[1]))
            pygame.draw.line(gradient, (*ACCENT_COLOR[:3], alpha), (0, i), (WINDOW_SIZE[0], i))
        self.screen.blit(gradient, (0, 0))

        self.board.draw(self.screen)

        panel_height = 45 * len(self.logic.players)
        panel_width = 280
        panel_x = 10
        panel_y = 10
        
        s = pygame.Surface((panel_width, panel_height))
        s.set_alpha(180)
        s.fill(BLACK)
        self.screen.blit(s, (panel_x, panel_y))
        
        y = panel_y + 5
        for i, player in enumerate(self.logic.players):
            is_current = (i == self.logic.current_player_index)
            
            if is_current:
                highlight = pygame.Surface((panel_width - 10, 40))
                highlight.set_alpha(50)
                highlight.fill(ACCENT_COLOR)
                self.screen.blit(highlight, (panel_x + 5, y))
            
            emoji = self.player_emojis[i % len(self.player_emojis)]
            color = ACCENT_COLOR if is_current else WHITE
            text = self.font.render(f"{emoji} {player['name']}", True, color)
            self.screen.blit(text, (panel_x + 10, y + 5))
            
            money_color = SUCCESS_COLOR if player['money'] > 500 else ERROR_COLOR if player['money'] < 200 else WHITE
            money_text = self.small_font.render(f"£{player['money']}", True, money_color)
            self.screen.blit(money_text, (panel_x + 180, y + 10))
            
            props = [prop for prop in self.logic.properties.values() 
                    if prop.get('owner') == player['name']]
            if props:
                props_text = self.small_font.render(
                    ', '.join(p['name'][:15] + ('...' if len(p['name']) > 15 else '') 
                             for p in props[:3]), True, LIGHT_GRAY)
                self.screen.blit(props_text, (panel_x + 20, y + 25))
            
            y += 45

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

        self.draw_notifications()
        
        current_time = pygame.time.get_ticks()
        messages_to_remove = []
        
        visible_messages = [m for m, t in zip(self.messages, self.message_times) 
                          if current_time - t < self.message_duration][:self.max_messages]
        total_height = len(visible_messages) * self.message_spacing
        message_y = (WINDOW_SIZE[1] - total_height) // 2
        
        for i, (message, start_time) in enumerate(zip(self.messages, self.message_times)):
            if i >= self.max_messages:
                break
                
            if current_time - start_time > self.message_duration:
                messages_to_remove.append(i)
                continue
                
            time_displayed = current_time - start_time
            if time_displayed < self.message_duration - self.message_fade_time:
                alpha = 255
            else:
                fade_progress = (time_displayed - (self.message_duration - self.message_fade_time)) / self.message_fade_time
                alpha = int(255 * (1 - fade_progress))
            
            msg_surface = self.font.render(message, True, WHITE)
            msg_rect = msg_surface.get_rect(centerx=WINDOW_SIZE[0] // 2, y=message_y)
            
            padding = 30
            bg_rect = msg_rect.inflate(padding * 2, padding)
            bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            
            pygame.draw.rect(bg_surface, (0, 0, 0, int(alpha * 0.8)), 
                           bg_surface.get_rect(), border_radius=15)
            
            glow_size = 4
            for i in range(glow_size):
                glow_alpha = int((alpha * 0.4) * (1 - i/glow_size))
                pygame.draw.rect(bg_surface, (*ACCENT_COLOR, glow_alpha),
                               bg_surface.get_rect().inflate(i*2, i*2),
                               2, border_radius=15)
            
            self.screen.blit(bg_surface, bg_rect)
            
            msg_surface.set_alpha(alpha)
            self.screen.blit(msg_surface, msg_rect)
            
            message_y += self.message_spacing
        
        for i in reversed(messages_to_remove):
            self.messages.pop(i)
            self.message_times.pop(i)

        pygame.display.flip()

    def draw_dice(self, dice1, dice2, is_rolling):
        dice_size = 60
        spacing = 20
        start_x = WINDOW_SIZE[0] - (dice_size * 2 + spacing) - 20
        y = WINDOW_SIZE[1] - dice_size - 80

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
                pygame.draw.rect(self.screen, color, dice_rect, 2, border_radius=10)
            
            dice_text = self.font.render(str(value), True, BLACK)
            dice_text_rect = dice_text.get_rect(center=dice_rect.center)
            self.screen.blit(dice_text, dice_text_rect)

    def draw_property_card(self, property_data):
        card_width = 300
        card_height = 200
        card_x = (WINDOW_SIZE[0] - card_width) // 2
        card_y = (WINDOW_SIZE[1] - card_height) // 2

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

    def draw_notifications(self):
        current_time = pygame.time.get_ticks()
        if self.notification_queue and current_time - self.notification_time < self.NOTIFICATION_DURATION:
            notification = self.notification_queue[0]
            alpha = max(0, 255 - ((current_time - self.notification_time) / self.NOTIFICATION_DURATION * 255))
            
            text = self.font.render(notification["text"], True, notification["color"])
            text_rect = text.get_rect(centerx=WINDOW_SIZE[0]//2, y=100)
            
            bg_rect = text_rect.inflate(40, 20)
            bg = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            bg.fill((*BLACK, int(alpha * 0.7)))
            self.screen.blit(bg, bg_rect)
            
            text.set_alpha(int(alpha))
            self.screen.blit(text, text_rect)
        elif self.notification_queue:
            self.notification_queue.pop(0)
            if self.notification_queue:
                self.notification_time = current_time

    def finish_dice_animation(self):
        self.dice_animation = False
        dice1, dice2 = self.dice_values
        self.last_roll = (dice1, dice2)
        self.roll_time = pygame.time.get_ticks()
        
        self.board.update_ownership(self.logic.properties)
        
        current_player = self.logic.players[self.logic.current_player_index]
        position = str(current_player['position'])
        
        while self.logic.message_queue:
            self.add_message(self.logic.message_queue.pop(0))
        
        if position in self.logic.properties:
            space = self.logic.properties[position]
            if space["name"] == "Go to Jail":
                self.add_message(f"{current_player['name']} goes to Jail! Do not pass GO, do not collect £200")
                self.state = "ROLL"
            elif "price" in space and not space.get("owner"):
                self.state = "BUY"
                self.current_property = space
                self.add_message(f"{current_player['name']} landed on {space['name']}. Buy for £{space['price']}?")
            else:
                if space.get("owner"):
                    rent = self.logic.calculate_space_rent(space, current_player)
                    self.add_message(f"{current_player['name']} must pay £{rent} rent to {space['owner']}")
                self.state = "ROLL"

    def play_turn(self):
        if self.dice_animation:
            return False

        self.dice_animation = True
        self.animation_start = pygame.time.get_ticks()
        
        dice1, dice2 = self.logic.play_turn()
        if dice1 is None:
            self.dice_animation = False
            return True
        
        self.dice_values = (dice1, dice2)
        
        while self.logic.message_queue:
            self.add_message(self.logic.message_queue.pop(0))
        
        current_player = self.logic.players[self.logic.current_player_index]
        roll_message = f"{current_player['name']} rolled {dice1 + dice2} ({dice1}, {dice2})"
        self.add_message(roll_message)
        
        if dice1 == dice2:
            self.add_message("Doubles! Roll again!")
        
        if self.logic.is_game_over():
            winner = self.logic.get_winner()
            if winner:
                self.add_message(f"Game Over! {winner} wins!")
            return True
        
        return False

    def handle_buy_decision(self, wants_to_buy):
        current_player = self.logic.players[self.logic.current_player_index]
        if wants_to_buy:
            if self.logic.buy_property(current_player):
                self.add_message(f"{current_player['name']} bought {self.current_property['name']} for £{self.current_property['price']}")
                self.board.update_ownership(self.logic.properties)
            else:
                self.add_message(f"{current_player['name']} cannot afford {self.current_property['name']}")
        else:
            self.add_message(f"{current_player['name']} passed on {self.current_property['name']}")
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
        elif self.state == "BUY":
            if event.key in KEY_BUY:
                self.handle_buy_decision(True)
                return False
            elif event.key in KEY_PASS:
                self.handle_buy_decision(False)
                return False
        return False
