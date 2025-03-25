import pygame
from src.Game_Logic import GameLogic
from src.Board import Board
from src.Font_Manager import font_manager

# Color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BURGUNDY = (128, 0, 32)
ACCENT_COLOR = BURGUNDY
BUTTON_HOVER = (160, 20, 40)


class GameMessage:
    def __init__(self, screen, game_logic: GameLogic, board: Board):
        self.screen = screen
        self.logic = game_logic
        self.board = board
        self.font = font_manager.get_font(24)
        self.small_font = font_manager.get_font(18)
        self.notification = None
        self.notification_time = 0
        self.NOTIFICATION_DURATION = 3000  # 3 seconds

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

        pygame.draw.rect(
            self.screen, WHITE, (popup_x, popup_y, popup_width, popup_height)
        )
        pygame.draw.rect(
            self.screen, ACCENT_COLOR, (popup_x, popup_y, popup_width, popup_height), 2
        )

        if self.popup_title:
            title_surface = self.font.render(self.popup_title, True, ACCENT_COLOR)
            title_rect = title_surface.get_rect(
                centerx=popup_x + popup_width // 2, top=popup_y + 20
            )
            self.screen.blit(title_surface, title_rect)

        if self.popup_message:
            words = self.popup_message.split()
            lines = []
            current_line = []

            for word in words:
                test_line = " ".join(current_line + [word])
                test_surface = self.small_font.render(test_line, True, BLACK)
                if test_surface.get_width() <= popup_width - 40:
                    current_line.append(word)
                else:
                    lines.append(" ".join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(" ".join(current_line))

            y_offset = popup_y + 80
            for line in lines:
                text_surface = self.small_font.render(line, True, BLACK)
                text_rect = text_surface.get_rect(
                    centerx=popup_x + popup_width // 2, top=y_offset
                )
                self.screen.blit(text_surface, text_rect)
                y_offset += 30

        button_width = 100
        button_height = 40
        button_x = popup_x + (popup_width - button_width) // 2
        button_y = popup_y + popup_height - 60

        mouse_pos = pygame.mouse.get_pos()
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        button_color = (
            BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else ACCENT_COLOR
        )

        pygame.draw.rect(self.screen, button_color, button_rect, border_radius=5)
        button_text = self.small_font.render("OK", True, WHITE)
        text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, text_rect)

    def show_card_popup(self, card_type, message):
        self.show_card = True
        self.current_card = {"type": card_type, "message": message}
        self.current_card_player = self.logic.players[self.logic.current_player_index]
        self.card_display_time = pygame.time.get_ticks()

        print(f"Showing card popup: {card_type} - {message}")

    def show_rent_popup(self, player, owner, property_name, rent_amount):
        self.show_card = True
        self.current_card = {
            "type": "Rent Payment",
            "message": f"You landed on {property_name} owned by {owner['name']}. Pay £{rent_amount} rent.",
        }
        self.current_card_player = player
        self.card_display_time = pygame.time.get_ticks()

        self.board.add_message(
            f"{player['name']} paid £{rent_amount} rent to {owner['name']} for {property_name}"
        )

        print(
            f"Showing rent popup: {player['name']} paid £{rent_amount} to {owner['name']}"
        )

    def show_tax_popup(self, player, tax_name, tax_amount):
        self.show_card = True
        self.current_card = {
            "type": "Tax Payment",
            "message": f"You landed on {tax_name}. Pay £{tax_amount} to the bank.",
        }
        self.current_card_player = player
        self.card_display_time = pygame.time.get_ticks()

        self.board.add_message(f"{player['name']} paid £{tax_amount} for {tax_name}")

        print(f"Showing tax popup: {player['name']} paid £{tax_amount} for {tax_name}")
