import pygame
import sys
import os
import time
import random
import math
from src.Board import Board
from src.Property import Property
from src.Game_Logic import GameLogic
from src.Cards import CardType
from src.Font_Manager import font_manager
from src.Ai_Player_Logic import EasyAIPlayer, HardAIPlayer
from src.UI import DevelopmentNotification, AIEmotionUI

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(base_path, "assets", "font", "Ticketing.ttf")

# Color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
UI_BG = (18, 18, 18)
BURGUNDY = (128, 0, 32)
DARK_GREEN = (0, 100, 0)
DARK_RED = (139, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
CREAM = (255, 253, 208)
ACCENT_COLOR = BURGUNDY
ERROR_COLOR = (220, 53, 69)
SUCCESS_COLOR = DARK_GREEN
BUTTON_HOVER = (160, 20, 40)

# Group colors for properties
GROUP_COLORS = {
    "Brown": (139, 69, 19),
    "Light Blue": (135, 206, 235),
    "Pink": (255, 192, 203),
    "Orange": (255, 165, 0),
    "Red": (255, 0, 0),
    "Yellow": (255, 255, 0),
    "Green": (0, 128, 0),
    "Blue": (0, 0, 255),
    "Station": (128, 128, 128),
    "Utility": (169, 169, 169)
}

class Game_Renderer:
    def __init__(
        self, players, game_mode="full", time_limit=None, ai_difficulty="easy"
    ):
        if not pygame.get_init():
            pygame.init()

        info = pygame.display.Info()
        self.screen = pygame.display.get_surface()
        if not self.screen:
            self.screen = pygame.display.set_mode((info.current_w, info.current_h))
        pygame.display.set_caption("Property Tycoon Alpha 25.03.2025")

        self.font = font_manager.get_font(32)
        self.small_font = font_manager.get_font(24)
        self.tiny_font = font_manager.get_font(16)
        self.button_font = font_manager.get_font(32)
        self.message_font = font_manager.get_font(24)

        window_size = self.screen.get_size()
        try:
            bg_path = os.path.join(base_path, "assets/image/starterbackground.png")
            self.original_background = pygame.image.load(bg_path)
            background = pygame.transform.scale(self.original_background, window_size)

            shuffling_path = os.path.join(base_path, "assets/image/Cards shuffling.png")
            self.original_shuffling = pygame.image.load(shuffling_path)
            shuffling_image = pygame.transform.scale(
                self.original_shuffling, window_size
            )

            self.screen.blit(background, (0, 0))
            self.screen.blit(shuffling_image, (0, 0))
            pygame.display.flip()
            pygame.time.wait(1000)

            start_path = os.path.join(base_path, "assets/image/Gamestart.png")
            self.original_start_image = pygame.image.load(start_path)
            logo_width = int(window_size[0] * 0.5)
            logo_height = int(
                logo_width
                * (
                    self.original_start_image.get_height()
                    / self.original_start_image.get_width()
                )
            )
            start_image = pygame.transform.scale(
                self.original_start_image, (logo_width, logo_height)
            )

            self.screen.blit(background, (0, 0))
            overlay = pygame.Surface(window_size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            logo_x = (window_size[0] - logo_width) // 2
            logo_y = (window_size[1] - logo_height) // 2
            self.screen.blit(start_image, (logo_x, logo_y))
            pygame.display.flip()
            pygame.time.wait(1000)
        except Exception as e:
            print(f"Error loading startup animations: {e}")

        self.game_mode = game_mode
        self.time_limit = time_limit
        self.ai_difficulty = ai_difficulty
        self.start_time = pygame.time.get_ticks() if time_limit else None

        if self.game_mode == "abridged" and self.time_limit:
            minutes = self.time_limit // 60
            print(
                f"Game initialized in Abridged mode with {minutes} minutes time limit"
            )
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
                dice_path = os.path.join(
                    base_path, "assets", "image", "Dice", f"{i}.png"
                )
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

            if self.ai_difficulty == "hard":
                from src.Ai_Player_Logic import HardAIPlayer

                self.logic.ai_player = HardAIPlayer()
            else:
                from src.Ai_Player_Logic import EasyAIPlayer

                self.logic.ai_player = EasyAIPlayer()

            if not self.logic.game_start():
                raise RuntimeError("Failed to initialize game data")

            if not players:
                raise ValueError("No players provided")

            self.players = players
            self.board = Board(self.players)

            from src.Cards import CardDeck, CardType

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
                button_height,
            )

            self.quit_button = pygame.Rect(
                window_size[0] - (button_width * 2) - (button_margin * 2),
                button_y,
                button_width,
                button_height,
            )

            self.pause_button = pygame.Rect(
                window_size[0] - (button_width * 2) - (button_margin * 2),
                button_y - button_height - button_margin,
                button_width,
                button_height,
            )

            self.game_paused = False
            self.pause_start_time = 0
            self.total_pause_time = 0

            self.yes_button = pygame.Rect(
                window_size[0] - (button_width * 2) - (button_margin * 2),
                button_y,
                button_width,
                button_height,
            )

            self.no_button = pygame.Rect(
                window_size[0] - button_width - button_margin,
                button_y,
                button_width,
                button_height,
            )

            self.auction_buttons = {
                "bid": pygame.Rect(0, 0, 120, 40),
                "pass": pygame.Rect(0, 0, 120, 40),
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
                if player.is_ai and self.ai_difficulty == "hard":
                    self.emotion_uis[player.name] = AIEmotionUI(
                        self.screen, player, self
                    )
                    print(f"Initialized emotion UI for {player.name}")

        except Exception as e:
            print(f"Error during game initialization: {e}")
            pygame.quit()
            raise

        self.update_current_player()

    def draw_button(self, button, text, hover=False, active=True):
        if not active:
            base_color = GRAY
        else:
            base_color = BUTTON_HOVER if hover else ACCENT_COLOR

        shadow_rect = button.copy()
        shadow_rect.y += 4
        shadow = pygame.Surface(button.size, pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=8)
        self.screen.blit(shadow, shadow_rect)

        button_surface = pygame.Surface(button.size, pygame.SRCALPHA)

        gradient = pygame.Surface(button.size, pygame.SRCALPHA)
        for i in range(button.height):
            alpha = 255 - int(i * 0.5)
            pygame.draw.line(gradient, (*base_color, alpha), (0, i), (button.width, i))

        pygame.draw.rect(
            button_surface, base_color, button_surface.get_rect(), border_radius=8
        )
        button_surface.blit(gradient, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        border_color = GOLD if hover else CREAM
        pygame.draw.rect(
            button_surface,
            border_color,
            button_surface.get_rect(),
            width=2,
            border_radius=8,
        )

        if hover:
            highlight = pygame.Surface(button.size, pygame.SRCALPHA)
            for i in range(4):
                alpha = 100 - i * 25
                pygame.draw.rect(
                    highlight,
                    (255, 255, 255, alpha),
                    highlight.get_rect().inflate(-i * 2, -i * 2),
                    border_radius=8,
                )
            button_surface.blit(highlight, (0, 0))

        self.screen.blit(button_surface, button)

        text_shadow = self.font.render(text, True, BLACK)
        text_rect_shadow = text_shadow.get_rect(center=button.center)
        text_rect_shadow.x += 1
        text_rect_shadow.y += 1
        self.screen.blit(text_shadow, text_rect_shadow)

        text_surface = self.font.render(text, True, CREAM)
        text_rect = text_surface.get_rect(center=button.center)
        self.screen.blit(text_surface, text_rect)


    def draw_time_remaining(self):
        if self.game_mode == "abridged" and self.time_limit:
            current_time = pygame.time.get_ticks()

            elapsed = (current_time - self.start_time - self.total_pause_time) // 1000

            if self.game_paused:
                current_pause_duration = current_time - self.pause_start_time
                elapsed = (
                    current_time
                    - self.start_time
                    - self.total_pause_time
                    - current_pause_duration
                ) // 1000

            remaining = max(0, self.time_limit - elapsed)
            minutes = remaining // 60
            seconds = remaining % 60

            window_size = self.screen.get_size()

            if (
                hasattr(self, "time_limit_reached")
                and self.time_limit_reached
                and not self.game_over
            ):
                banner_height = 40
                banner_surface = pygame.Surface(
                    (window_size[0], banner_height), pygame.SRCALPHA
                )
                banner_color = (255, 0, 0, 150)
                banner_surface.fill(banner_color)
                self.screen.blit(banner_surface, (0, 0))

                font = pygame.font.Font(None, 28)
                text = font.render(
                    "TIME'S UP! Finishing current lap...", True, (255, 255, 255)
                )
                text_rect = text.get_rect(
                    center=(window_size[0] // 2, banner_height // 2)
                )
                self.screen.blit(text, text_rect)

                remaining = 0
                minutes = 0
                seconds = 0

            if remaining <= self.time_warning_start:
                flash_alpha = (
                    abs(math.sin(current_time / self.warning_flash_rate)) * 255
                )
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

            glow_surface = pygame.Surface(
                (panel_width + 10, panel_height + 10), pygame.SRCALPHA
            )
            for i in range(5):
                alpha = int(100 * (1 - i / 5))
                pygame.draw.rect(
                    glow_surface,
                    (*ACCENT_COLOR[:3], alpha),
                    pygame.Rect(
                        i, i, panel_width + 10 - i * 2, panel_height + 10 - i * 2
                    ),
                    border_radius=10,
                )
            self.screen.blit(glow_surface, (panel_x - 5, panel_y - 5))

            panel = pygame.Surface((panel_width, panel_height))
            panel.fill(UI_BG)
            self.screen.blit(panel, (panel_x, panel_y))

            panel_title = self.small_font.render("GAME STATUS", True, LIGHT_GRAY)
            panel_title_rect = panel_title.get_rect(
                centerx=panel_x + panel_width // 2, top=panel_y + 10
            )
            self.screen.blit(panel_title, panel_title_rect)

            active_players = [
                p["name"] for p in self.logic.players if not p.get("exited", False)
            ]
            min_lap = (
                min([self.lap_count[p] for p in active_players])
                if active_players
                else 0
            )

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

            time_text = self.font.render(
                f"{minutes:02d}:{seconds:02d}", True, time_color
            )
            self.screen.blit(time_text, (panel_x + 40, time_y - 5))

            progress_width = panel_width - 30
            progress_height = 8
            progress_x = panel_x + 15
            progress_y = panel_y + panel_height - 20

            progress_percent = 1 - (remaining / self.time_limit)

            pygame.draw.rect(
                self.screen,
                GRAY,
                pygame.Rect(progress_x, progress_y, progress_width, progress_height),
                border_radius=4,
            )

            fill_width = int(progress_width * progress_percent)
            fill_color = ERROR_COLOR if remaining < 300 else ACCENT_COLOR
            if fill_width > 0:
                pygame.draw.rect(
                    self.screen,
                    fill_color,
                    pygame.Rect(progress_x, progress_y, fill_width, progress_height),
                    border_radius=4,
                )

    def draw(self):
        if self.game_mode == "abridged" and self.check_time_limit():
            return

        if not pygame.display.get_surface():
            return

        window_size = self.screen.get_size()
        self.screen.fill(UI_BG)
        gradient = pygame.Surface(window_size, pygame.SRCALPHA)
        for i in range(window_size[1]):
            alpha = int(255 * (1 - i / window_size[1]))
            pygame.draw.line(
                gradient, (*ACCENT_COLOR[:3], alpha), (0, i), (window_size[0], i)
            )
        self.screen.blit(gradient, (0, 0))

        if self.development_mode and self.state == "DEVELOPMENT":
            if (
                not any(player.is_moving for player in self.players)
                and not self.dice_animation
            ):
                current_player = self.logic.players[self.logic.current_player_index]
                if not current_player.get("is_ai", False):
                    if not hasattr(self, "dev_notification"):
                        self.dev_notification = DevelopmentNotification(
                            self.screen, current_player["name"]
                        )
                    self.dev_notification.draw(pygame.mouse.get_pos())

        self.board.draw(self.screen)

        for emotion_ui in self.emotion_uis.values():
            emotion_ui.draw()

        self.synchronize_player_positions()
        self.synchronize_player_money()
        self.synchronize_free_parking_pot()

        for player in self.players:
            player.update_animation()

            if (
                hasattr(player, "prev_moving")
                and player.prev_moving
                and not player.is_moving
            ):
                self.check_passing_go(player, player.move_start_position)
            player.prev_moving = player.is_moving

        any_player_moving = any(player.is_moving for player in self.players)

        if (
            hasattr(self, "waiting_for_animation")
            and self.waiting_for_animation
            and not any_player_moving
        ):
            self.waiting_for_animation = False

            if (
                hasattr(self, "pending_auction_property")
                and self.pending_auction_property
            ):
                print("Animations completed - starting pending auction")
                property_data = self.pending_auction_property
                self.pending_auction_property = None
                self.start_auction(property_data)

        if hasattr(self, "auction_completed") and self.auction_completed:
            current_time = pygame.time.get_ticks()
            if current_time - self.auction_end_time > self.auction_end_delay:
                print("Auction delay timer elapsed - changing state to ROLL")
                self.state = "ROLL"
                self.auction_completed = False

        self.board.draw(self.screen)

        mouse_pos = pygame.mouse.get_pos()

        panel_width = 280
        panel_spacing = 10
        player_height = 100
        total_height = (player_height + panel_spacing) * len(
            self.logic.players
        ) - panel_spacing
        panel_x = window_size[0] - panel_width - 20
        panel_y = 20

        panel_surface = pygame.Surface((panel_width, total_height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surface, (0, 0, 0, 180), panel_surface.get_rect(), border_radius=15
        )
        self.screen.blit(panel_surface, (panel_x, panel_y))

        current_y = panel_y
        hovered_property = None

        for i, player_data in enumerate(self.logic.players):
            is_current = i == self.logic.current_player_index
            player_obj = next(
                (p for p in self.players if p.name == player_data["name"]), None
            )

            player_rect = pygame.Rect(panel_x, current_y, panel_width, player_height)

            if is_current:
                highlight_surface = pygame.Surface(
                    (panel_width, player_height), pygame.SRCALPHA
                )
                highlight_color = (*ACCENT_COLOR[:3], 50)
                pygame.draw.rect(
                    highlight_surface,
                    highlight_color,
                    highlight_surface.get_rect(),
                    border_radius=15,
                )
                self.screen.blit(highlight_surface, player_rect)

            logo_size = 50
            logo_margin = 8
            logo_rect = pygame.Rect(
                panel_x + logo_margin,
                current_y + (player_height - logo_size) // 2,
                logo_size,
                logo_size,
            )

            if player_obj and player_obj.player_image:
                scaled_logo = pygame.transform.scale(
                    player_obj.player_image, (logo_size, logo_size)
                )
                if (
                    player_data.get("exited", False)
                    or player_data.get("bankrupt", False)
                    or (
                        player_obj
                        and (player_obj.voluntary_exit or player_obj.bankrupt)
                    )
                ):
                    scaled_logo.set_alpha(128)
                self.screen.blit(scaled_logo, logo_rect)

            info_x = logo_rect.right + 10
            info_y = current_y + 10

            name_color = ACCENT_COLOR if is_current else WHITE
            if player_data.get("in_jail", False):
                name_text = f"{player_data['name']} [JAIL]"
                name_color = ERROR_COLOR if is_current else GRAY
            elif player_data.get("exited", False) or (
                player_obj and player_obj.voluntary_exit
            ):
                name_text = player_data["name"]
                name_color = (200, 0, 0)
            elif player_data.get("bankrupt", False) or (
                player_obj and player_obj.bankrupt
            ):
                name_text = player_data["name"]
                name_color = (200, 0, 0)
            else:
                name_text = player_data["name"]

            name_surface = self.font.render(name_text, True, name_color)
            self.screen.blit(name_surface, (info_x, info_y))

            if player_data.get("exited", False) or (
                player_obj and player_obj.voluntary_exit
            ):
                exit_text = self.small_font.render("[EXITED]", True, (200, 0, 0))
                self.screen.blit(
                    exit_text, (info_x, info_y + name_surface.get_height())
                )
            elif player_data.get("bankrupt", False) or (
                player_obj and player_obj.bankrupt
            ):
                bankrupt_text = self.small_font.render("[BANKRUPT]", True, (200, 0, 0))
                self.screen.blit(
                    bankrupt_text, (info_x, info_y + name_surface.get_height())
                )

            money_y = info_y + 30
            if (
                player_data.get("exited", False)
                or player_data.get("bankrupt", False)
                or (player_obj and (player_obj.voluntary_exit or player_obj.bankrupt))
            ):
                money_y += 15

            money_text = f"£ {player_data['money']:,}"
            money_color = (
                SUCCESS_COLOR
                if player_data["money"] > 500
                else ERROR_COLOR if player_data["money"] < 200 else WHITE
            )
            money_surface = self.small_font.render(money_text, True, money_color)
            self.screen.blit(money_surface, (info_x, money_y))

            props = [
                prop
                for prop in self.logic.properties.values()
                if prop.get("owner") == player_data["name"]
            ]

            if props:
                prop_x = info_x
                prop_y = money_y + 30
                prop_size = 15
                prop_spacing = 5
                max_props_per_row = 6

                for idx, prop in enumerate(props):
                    row = idx // max_props_per_row
                    col = idx % max_props_per_row
                    x = prop_x + col * (prop_size + prop_spacing)
                    y = prop_y + row * (prop_size + prop_spacing)

                    prop_rect = pygame.Rect(x, y, prop_size, prop_size)
                    group = prop.get("group")
                    color = GROUP_COLORS.get(group, GRAY) if group else GRAY

                    pygame.draw.rect(self.screen, color, prop_rect, border_radius=3)

                    houses = prop.get("houses", 0)
                    if houses > 0:
                        if houses == 5:
                            indicator_color = RED
                            indicator_text = "H"
                        else:
                            indicator_color = GREEN
                            indicator_text = str(houses)

                        indicator_surface = self.tiny_font.render(
                            indicator_text, True, WHITE
                        )
                        indicator_rect = indicator_surface.get_rect(
                            center=prop_rect.center
                        )

                        self.screen.blit(indicator_surface, indicator_rect)

                    if prop_rect.collidepoint(mouse_pos):
                        hovered_property = prop
                        pygame.draw.rect(
                            self.screen, WHITE, prop_rect, 1, border_radius=3
                        )

            if i < len(self.logic.players) - 1:
                pygame.draw.line(
                    self.screen,
                    GRAY,
                    (panel_x + 10, current_y + player_height - 1),
                    (panel_x + panel_width - 10, current_y + player_height - 1),
                )

            current_y += player_height + panel_spacing

        if hovered_property:
            self.draw_property_tooltip(hovered_property, mouse_pos)

        self.draw_time_remaining()

        self.draw_free_parking_pot()

        self.draw_notification()

        for emotion_ui in self.emotion_uis.values():
            emotion_ui.draw()

        if self.state == "ROLL":
            current_player = next(
                (
                    p
                    for p in self.players
                    if p.name
                    == self.logic.players[self.logic.current_player_index]["name"]
                ),
                None,
            )
            self.current_player_is_ai = current_player and current_player.is_ai

            human_players_remaining = any(
                not p.is_ai and not p.voluntary_exit and not p.bankrupt
                for p in self.players
            )

            if not self.current_player_is_ai:
                for emotion_ui in self.emotion_uis.values():
                    emotion_ui.draw()

                if not self.development_mode:
                    self.draw_button(
                        self.roll_button,
                        "Roll",
                        hover=self.roll_button.collidepoint(mouse_pos),
                    )

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
                    pygame.draw.rect(
                        shadow, (*BLACK, 128), shadow.get_rect(), border_radius=5
                    )
                    self.screen.blit(shadow, shadow_rect)

                    pygame.draw.rect(
                        self.screen, base_color, self.quit_button, border_radius=5
                    )
                    gradient = pygame.Surface(self.quit_button.size, pygame.SRCALPHA)
                    for i in range(self.quit_button.height):
                        alpha = int(100 * (1 - i / self.quit_button.height))
                        pygame.draw.line(
                            gradient,
                            (255, 255, 255, alpha),
                            (0, i),
                            (self.quit_button.width, i),
                        )
                    self.screen.blit(gradient, self.quit_button)

                    quit_text = self.font.render("Leave", True, WHITE)
                    text_rect = quit_text.get_rect(center=self.quit_button.center)
                    text_shadow = self.font.render("Leave", True, BLACK)
                    text_shadow_rect = text_shadow.get_rect(
                        center=self.quit_button.center
                    )
                    text_shadow_rect.x += 1
                    text_shadow_rect.y += 1
                    self.screen.blit(text_shadow, text_shadow_rect)
                    self.screen.blit(quit_text, text_rect)

            elif not self.dice_animation and not any_player_moving:
                self.check_and_trigger_ai_turn()

        elif self.state == "BUY" and self.current_property is not None:
            self.draw_property_card(self.current_property)
            self.draw_buy_options(mouse_pos)
        elif self.state == "AUCTION" and hasattr(self.logic, "current_auction"):
            if self.logic.current_auction is None and not hasattr(
                self, "auction_completed"
            ):
                print(
                    "Warning: current_auction is None and no completion in progress - resetting state to ROLL"
                )
                self.state = "ROLL"
                return

            if self.logic.current_auction:
                self.draw_auction(self.logic.current_auction)
                result_message = self.logic.check_auction_end()
                if result_message == "auction_completed":
                    print("Auction completed in draw method - setting up delay")

                    if self.logic.current_auction and self.logic.current_auction.get(
                        "highest_bidder"
                    ):
                        winner = self.logic.current_auction["highest_bidder"]
                        property_name = self.logic.current_auction.get(
                            "property", {}
                        ).get("name", "Unknown property")
                        bid_amount = self.logic.current_auction.get("current_bid", 0)
                        self.board.add_message(
                            f"{winner['name']} won {property_name} for £{bid_amount}"
                        )
                    else:
                        property_name = self.logic.current_auction.get(
                            "property", {}
                        ).get("name", "Unknown property")
                        self.board.add_message(f"No one bid on {property_name}")

                    self.auction_end_time = pygame.time.get_ticks()
                    self.auction_end_delay = 3000
                    self.auction_completed = True
                    self.board.update_ownership(self.logic.properties)
        elif self.state == "DEVELOPMENT" and self.selected_property is not None:
            if hasattr(self.logic, "current_auction") and self.logic.current_auction:
                print("Auction in progress - not showing development UI")
            else:
                current_player = self.logic.players[self.logic.current_player_index]
                player_obj = next(
                    (p for p in self.players if p.name == current_player["name"]), None
                )

                if player_obj and player_obj.is_ai:
                    print(
                        f"Auto-closing development UI for AI player {current_player['name']}"
                    )
                    self.state = "ROLL"
                    self.selected_property = None
                    self.development_mode = False
                elif current_player.get("in_jail", False):
                    print(
                        f"Player {current_player['name']} is in jail - not showing development UI"
                    )
                    self.state = "ROLL"
                    self.selected_property = None
                    self.development_mode = False
                else:
                    self.draw_development_ui(self.selected_property)

        if self.development_mode and not any_player_moving and not self.dice_animation:
            if self.state in ["BUY", "AUCTION"]:
                print("Buy/Auction in progress - not showing development notification")
                return

            if hasattr(self.logic, "current_auction") and self.logic.current_auction:
                print("Auction in progress - not showing development notification")
            else:
                current_player = self.logic.players[self.logic.current_player_index]
                owned_properties = [
                    p
                    for p in self.logic.properties.values()
                    if p.get("owner") == current_player["name"]
                ]
                if owned_properties:
                    if not self.dev_notification:
                        self.dev_notification = DevelopmentNotification(
                            self.screen, current_player["name"], self.font
                        )

                    self.dev_notification.draw(mouse_pos)

        current_time = pygame.time.get_ticks()
        if self.dice_animation:
            if current_time - self.animation_start < self.animation_duration:
                dice1 = ((current_time // 100) % 6) + 1
                dice2 = ((current_time // 150) % 6) + 1
                self.draw_dice(dice1, dice2, True)
            else:
                self.finish_dice_animation()
        elif self.last_roll and (
            current_time - self.roll_time < self.ROLL_DISPLAY_TIME
        ):
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
                scaled_dice = pygame.transform.scale(
                    self.dice_images[value], (dice_size - 4, dice_size - 4)
                )
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
                sparkle_x = (
                    start_x
                    + dice_size
                    + spacing / 2
                    + math.cos(math.radians(angle)) * radius
                )
                sparkle_y = y + dice_size / 2 + math.sin(math.radians(angle)) * radius
                sparkle_color = (
                    255,
                    255,
                    0,
                    max(0, math.sin(current_time / 200 + i) * 255),
                )
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

        if "group" in property_data:
            header_height = 40
            header_rect = pygame.Rect(card_x, card_y, card_width, header_height)
            header_color = GROUP_COLORS.get(property_data["group"], GRAY)
            pygame.draw.rect(self.screen, header_color, header_rect, border_radius=15)
            pygame.draw.rect(
                self.screen,
                header_color,
                pygame.Rect(card_x, card_y + header_height - 15, card_width, 15),
            )

        name_text = self.font.render(property_data["name"], True, BLACK)
        name_rect = name_text.get_rect(centerx=card_rect.centerx, top=card_y + 50)
        self.screen.blit(name_text, name_rect)

        y_offset = name_rect.bottom + 20
        padding = 20

        price_text = self.font.render(
            f"Price: £{property_data['price']}", True, ACCENT_COLOR
        )
        self.screen.blit(price_text, (card_x + padding, y_offset))
        y_offset += 35

        rent_text = self.small_font.render(
            f"Base Rent: £{property_data.get('rent', 0)}", True, BLACK
        )
        self.screen.blit(rent_text, (card_x + padding, y_offset))
        y_offset += 25

        if "house_costs" in property_data:
            for i, cost in enumerate(property_data["house_costs"], 1):
                house_text = self.small_font.render(
                    f"{i} House{'s' if i > 1 else ''}: £{cost}", True, BLACK
                )
                self.screen.blit(house_text, (card_x + padding, y_offset))
                y_offset += 25

        if "Station" in property_data["name"]:
            rent_rules = [
                "1 Station: £25",
                "2 Stations: £50",
                "3 Stations: £100",
                "4 Stations: £200",
            ]
            for rule in rent_rules:
                rule_text = self.small_font.render(rule, True, BLACK)
                self.screen.blit(rule_text, (card_x + padding, y_offset))
                y_offset += 25
        elif property_data["name"] in ["Tesla Power Co", "Edison Water"]:
            utility_text = self.small_font.render(
                "Rent = 4x dice if 1 owned", True, BLACK
            )
            self.screen.blit(utility_text, (card_x + padding, y_offset))
            y_offset += 25
            utility_text2 = self.small_font.render(
                "Rent = 10x dice if both owned", True, BLACK
            )
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
        self.no_button = pygame.Rect(
            start_x + button_width + spacing, button_y, button_width, button_height
        )

        yes_hover = self.yes_button.collidepoint(mouse_pos)
        no_hover = self.no_button.collidepoint(mouse_pos)

        self.draw_button(self.yes_button, "Buy", hover=yes_hover, active=True)

        self.draw_button(self.no_button, "Pass", hover=no_hover, active=True)

    def draw_property_tooltip(self, property_data, mouse_pos):
        padding = 10
        window_size = self.screen.get_size()

        tooltip_width = 250
        line_height = 25
        num_lines = 5
        if property_data.get("group"):
            num_lines += 1
        tooltip_height = num_lines * line_height + padding * 2

        x = min(mouse_pos[0] + 20, window_size[0] - tooltip_width - padding)
        y = min(mouse_pos[1] + 20, window_size[1] - tooltip_height - padding)

        shadow_surface = pygame.Surface(
            (tooltip_width + 4, tooltip_height + 4), pygame.SRCALPHA
        )
        pygame.draw.rect(
            shadow_surface, (0, 0, 0, 128), shadow_surface.get_rect(), border_radius=10
        )
        self.screen.blit(shadow_surface, (x + 2, y + 2))

        tooltip_surface = pygame.Surface(
            (tooltip_width, tooltip_height), pygame.SRCALPHA
        )
        pygame.draw.rect(
            tooltip_surface,
            (30, 30, 30, 240),
            tooltip_surface.get_rect(),
            border_radius=10,
        )

        if property_data.get("group"):
            header_height = 30
            header_color = GROUP_COLORS.get(property_data["group"], GRAY)
            pygame.draw.rect(
                tooltip_surface,
                header_color,
                (0, 0, tooltip_width, header_height),
                border_radius=10,
            )
            pygame.draw.rect(
                tooltip_surface,
                header_color,
                (0, header_height - 15, tooltip_width, 15),
            )

        self.screen.blit(tooltip_surface, (x, y))

        current_y = y + padding

        name_text = self.small_font.render(property_data["name"], True, WHITE)
        self.screen.blit(name_text, (x + padding, current_y))
        current_y += line_height

        if property_data.get("group"):
            group_text = self.small_font.render(
                f"Group: {property_data['group']}", True, LIGHT_GRAY
            )
            self.screen.blit(group_text, (x + padding, current_y))
            current_y += line_height

        price_text = self.small_font.render(
            f"Price: £{property_data.get('price', 0):,}", True, SUCCESS_COLOR
        )
        self.screen.blit(price_text, (x + padding, current_y))
        current_y += line_height

        base_rent = property_data.get("rent", 0)
        rent_text = self.small_font.render(
            f"Base Rent: £{base_rent:,}", True, ACCENT_COLOR
        )
        self.screen.blit(rent_text, (x + padding, current_y))
        current_y += line_height

        if property_data.get("houses", 0) > 0:
            houses = property_data["houses"]
            if houses == 5:
                hotel_text = self.small_font.render("Has Hotel", True, RED)
                self.screen.blit(hotel_text, (x + padding, current_y))
            else:
                house_text = self.small_font.render(
                    f"Houses Built: {houses}", True, GREEN
                )
                self.screen.blit(house_text, (x + padding, current_y))
            current_y += line_height
        elif property_data.get("has_hotel", False):
            hotel_text = self.small_font.render("Has Hotel", True, RED)
            self.screen.blit(hotel_text, (x + padding, current_y))
            current_y += line_height

        if property_data.get("mortgaged", False):
            mortgage_text = self.small_font.render("[MORTGAGED]", True, ERROR_COLOR)
            self.screen.blit(mortgage_text, (x + padding, current_y))
        else:
            mortgage_value = property_data.get("price", 0) // 2
            mortgage_text = self.small_font.render(
                f"Mortgage Value: £{mortgage_value:,}", True, LIGHT_GRAY
            )
            self.screen.blit(mortgage_text, (x + padding, current_y))

        pygame.draw.rect(
            self.screen,
            ACCENT_COLOR,
            (x, y, tooltip_width, tooltip_height),
            1,
            border_radius=10,
        )

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

        if current_player.get("in_jail", False):
            print("Player is in jail")
            if dice1 == dice2:
                print("Rolled doubles - getting out of jail")
                current_player["in_jail"] = False
                current_player["jail_turns"] = 0
                self.board.add_message(
                    f"{current_player['name']} rolled doubles ({dice1},{dice2}) and left jail!"
                )

                for player in self.players:
                    if player.name == current_player["name"]:
                        player.in_jail = False
                        break
            else:
                print("Failed to roll doubles - staying in jail")
                self.handle_jail_turn(current_player)
                self.state = "ROLL"
                return

        position = current_player["position"]
        print(f"Landing on position: {position}")

        self.board.update_board_positions()
        self.board.update_ownership(self.logic.properties)

        current_player_obj = next(
            (p for p in self.players if p.name == current_player["name"]), None
        )

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
            self.board.add_message(
                f"{current_player['name']} landed on Opportunity Knocks"
            )

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
                current_player["in_jail"] = True
                current_player["jail_turns"] = 0
                current_player["position"] = 11

                for player in self.players:
                    if player.name == current_player["name"]:
                        player.position = 11
                        player.in_jail = True
                        player.jail_turns = 0
                        player.just_went_to_jail = True
                        break

                self.logic.is_going_to_jail = True
                self.handle_turn_end()
                self.state = "ROLL"
                self.board.update_board_positions()
            elif (
                "price" in space
                and space.get("owner") is None
                and not current_player.get("in_jail", False)
            ):
                if current_player.get("in_jail", False):
                    print("Player in jail - cannot buy property")
                    self.board.add_message(
                        f"{current_player['name']} cannot buy property while in jail!"
                    )
                    self.state = "ROLL"
                else:
                    print("\nUnowned property - initiating buy sequence")
                    print(f"Property price: £{space['price']}")
                    print(f"Player money: £{current_player['money']}")

                    if self.logic.completed_circuits.get(current_player["name"], 0) < 1:
                        message = f"{current_player['name']} must pass GO before buying property"
                        self.board.add_message(message)
                        print(
                            "Player has not completed a circuit - cannot buy property"
                        )
                        self.state = "ROLL"
                        return False

                    self.board.add_message(
                        f"{current_player['name']} landed on {space['name']}"
                    )
                    self.board.add_message(
                        f"Buy {space['name']} for £{space['price']}?"
                    )

                    self.draw()
                    pygame.display.flip()

                    pygame.time.delay(500)
                    self.state = "BUY"
                    self.current_property = space
                    print("Buy state activated")

                    if current_player_obj and current_player_obj.is_ai:
                        print("\nAI player making purchase decision")
                        pygame.time.delay(1000)
                        will_buy = (
                            random.random() < 0.7
                            and current_player["money"] >= space["price"]
                        )
                        print(f"AI decision: {'Buy' if will_buy else 'Pass'}")
                        self.handle_buy_decision(will_buy)
            else:
                print("Property already owned or not purchasable")
                self.state = "ROLL"

                if current_player_obj and current_player_obj.is_ai:
                    property_to_develop = (
                        self.logic.ai_player.handle_property_development(
                            current_player, self.logic.properties
                        )
                    )
                    if property_to_develop:
                        house_cost = property_to_develop["price"] / 2
                        if current_player["money"] >= house_cost:
                            property_to_develop["houses"] = (
                                property_to_develop.get("houses", 0) + 1
                            )
                            current_player["money"] -= house_cost
                            self.board.add_message(
                                f"{current_player['name']} built a house on {property_to_develop['name']}"
                            )
                            self.board.update_ownership(self.logic.properties)
        else:
            print("Not a property space or already processed by card handling")
            self.state = "ROLL"

        if self.state != "BUY":
            self.update_current_player()

        self.wait_for_animations()

        while self.logic.message_queue:
            message = self.logic.message_queue.pop(0)
            print(f"Processing message: {message}")
            self.board.add_message(message)
            if "Get Out of Jail Free card" in message or "collected" in message:
                self.board.add_message(message)

        print(f"\nFinal state: {self.state}")
        print("=== End Dice Roll Debug ===\n")

        self.draw()
        pygame.display.flip()

        self.development_mode = True

        current_player = self.logic.players[self.logic.current_player_index]
        owned_properties = [
            p
            for p in self.logic.properties.values()
            if p.get("owner") == current_player["name"]
        ]
        if not owned_properties:
            self.development_mode = False

        self.logic.is_going_to_jail = False
