import pygame
import sys
import random
from src.Game_Logic import GameLogic
from src.Board import Board
from src.Font_Manager import font_manager
from src.Cards import CardType

# Color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
UI_BG = (18, 18, 18)
BURGUNDY = (128, 0, 32)
ACCENT_COLOR = BURGUNDY
ERROR_COLOR = (220, 53, 69)
BUTTON_HOVER = (160, 20, 40)

class GameJail:
    def __init__(self, screen, game_logic: GameLogic, board: Board):
        self.screen = screen
        self.logic = game_logic
        self.board = board
        self.font = font_manager.get_font(24)
        self.small_font = font_manager.get_font(18)
        self.jail_options_visible = False
        self.jail_buttons = {}

    def draw_jail_options(self, player):
        if not player.get("in_jail", False):
            return

        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.3)
        card_height = int(window_size[1] * 0.3)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2

        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))

        shadow_rect = pygame.Rect(card_x + 6, card_y + 6, card_width, card_height)
        shadow = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, shadow_rect)

        pygame.draw.rect(
            self.screen,
            WHITE,
            (card_x, card_y, card_width, card_height),
            border_radius=15,
        )

        title_text = self.font.render("Jail Options", True, ACCENT_COLOR)
        title_rect = title_text.get_rect(
            centerx=card_x + card_width // 2, y=card_y + 20
        )
        self.screen.blit(title_text, title_rect)

        options = []
        if player.get("jail_card", False):
            options.append(("Use Get Out of Jail Free Card", "card"))
        if player.get("money", 0) >= 50:
            options.append(("Pay £50 Fine", "pay"))
        options.append(("Roll for Doubles", "roll"))

        button_height = 40
        button_margin = 10
        y_offset = card_y + 80
        mouse_pos = pygame.mouse.get_pos()

        for i, (option_text, key) in enumerate(options):
            button_rect = pygame.Rect(
                card_x + 20, y_offset, card_width - 40, button_height
            )
            is_hovered = button_rect.collidepoint(mouse_pos)

            self.draw_button(button_rect, option_text, hover=is_hovered, active=True)

            y_offset += button_height + button_margin

        turns_text = self.small_font.render(
            f"Turns in jail: {player.get('jail_turns', 0)}/3", True, ERROR_COLOR
        )
        turns_rect = turns_text.get_rect(
            centerx=card_x + card_width // 2, bottom=card_y + card_height - 20
        )
        self.screen.blit(turns_text, turns_rect)

    def get_jail_choice(self, player):
        player_obj = next((p for p in self.players if p.name == player["name"]), None)
        if player_obj and player_obj.is_ai:
            if self.logic.jail_free_cards.get(player["name"], 0) > 0:
                return "card"
            elif player["money"] >= 50 and random.random() < 0.5:
                return "pay"
            return "roll"

        if self.game_mode == "abridged" and self.check_time_limit():
            print(
                "Time limit reached during jail choice - automatically returning 'roll'"
            )
            return "roll"

        if player["money"] < 50 and not self.logic.jail_free_cards.get(
            player["name"], 0
        ):
            self.board.add_message("No options available - must try rolling doubles")
            return "roll"

        waiting = True
        choice = None
        self.board.add_message("Choose how to get out of jail")

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
        if self.logic.jail_free_cards.get(player["name"], 0) > 0:
            options.append(("[1] Use Get Out of Jail Free card", "card"))
        if player["money"] >= 50:
            options.append(("[2] Pay £50 fine", "pay"))
        options.append(("[3] Try rolling doubles", "roll"))
        options.append(("[4] Stay in jail (skip 2 turns)", "stay"))

        button_rects = []
        y_offset = y_start
        for option_text, option_value in options:
            button_rect = pygame.Rect(
                card_x + 20, y_offset, card_width - 40, button_height
            )
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
                    if (
                        event.key == pygame.K_1
                        and self.logic.jail_free_cards.get(player["name"], 0) > 0
                    ):
                        choice = "card"
                        waiting = False
                    elif event.key == pygame.K_2 and player["money"] >= 50:
                        choice = "pay"
                        waiting = False
                    elif event.key == pygame.K_3:
                        choice = "roll"
                        waiting = False
                    elif event.key == pygame.K_4:
                        choice = "stay"
                        waiting = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if current_time - last_click_time < 300:
                        continue
                    last_click_time = current_time

                    mouse_pos = event.pos
                    for button_rect, option_value in button_rects:
                        if button_rect.collidepoint(mouse_pos):
                            if (
                                option_value == "card"
                                and self.logic.jail_free_cards.get(player["name"], 0)
                                > 0
                            ):
                                choice = "card"
                                waiting = False
                            elif option_value == "pay" and player["money"] >= 50:
                                choice = "pay"
                                waiting = False
                            elif option_value == "roll":
                                choice = "roll"
                                waiting = False
                            elif option_value == "stay":
                                choice = "stay"
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
        print(f"\n=== Jail Turn Handler for {player['name']} ===")
        print(f"In jail: {player['in_jail']}")
        print(f"Jail turns: {player.get('jail_turns', 0)}")
        print(f"Money: £{player['money']}")
        print(
            f"Has jail free cards: {self.logic.jail_free_cards.get(player['name'], 0)}"
        )

        if not player["in_jail"]:
            print("Player not in jail - exiting jail handler")
            return False

        player_obj = next((p for p in self.players if p.name == player["name"]), None)
        if not player_obj:
            print(f"Warning: Could not find player object for {player['name']}")
            return False

        if not player_obj.in_jail:
            print(f"Synchronizing jail state for {player['name']}")
            player_obj.in_jail = True
            player_obj.jail_turns = player["jail_turns"]

        if player_obj.is_ai:
            print(f"AI player {player['name']} deciding how to handle jail")

            if self.logic.jail_free_cards.get(player["name"], 0) > 0:
                print(f"AI using 'Get Out of Jail Free' card")
                card_type = player_obj.use_jail_card()
                if card_type == CardType.POT_LUCK:
                    self.pot_luck_deck.return_jail_card(card_type)
                    print("Returned Pot Luck jail card to deck")
                else:
                    self.opportunity_deck.return_jail_card(card_type)
                    print("Returned Opportunity Knocks jail card to deck")

                player["in_jail"] = False
                player["jail_turns"] = 0
                player_obj.in_jail = False
                player_obj.jail_turns = 0
                player_obj.stay_in_jail = False
                self.board.add_message(
                    f"{player['name']} used Get Out of Jail Free card and left jail!"
                )
                print(f"AI player {player['name']} successfully left jail using card")
                return True
            elif player["money"] >= 50 and random.random() < 0.5:
                print(
                    f"AI player {player['name']} paying £50 to leave jail (randomly decided)"
                )
                player["money"] -= 50
                self.logic.free_parking_fund += 50
                self.synchronize_free_parking_pot()
                player["in_jail"] = False
                player["jail_turns"] = 0
                player_obj.in_jail = False
                player_obj.jail_turns = 0
                player_obj.stay_in_jail = False
                self.board.add_message(f"{player['name']} paid £50 and left jail!")
                print(
                    f"AI player {player['name']} successfully left jail by paying £50"
                )
                return True
            else:
                print(f"AI player {player['name']} will try to roll doubles")
        else:
            print(f"Human player {player['name']} choosing jail option")
            self.draw()
            pygame.display.flip()

            choice = self.get_jail_choice(player)
            print(f"Human player selected option: {choice}")

            if (
                choice == "card"
                and self.logic.jail_free_cards.get(player["name"], 0) > 0
            ):
                print(f"Using 'Get Out of Jail Free' card")
                card_type = player_obj.use_jail_card()
                if card_type == CardType.POT_LUCK:
                    self.pot_luck_deck.return_jail_card(card_type)
                else:
                    self.opportunity_deck.return_jail_card(card_type)
                player["in_jail"] = False
                player["jail_turns"] = 0
                player_obj.in_jail = False
                player_obj.jail_turns = 0
                player_obj.stay_in_jail = False
                self.board.add_message(
                    f"{player['name']} used Get Out of Jail Free card and left jail!"
                )
                print(f"Player {player['name']} successfully left jail using card")
                return True
            elif choice == "pay" and player["money"] >= 50:
                print(f"Paying £50 to leave jail")
                player["money"] -= 50
                self.logic.free_parking_fund += 50
                self.synchronize_free_parking_pot()
                player["in_jail"] = False
                player["jail_turns"] = 0
                player_obj.in_jail = False
                player_obj.jail_turns = 0
                player_obj.stay_in_jail = False
                self.board.add_message(f"{player['name']} paid £50 and left jail!")
                try:
                    self.board.add_message(f"{player['name']} paid £50 and left jail!")
                except AttributeError:
                    print("Error: board.add_message call failed")
                print(f"Player {player['name']} successfully left jail by paying £50")
                return True
            elif choice == "stay":
                print(f"Player {player['name']} chose to stay in jail")
                player_obj.stay_in_jail = True
                player["jail_turns"] = player.get("jail_turns", 0) + 1
                player_obj.jail_turns = player["jail_turns"]
                self.board.add_message(f"{player['name']} chose to stay in jail!")
                return False
            elif choice == "roll":
                print(f"Player {player['name']} will try to roll doubles")
                return True

        player["jail_turns"] = player.get("jail_turns", 0) + 1
        player_obj.jail_turns = player["jail_turns"]
        print(f"Jail turn count increased to {player['jail_turns']}")

        if player["jail_turns"] >= 3:
            print(f"Player {player['name']} has been in jail for 3 turns")
            if player["money"] >= 50:
                print("Forcing payment after 3 turns")
                player["money"] -= 50
                self.logic.free_parking_fund += 50
                self.synchronize_free_parking_pot()
                player["in_jail"] = False
                player["jail_turns"] = 0
                player_obj.in_jail = False
                player_obj.jail_turns = 0
                player_obj.stay_in_jail = False
                self.board.add_message(
                    f"{player['name']} paid £50 after 3 turns and left jail!"
                )
                print(
                    f"Player {player['name']} successfully left jail after 3 turns by paying £50"
                )
                return True
            else:
                print(
                    f"Player {player['name']} can't pay jail fine - leaving jail bankrupt"
                )
                player["in_jail"] = False
                player["jail_turns"] = 0
                player_obj.in_jail = False
                player_obj.jail_turns = 0
                player_obj.stay_in_jail = False
                self.board.add_message(
                    f"{player['name']} couldn't pay jail fine and left jail bankrupt!"
                )
                self.handle_bankruptcy(player)
                return True

        print(f"Player {player['name']} remains in jail - jail turn handled\n")
        return False
