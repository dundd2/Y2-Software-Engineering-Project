import pygame
import sys
import os
import time
import random
import math
from src.Board import Board
from src.Property import Property
from src.Game_Logic import GameLogic
from src.Cards import CardType, CardDeck
from src.Font_Manager import font_manager
from src.Ai_Player_Logic import EasyAIPlayer, HardAIPlayer
from typing import Optional
import string
from src.UI import DevelopmentNotification, AIEmotionUI
from src.GameRenderer import GameRenderer
from src.GameEventHandler import GameEventHandler

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_PATH = os.path.join(base_path, "assets", "font", "Ticketing.ttf")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
UI_BG = (18, 18, 18)

DARK_RED = (139, 0, 0)
DARK_GREEN = (0, 100, 0)
DARK_BLUE = (0, 0, 139)
GOLD = (218, 165, 32)
CREAM = (255, 253, 208)
BURGUNDY = (128, 0, 32)

RED = (255, 0, 0)
GREEN = (0, 255, 0)

ACCENT_COLOR = BURGUNDY
BUTTON_HOVER = (160, 20, 40)
ERROR_COLOR = (220, 53, 69)
SUCCESS_COLOR = DARK_GREEN
MODE_COLOR = DARK_BLUE
TIME_COLOR = (255, 180, 100)
HUMAN_COLOR = DARK_GREEN
AI_COLOR = DARK_RED

GROUP_COLORS = {
    "Brown": (139, 69, 19),
    "Blue": (0, 0, 255),
    "Purple": (128, 0, 128),
    "Orange": (255, 165, 0),
    "Red": (255, 0, 0),
    "Yellow": (255, 255, 0),
    "Green": (0, 255, 0),
    "Deep Blue": (0, 0, 139),
}

KEY_ROLL = [pygame.K_SPACE, pygame.K_RETURN]
KEY_BUY = [pygame.K_y, pygame.K_RETURN]
KEY_PASS = [pygame.K_n, pygame.K_ESCAPE]


class Game:
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

        self.renderer = None

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

    def add_message(self, text):
        self.board.add_message(text)

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

                    self.renderer.draw()
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

        self.renderer.draw()
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

        player_obj = next(
            (p for p in self.players if p.name == current_player["name"]), None
        )
        is_ai_player = player_obj and player_obj.is_ai

        if self.development_mode and not is_ai_player:
            return False

        self.update_current_player()

        if not player_obj:
            print(f"Warning: Could not find player object for {current_player['name']}")
            return False

        if player_obj.in_jail != current_player.get("in_jail", False):
            print(f"Synchronizing jail status for {player_obj.name}")
            player_obj.in_jail = current_player.get("in_jail", False)
            current_player["in_jail"] = player_obj.in_jail
            player_obj.jail_turns = current_player.get("jail_turns", 0)
            current_player["jail_turns"] = player_obj.jail_turns

        if player_obj.in_jail and player_obj.stay_in_jail:
            print(
                f"Player {current_player['name']} chose to stay in jail - skipping turn"
            )
            self.board.add_message(
                f"{current_player['name']} is staying in jail - skipping turn"
            )
            self.handle_turn_end()
            return True

        if player_obj.in_jail and current_player.get("in_jail", False):
            print(f"Player {current_player['name']} is in jail - showing jail options")
            jail_result = self.handle_jail_turn(current_player)
            if not jail_result:
                self.board.add_message(f"{current_player['name']} stays in jail")
                self.handle_turn_end()
                return True

        old_position = current_player["position"]

        self.lap_count[current_player["name"]] += 1
        print(
            f"Lap count for {current_player['name']}: {self.lap_count[current_player['name']]}"
        )

        if self.state == "ROLL":
            self.dice_animation = True
            self.animation_start = pygame.time.get_ticks()

            dice1, dice2 = self.logic.play_turn()
            if dice1 is None:
                self.dice_animation = False
                return True

            while self.logic.message_queue:
                message = self.logic.message_queue.pop(0)
                print(f"Processing message: {message}")
                self.board.add_message(message)
                if "left jail" in message:
                    print(f"Jail exit notification: {message}")

            self.dice_values = (dice1, dice2)

            for player in self.players:
                if player.name == current_player["name"]:
                    if player.position != old_position:
                        print(
                            f"Correcting position mismatch for {player.name}: Player object: {player.position}, Game logic: {old_position}"
                        )
                        player.position = old_position

                    spaces_to_move = (current_player["position"] - old_position) % 40
                    if (
                        spaces_to_move == 0
                        and current_player["position"] != old_position
                    ):
                        spaces_to_move = 40

                    self.move_player(player, spaces_to_move)
                    print(
                        f"Starting animation for {player.name} to move {spaces_to_move} spaces from {old_position} to {current_player['position']}"
                    )

        self.wait_for_animations()

        self.board.update_board_positions()

        if current_player["position"] < old_position:
            self.rounds_completed[current_player["name"]] += 1
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
                    winner = (
                        self.logic.bankrupted_players[-2]
                        if len(self.logic.bankrupted_players) > 1
                        else None
                    )
                    self.game_over = True
                    return {
                        "winner": winner,
                        "bankrupted_players": self.logic.bankrupted_players,
                        "voluntary_exits": self.logic.voluntary_exits,
                    }
                return None

            active_players = [p for p in self.logic.players if p["money"] > 0]
            if len(active_players) <= 1:
                winner = active_players[0]["name"] if active_players else None
                self.game_over = True
                return {
                    "winner": winner,
                    "bankrupted_players": self.logic.bankrupted_players,
                    "voluntary_exits": self.logic.voluntary_exits,
                }

            human_players = [
                p
                for p in self.players
                if not p.is_ai and not p.bankrupt and not p.voluntary_exit
            ]
            ai_players = [
                p
                for p in self.players
                if p.is_ai and not p.bankrupt and not p.voluntary_exit
            ]

            if len(human_players) == 0 and len(ai_players) == 1:
                winner = ai_players[0].name
                self.game_over = True
                return {
                    "winner": winner,
                    "bankrupted_players": self.logic.bankrupted_players,
                    "voluntary_exits": self.logic.voluntary_exits,
                }

        elif self.game_mode == "abridged":
            if (
                self.time_limit
                and (current_time - self.start_time) // 1000 >= self.time_limit
            ):
                active_players = [
                    p["name"] for p in self.logic.players if not p.get("exited", False)
                ]

                if active_players:
                    min_laps = min([self.lap_count[p] for p in active_players])
                    if all(self.lap_count[p] == min_laps for p in active_players):
                        assets = {}
                        for player in self.logic.players:
                            total = player["money"]
                            for prop in self.logic.properties.values():
                                if prop.get("owner") == player["name"]:
                                    total += prop.get("price", 0)
                                    if "houses" in prop:
                                        house_costs = prop.get("house_costs", [])
                                        houses_count = prop["houses"]
                                        if house_costs and houses_count > 0:
                                            total += sum(house_costs[:houses_count])
                            assets[player["name"]] = total

                        max_asset_value = max(assets.values())

                        winners = [
                            player
                            for player, value in assets.items()
                            if value == max_asset_value
                        ]

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
                            "voluntary_exits": self.logic.voluntary_exits,
                        }

        return None

    def handle_buy_decision(self, wants_to_buy):
        self.development_mode = False
        self.selected_property = None
        self.dev_notification = None

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
        print(
            f"Completed circuits: {self.logic.completed_circuits.get(current_player['name'], 0)}"
        )
        print(f"Current lap count: {self.lap_count.get(current_player['name'], 0)}")

        print(f"Property owner before: {property_data.get('owner', 'None')}")

        if wants_to_buy:
            if current_player["money"] >= property_data["price"]:
                print("\nAttempting purchase...")
                current_player["money"] -= property_data["price"]
                property_data["owner"] = current_player["name"]
                print(f"Property owner set to: {property_data['owner']}")
                print(f"Property data position: {property_data['position']}")
                print(
                    f"Property in self.logic.properties: {property_data['position'] in self.logic.properties}"
                )

                if str(property_data["position"]) in self.logic.properties:
                    print(
                        f"Global property owner: {self.logic.properties[str(property_data['position'])].get('owner', 'None')}"
                    )
                    self.logic.properties[str(property_data["position"])]["owner"] = (
                        current_player["name"]
                    )
                    print(
                        f"Updated global property owner: {self.logic.properties[str(property_data['position'])].get('owner', 'None')}"
                    )

                self.board.add_message(
                    f"{current_player['name']} bought {property_data['name']} for £{property_data['price']}"
                )
                print("Purchase successful")

                if (
                    not hasattr(self.logic, "current_auction")
                    or not self.logic.current_auction
                ):
                    print("State changed to ROLL")
                    self.state = "ROLL"
                else:
                    print("Auction in progress - maintaining AUCTION state")

                print("\nPlayer properties after purchase:")
                owned_count = 0
                for prop_pos, prop in self.logic.properties.items():
                    if prop.get("owner") == current_player["name"]:
                        owned_count += 1
                        print(
                            f"  - {prop['name']} (Position: {prop_pos}, Group: {prop.get('group', 'None')})"
                        )
                print(f"Total properties owned: {owned_count}")

                self.board.update_ownership(self.logic.properties)
            else:
                print("\nNot enough money for purchase")
                self.board.add_message(
                    f"{current_player['name']} doesn't have enough money to buy {property_data['name']}"
                )

                print("Starting auction due to insufficient funds")
                self.start_auction(property_data)
        else:
            print("\nPlayer passed on purchase")

            self.start_auction(property_data)

        print("\nFinal state:")
        print(f"Property owner: {property_data['owner']}")
        print(f"Player money: £{current_player['money']}")

        if not hasattr(self.logic, "current_auction") or not self.logic.current_auction:
            print(f"Final state: {self.state}")
            if self.state == "ROLL":
                self.update_current_player()
        else:
            print(f"Auction in progress - state is {self.state}")

    def start_auction(self, property_data):
        print(f"\n=== Starting Auction for {property_data['name']} ===")

        self.development_mode = False
        self.selected_property = None
        self.dev_notification = None

        any_eligible = False
        for player in self.logic.players:
            if self.logic.completed_circuits.get(player["name"], 0) >= 1:
                any_eligible = True
                break

        if not any_eligible:
            print("No players have completed a circuit - skipping auction")
            message = "No players have completed a circuit - property remains unsold"
            self.board.add_message(message)
            self.state = "ROLL"
            self.update_current_player()
            return

        any_moving = any(player.is_moving for player in self.players)
        if any_moving:
            print("Animations in progress - delaying auction start")
            self.pending_auction_property = property_data
            self.waiting_for_animation = True
            return

        result = self.logic.auction_property(property_data["position"])

        if result == "auction_in_progress":
            self.state = "AUCTION"
            self.auction_bid_amount = ""
            print(f"State changed to {self.state}")
            self.auction_just_started = True
        else:
            print(f"Failed to start auction: {result}")
            self.state = "ROLL"
            print(f"State changed to {self.state}")
            self.update_current_player()

    def handle_space(self, current_player):
        position = str(current_player["position"])
        if position not in self.logic.properties:
            return None, None

        space = self.logic.properties[position]

        if (
            "price" in space
            and space["owner"] is None
            and not current_player.get("in_jail", False)
        ):
            self.current_property = space
            self.state = "BUY"

            if self.logic.completed_circuits.get(current_player["name"], 0) < 1:
                self.start_auction(space)
                return None, None

            player_obj = next(
                (p for p in self.players if p.name == current_player["name"]), None
            )
            is_ai_player = (
                player_obj.is_ai if player_obj else current_player.get("is_ai", False)
            )

            if not is_ai_player:
                self.board.add_message(
                    f"Would you like to buy {space['name']} for £{space['price']}?"
                )
                return "can_buy", None
            else:
                if self.logic.ai_player.should_buy_property(
                    space,
                    current_player["money"],
                    [
                        p
                        for p in self.logic.properties.values()
                        if p.get("owner") == current_player["name"]
                    ],
                ):
                    self.handle_buy_decision(True)
                else:
                    self.handle_buy_decision(False)
                return None, None

        return self.logic.handle_space(current_player)

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
        for ui_player in self.players:
            if ui_player.name == player["name"]:
                ui_player.bankrupt = True
                print(f"Marking player {ui_player.name} as bankrupt in UI")
                break

        if self.logic.remove_player(player["name"]):
            self.board.add_message(f"{player['name']} bankrupt!")
            self.board.update_ownership(self.logic.properties)

            if self.check_one_player_remains():
                print("Only one player remains after bankruptcy - ending game")
                if self.game_settings.get("mode") == "full":
                    self.end_full_game()
                else:
                    self.end_abridged_game()

            return True
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
                self.renderer.draw()
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
            self.renderer.draw()
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

    def handle_card_action(self, card, player):
        print(f"Processing card action: {card.text} for player {player['name']}")

        self.show_card = True
        self.current_card = {"type": card.card_type.name, "message": card.text}
        self.current_card_player = player
        self.card_display_time = pygame.time.get_ticks()

        pygame.event.clear()
        waiting = True
        while waiting:
            self.renderer.draw()
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

        return result

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

    def handle_card_draw(self, player, card_type):

        result, message = self.logic.handle_card_draw(player, card_type)

        if result == "moved":
            player_obj = next(
                (p for p in self.players if p.name == player["name"]), None
            )
            if player_obj:
                player_obj.start_move([player["position"]])
                self.wait_for_animations()
                self.board.update_board_positions()

        return result

    def check_one_player_remains(self):
        if not hasattr(self, "_previous_active_counts"):
            self._previous_active_counts = {"ui": 0, "logic": 0}

        for ui_player in self.players:
            player_in_logic = any(
                p["name"] == ui_player.name for p in self.logic.players
            )
            if (
                not player_in_logic
                and not ui_player.bankrupt
                and not ui_player.voluntary_exit
            ):
                print(
                    f"Player {ui_player.name} not found in game logic but exists in UI - marking as bankrupt"
                )
                ui_player.bankrupt = True

        active_player_objects = [
            p for p in self.players if not p.bankrupt and not p.voluntary_exit
        ]
        active_player_data = [
            p
            for p in self.logic.players
            if p["money"] > 0 and not p.get("exited", False)
        ]

        if (
            len(active_player_objects) != self._previous_active_counts["ui"]
            or len(active_player_data) != self._previous_active_counts["logic"]
        ):
            print(f"\nActive player count changed:")
            print(
                f"UI players: {len(active_player_objects)} - {[p.name for p in active_player_objects]}"
            )
            print(
                f"Logic players: {len(active_player_data)} - {[p['name'] for p in active_player_data]}"
            )

            self._previous_active_counts["ui"] = len(active_player_objects)
            self._previous_active_counts["logic"] = len(active_player_data)

        if len(active_player_objects) <= 1 and len(active_player_data) <= 1:
            print("\nOne or fewer players remain active")

            if len(active_player_objects) == 1 and len(active_player_data) == 1:
                winner = active_player_objects[0]
                print(f"Last player standing: {winner.name}")
                self.game_over = True
                self.handle_game_over(winner.name)
            elif len(active_player_objects) == 0 and len(active_player_data) == 0:
                print("No active players remain - ending with no winner")
                self.game_over = True

            return True

        return False

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
            if (
                not hasattr(self, "_time_limit_notified")
                or not self._time_limit_notified
            ):
                minutes = self.time_limit // 60
                print(f"\n\n!!!TIME LIMIT REACHED!!!: {minutes} minutes have elapsed!")
                print("Game will end after all players complete their current lap...")

                self.board.add_message(f"TIME'S UP! Game will end after this lap.")

                if (
                    self.state == "AUCTION"
                    and hasattr(self.logic, "current_auction")
                    and self.logic.current_auction
                ):
                    print("Time limit reached during auction - canceling auction")
                    if (
                        isinstance(self.logic.current_auction, dict)
                        and "property" in self.logic.current_auction
                    ):
                        property_name = self.logic.current_auction.get(
                            "property", {}
                        ).get("name", "Unknown")
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
                    player_obj = next(
                        (p for p in self.players if p.name == player_name), None
                    )
                    if (
                        player_obj
                        and not player_obj.bankrupt
                        and not player_obj.voluntary_exit
                    ):
                        self.final_lap[player_name] = lap

                print("\n===== CURRENT GAME STATE =====")
                print(
                    f"Active players: {len([p for p in self.players if not p.bankrupt and not p.voluntary_exit])}"
                )
                print(f"Current lap counts: {self.final_lap}")
                print("Game will end after all players complete their current lap")

                print("\nCurrent Player Assets:")
                try:
                    for logic_player in self.logic.players:
                        player_name = logic_player["name"]
                        player_obj = next(
                            (p for p in self.players if p.name == player_name), None
                        )

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
                                print(
                                    f"Error calculating assets for {player_name}: {e}"
                                )
                                assets = logic_player.get("money", 0)
                                status = "Active (Fallback)"

                        print(f"  {player_name}: £{assets} ({status})")
                        print(f"  Lap count: {self.lap_count.get(player_name, 0)}")
                except Exception as e:
                    print(f"Error listing player assets: {e}")
                print("============================\n")

            if hasattr(self, "final_lap"):
                all_completed = True
                active_players = [
                    p.name
                    for p in self.players
                    if not p.bankrupt and not p.voluntary_exit
                ]

                for player_name in active_players:
                    if player_name in self.final_lap:
                        current_lap = self.lap_count.get(player_name, 0)
                        final_lap = self.final_lap.get(player_name, 0)

                        if current_lap <= final_lap:
                            all_completed = False
                            print(
                                f"Waiting for {player_name} to complete their turn (lap {current_lap}, final lap {final_lap})"
                            )
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
        active_players = [
            p for p in self.players if not p.bankrupt and not p.voluntary_exit
        ]
        winner = active_players[0] if active_players else None

        final_assets = {}

        for logic_player in self.logic.players:
            player_name = logic_player["name"]
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
            "tied_winners": [],
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
            player_name = logic_player["name"]
            player_obj = next((p for p in self.players if p.name == player_name), None)

            if player_obj and player_obj.voluntary_exit:
                final_assets[player_name] = player_obj.final_assets
            else:
                final_assets[player_name] = self.calculate_player_assets(logic_player)

        active_players = [
            p for p in self.players if not p.bankrupt and not p.voluntary_exit
        ]

        if active_players:
            active_player_assets = {
                p.name: final_assets.get(p.name, 0) for p in active_players
            }

            if active_player_assets:
                max_assets = (
                    max(active_player_assets.values()) if active_player_assets else 0
                )
                players_with_max_assets = [
                    name
                    for name, assets in active_player_assets.items()
                    if assets == max_assets
                ]

                if len(players_with_max_assets) > 1:
                    winner_name = "Tie"
                    tied_winners = players_with_max_assets
                else:
                    winner_name = (
                        players_with_max_assets[0]
                        if players_with_max_assets
                        else "No winner"
                    )
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
            "lap_count": self.lap_count,
        }

    def calculate_player_assets(self, player):
        try:
            if not player or not isinstance(player, dict):
                print(
                    f"Warning: Invalid player object in calculate_player_assets: {player}"
                )
                return 0

            total = player.get("money", 0)

            if not hasattr(self.logic, "properties") or not self.logic.properties:
                print("Warning: No properties found in game logic")
                return total

            for prop_id, prop in self.logic.properties.items():
                if not isinstance(prop, dict):
                    continue

                if prop.get("owner") == player.get("name"):
                    total += prop.get("price", 0)

                    if "houses" in prop and prop["houses"] > 0:
                        house_costs = prop.get("house_costs", [])

                        if isinstance(house_costs, list) and house_costs:
                            houses_count = min(prop["houses"], len(house_costs))
                            for i in range(houses_count):
                                total += house_costs[i]
                        elif isinstance(house_costs, (int, float)):
                            total += house_costs * prop["houses"]

            return total

        except Exception as e:
            print(f"Error in calculate_player_assets: {e}")
            return player.get("money", 0)

    def handle_voluntary_exit(self, player_name, final_assets):
        print(f"\n=== Voluntary Exit Debug ===")
        print(f"Player {player_name} is exiting the game")

        logic_player = next(
            (p for p in self.logic.players if p["name"] == player_name), None
        )
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

        player_properties = [
            p for p in self.logic.properties.values() if p.get("owner") == player_name
        ]
        print(
            f"Player has {len(player_properties)} properties that will be returned to bank"
        )

        if hasattr(player_obj, "handle_voluntary_exit"):
            print(f"Setting voluntary_exit flag for {player_name}")
            player_obj.final_assets = actual_final_assets
            player_obj.handle_voluntary_exit()

        result = self.logic.remove_player(player_name, voluntary=True)
        print(f"Game logic marked player as exited: {result}")

        if result:
            exited_player = next(
                (p for p in self.logic.players if p["name"] == player_name), None
            )
            if exited_player and exited_player.get("exited", False):
                print(f"Player {player_name} successfully marked as exited")
            else:
                print(f"Warning: Player {player_name} not properly marked as exited")

            self.board.update_ownership(self.logic.properties)

            active_players = [
                p for p in self.logic.players if not p.get("exited", False)
            ]
            print(f"Active players after exit: {[p['name'] for p in active_players]}")

            next_player_found = False
            original_index = self.logic.current_player_index

            while not next_player_found and active_players:
                self.logic.current_player_index = (
                    self.logic.current_player_index + 1
                ) % len(self.logic.players)

                if self.logic.current_player_index == original_index:
                    break

                current_player = self.logic.players[self.logic.current_player_index]
                if not current_player.get("exited", False):
                    next_player_found = True
                    print(
                        f"Next active player: {current_player['name']} (index: {self.logic.current_player_index})"
                    )

            print(f"Current player index after exit: {self.logic.current_player_index}")

            if len(active_players) <= 1:
                print(
                    f"Only {len(active_players)} active player(s) left - game should end soon"
                )
                if self.check_one_player_remains():
                    print("Game ending due to only one player remaining")
                    game_over_data = self.end_full_game()
                    return game_over_data

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
                print(
                    f"Warning: Invalid position {player.position} detected for {player.name} in move_player, resetting to position 1"
                )
                player.position = 1

            old_position = player.position

            if not isinstance(spaces, int):
                print(
                    f"Warning: Invalid spaces value {spaces} for {player.name}, defaulting to 0"
                )
                spaces = 0
            elif spaces < 0 or spaces > 40:
                print(
                    f"Warning: Spaces value {spaces} out of range for {player.name}, adjusting to valid range"
                )
                spaces = max(0, min(spaces, 40))

            new_position = (old_position + spaces) % 40
            if new_position == 0:
                new_position = 40

            if not (1 <= new_position <= 40):
                print(
                    f"Warning: Invalid new position {new_position} calculated for {player.name}, correcting"
                )
                new_position = max(1, min(new_position, 40))

            print(
                f"Player.move: {player.name} from {old_position} to {new_position} ({spaces} steps)"
            )

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
                if logic_player["name"] == player.name:
                    logic_player["position"] = new_position
                    found = True
                    break

            if not found:
                print(
                    f"Warning: Could not find logic player for {player.name} during move_player"
                )

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

        self.renderer.draw()
        pygame.display.flip()

        self.waiting_for_animation = True

    def check_passing_go(self, player, old_position):
        new_position = player.position

        if new_position < old_position and not self.logic.is_going_to_jail:
            player_dict = next(
                p for p in self.logic.players if p["name"] == player.name
            )
            player_dict["money"] += 200
            self.logic.bank_money -= 200
            self.board.add_message(f"{player.name} collected £200 for passing GO")

    def synchronize_player_positions(self):
        try:
            for player in self.players:
                if player.bankrupt or player.voluntary_exit:
                    continue

                if not isinstance(player.position, int) or not (
                    1 <= player.position <= 40
                ):
                    player.position = 1

            for logic_player in self.logic.players:
                if not isinstance(logic_player.get("position"), int) or not (
                    1 <= logic_player.get("position", 0) <= 40
                ):
                    logic_player["position"] = 1

            for player in self.players:
                if player.bankrupt or player.voluntary_exit:
                    continue

                found = False
                for logic_player in self.logic.players:
                    if player.name == logic_player["name"]:
                        found = True

                        if player.position != logic_player["position"]:
                            if player.is_ai:
                                player.position = logic_player["position"]
                            else:
                                if abs(player.position - logic_player["position"]) <= 3:
                                    logic_player["position"] = player.position
                        break

                if not found and not player.bankrupt and not player.voluntary_exit:
                    print(
                        f"Warning: Player {player.name} exists in UI but not in game logic"
                    )

            for logic_player in self.logic.players:
                found = False
                for player in self.players:
                    if logic_player["name"] == player.name:
                        found = True
                        break

                if not found:
                    print(
                        f"Warning: Player {logic_player['name']} exists in game logic but not in UI"
                    )
        except Exception as e:
            print(f"Error in synchronize_player_positions: {e}")

    def handle_ai_turn(self, ai_player):
        MAX_ITERATIONS = 100
        iteration_count = 0

        try:
            player_obj = next(
                (player for player in self.players if player.name == ai_player["name"]),
                None,
            )

            if not player_obj:
                return None

            if not player_obj.is_ai:
                return None

            player_pos_valid = (
                isinstance(player_obj.position, int) and 1 <= player_obj.position <= 40
            )
            logic_pos_valid = (
                isinstance(ai_player.get("position"), int)
                and 1 <= ai_player.get("position", 0) <= 40
            )

            if not player_pos_valid and logic_pos_valid:
                player_obj.position = ai_player["position"]
            elif player_pos_valid and not logic_pos_valid:
                ai_player["position"] = player_obj.position
            elif not player_pos_valid and not logic_pos_valid:
                player_obj.position = 1
                ai_player["position"] = 1
            elif player_obj.position != ai_player["position"]:
                player_obj.position = ai_player["position"]
        except Exception as e:
            return None

        if self.state == "ROLL":
            self.play_turn()

            start_time = pygame.time.get_ticks()
            while self.state == "BUY" and self.current_property:

                current_time = pygame.time.get_ticks()
                if current_time - start_time > 5000:
                    print(
                        f"Timeout reached for AI {ai_player['name']} in BUY state - forcing decision"
                    )
                    self.handle_buy_decision(False)
                    break

                iteration_count += 1
                if iteration_count > MAX_ITERATIONS:
                    print(
                        f"Maximum iterations reached for AI {ai_player['name']} in BUY state - forcing decision"
                    )
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
                        ai_player["money"],
                        [
                            p
                            for p in self.logic.properties.values()
                            if p.get("owner") == ai_player["name"]
                        ],
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

        elif self.state == "AUCTION" and hasattr(self.logic, "current_auction"):
            auction_data = self.logic.current_auction

            if auction_data is None:
                print("Warning: Auction data is None in handle_ai_turn")
                return None

            start_time = pygame.time.get_ticks()
            while (
                auction_data["active_players"][auction_data["current_bidder_index"]][
                    "name"
                ]
                == ai_player["name"]
            ):
                current_time = pygame.time.get_ticks()
                if current_time - start_time > 5000:
                    print(
                        f"Timeout reached for AI {ai_player['name']} in AUCTION state - forcing pass"
                    )
                    success, message = self.logic.process_auction_pass(ai_player)
                    if message:
                        self.board.add_message(message)
                    break

                iteration_count += 1
                if iteration_count > MAX_ITERATIONS:
                    print(
                        f"Maximum iterations reached for AI {ai_player['name']} in AUCTION state - forcing pass"
                    )
                    success, message = self.logic.process_auction_pass(ai_player)
                    if message:
                        self.board.add_message(message)
                    break

                print(f"\n=== AI Auction Turn ===")
                print(f"AI Player: {ai_player['name']}")
                print(f"Property: {auction_data['property']['name']}")
                print(f"Current bid: £{auction_data['current_bid']}")
                print(f"Minimum bid: £{auction_data['minimum_bid']}")

                if ai_player["name"] in auction_data.get("passed_players", set()):
                    print(f"AI {ai_player['name']} has already passed")
                    break

                try:
                    bid_amount = self.logic.get_ai_auction_bid(
                        ai_player, auction_data["property"], auction_data["current_bid"]
                    )

                    if bid_amount and bid_amount >= auction_data["minimum_bid"]:
                        print(f"AI Decision: Bid £{bid_amount}")
                        success, message = self.logic.process_auction_bid(
                            ai_player, bid_amount
                        )
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

    def handle_development_click(self, pos, property_data):
        print("\n=== Development Click Debug ===")

        if not property_data:
            print("Error: No property selected")
            return False

        current_player = self.logic.players[self.logic.current_player_index]
        print(f"Player: {current_player['name']}")
        print(f"Player lap count: {self.lap_count.get(current_player['name'], 0)}")
        print(f"Property: {property_data['name']}")
        print(f"Houses: {property_data.get('houses', 0)}")
        print(f"Development mode: {self.development_mode}")

        for action, button in self.development_buttons.items():
            if button.collidepoint(pos):
                print(f"Button clicked: {action}")

                if action == "close":
                    self.selected_property = None
                    self.state = "ROLL"
                    print("Closing development UI")
                    print(f"Development mode remains: {self.development_mode}")
                    return True

                elif action == "upgrade":
                    houses = property_data.get("houses", 0)
                    if houses < 4:
                        result = self.logic.build_house(property_data, current_player)
                        if result:
                            self.board.add_message(
                                f"{current_player['name']} built a house on {property_data['name']}"
                            )
                            print(
                                f"House built successfully on {property_data['name']}"
                            )
                        else:
                            print("Failed to build house")
                    else:
                        result = self.logic.build_hotel(property_data, current_player)
                        if result:
                            self.board.add_message(
                                f"{current_player['name']} built a hotel on {property_data['name']}"
                            )
                            print(
                                f"Hotel built successfully on {property_data['name']}"
                            )
                        else:
                            print("Failed to build hotel")

                    print(f"Upgrade result: {result}")
                    self.board.update_ownership(self.logic.properties)
                    return False

                elif action == "mortgage":
                    is_mortgaged = property_data.get("is_mortgaged", False)
                    if is_mortgaged:
                        result = self.logic.unmortgage_property(
                            property_data, current_player
                        )
                        if result:
                            self.board.add_message(
                                f"{current_player['name']} unmortgaged {property_data['name']}"
                            )
                            print(
                                f"Property unmortgaged successfully: {property_data['name']}"
                            )
                        else:
                            print("Failed to unmortgage property")
                    else:
                        result = self.logic.mortgage_property(
                            property_data, current_player
                        )
                        if result:
                            self.board.add_message(
                                f"{current_player['name']} mortgaged {property_data['name']}"
                            )
                            print(
                                f"Property mortgaged successfully: {property_data['name']}"
                            )
                        else:
                            print("Failed to mortgage property")

                    print(f"Mortgage/Unmortgage result: {result}")
                    self.board.update_ownership(self.logic.properties)
                    return False

                elif action == "sell":
                    houses = property_data.get("houses", 0)
                    if houses == 5:
                        result = self.logic.sell_hotel(property_data, current_player)
                        if result:
                            self.board.add_message(
                                f"{current_player['name']} sold a hotel from {property_data['name']}"
                            )
                            print(
                                f"Hotel sold successfully from {property_data['name']}"
                            )
                        else:
                            print("Failed to sell hotel")
                    elif houses > 0:
                        result = self.logic.sell_house(property_data, current_player)
                        if result:
                            self.board.add_message(
                                f"{current_player['name']} sold a house from {property_data['name']}"
                            )
                            print(
                                f"House sold successfully from {property_data['name']}"
                            )
                        else:
                            print("Failed to sell house")
                    else:
                        self.board.add_message("No houses/hotels to sell")
                        result = False
                        print("Nothing to sell: property has no houses or hotels")

                    print(f"Sell result: {result}")
                    self.board.update_ownership(self.logic.properties)
                    return False

                elif action == "auction":
                    current_player = self.logic.players[self.logic.current_player_index]

                    property_data["owner"] = None

                    self.board.add_message(
                        f"{current_player['name']} put {property_data['name']} up for auction"
                    )
                    print(
                        f"Player {current_player['name']} is auctioning {property_data['name']}"
                    )

                    self.start_auction(property_data)

                    self.board.update_ownership(self.logic.properties)

                    return False

        return False

    def add_to_free_parking(self, amount):
        self.free_parking_pot += amount
        self.board.add_message(
            f"£{amount} added to Free Parking pot (Total: £{self.free_parking_pot})"
        )

    def collect_free_parking(self, player):
        if self.free_parking_pot > 0:
            amount = self.free_parking_pot
            player["money"] += amount
            self.free_parking_pot = 0
            self.board.add_message(
                f"{player['name']} collected £{amount} from Free Parking!"
            )

            self.show_card = True
            self.current_card = {
                "type": "Free Parking",
                "message": f"You collected £{amount:,} from the Free Parking pot!",
            }
            self.current_card_player = player
            self.card_display_time = pygame.time.get_ticks()

            pygame.event.clear()
            waiting = True
            while waiting:
                self.renderer.draw()
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

            return True
        return False

    def handle_fine_payment(self, player, amount, reason="fine"):
        if player["money"] >= amount:
            player["money"] -= amount
            self.add_to_free_parking(amount)
            self.board.add_message(f"{player['name']} paid £{amount} {reason}")
            return True
        else:
            self.board.add_message(f"{player['name']} cannot pay £{amount} {reason}")
            return False

    def synchronize_free_parking_pot(self):
        if hasattr(self.logic, "free_parking_fund"):
            self.free_parking_pot = self.logic.free_parking_fund

    def show_exit_confirmation(self):
        window_size = self.screen.get_size()

        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))

        dialog_width = int(window_size[0] * 0.4)
        dialog_height = int(window_size[1] * 0.3)
        dialog_x = (window_size[0] - dialog_width) // 2
        dialog_y = (window_size[1] - dialog_height) // 2

        shadow_rect = pygame.Rect(
            dialog_x + 6, dialog_y + 6, dialog_width, dialog_height
        )
        shadow = pygame.Surface((dialog_width, dialog_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=15)

        button_width = 100
        button_height = 40
        button_spacing = 30
        total_width = (button_width * 2) + button_spacing
        start_x = dialog_x + (dialog_width - total_width) // 2
        button_y = dialog_y + dialog_height - 80

        yes_button = pygame.Rect(start_x, button_y, button_width, button_height)
        no_button = pygame.Rect(
            start_x + button_width + button_spacing,
            button_y,
            button_width,
            button_height,
        )

        title_text = self.font.render("Leave Game?", True, ERROR_COLOR)
        title_rect = title_text.get_rect(
            centerx=dialog_x + dialog_width // 2, top=dialog_y + 20
        )

        warning_text = self.small_font.render(
            "You will lose the game if you leave!", True, BLACK
        )
        warning_rect = warning_text.get_rect(
            centerx=dialog_x + dialog_width // 2, top=title_rect.bottom + 20
        )

        message_text = self.small_font.render(
            "Your properties will return to bank.", True, BLACK
        )
        message_rect = message_text.get_rect(
            centerx=dialog_x + dialog_width // 2, top=warning_rect.bottom + 10
        )

        yes_text = self.font.render("Yes", True, WHITE)
        no_text = self.font.render("No", True, WHITE)

        last_yes_hover = False
        last_no_hover = False

        def draw_dialog(force_redraw=False, yes_hover=False, no_hover=False):
            if force_redraw or yes_hover != last_yes_hover or no_hover != last_no_hover:
                screen_backup = self.screen.copy()

                self.screen.blit(overlay, (0, 0))

                self.screen.blit(shadow, shadow_rect)
                pygame.draw.rect(
                    self.screen,
                    WHITE,
                    (dialog_x, dialog_y, dialog_width, dialog_height),
                    border_radius=15,
                )
                self.screen.blit(title_text, title_rect)
                self.screen.blit(warning_text, warning_rect)
                self.screen.blit(message_text, message_rect)

                pygame.draw.rect(
                    self.screen,
                    BUTTON_HOVER if yes_hover else ERROR_COLOR,
                    yes_button,
                    border_radius=5,
                )
                pygame.draw.rect(
                    self.screen,
                    BUTTON_HOVER if no_hover else ACCENT_COLOR,
                    no_button,
                    border_radius=5,
                )

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
                    last_yes_hover, last_no_hover = draw_dialog(
                        force_redraw=False, yes_hover=yes_hover, no_hover=no_hover
                    )

        pygame.time.wait(100)

        self.renderer.draw()
        pygame.display.flip()

        return confirm_exit

    def synchronize_player_money(self):
        for player in self.players:
            for logic_player in self.logic.players:
                if player.name == logic_player["name"]:
                    if hasattr(player, "money") and player.money != logic_player.get(
                        "money", 0
                    ):
                        old_money = player.money
                        player.money = logic_player.get("money", 0)
                        print(
                            f"Money synchronized for {player.name}: {old_money} -> {player.money}"
                        )
                    break

    def check_and_trigger_ai_turn(self, recursion_depth=0):
        if recursion_depth > len(self.logic.players):
            print(
                "Maximum recursion depth reached in check_and_trigger_ai_turn, aborting"
            )
            return False

        if self.state != "ROLL" and self.state != "DEVELOPMENT":
            print(
                f"Not in ROLL or DEVELOPMENT state, skipping AI turn check. Current state: {self.state}"
            )
            return False

        if not self.logic.players:
            print("No players left in the game")
            return False

        if self.logic.current_player_index >= len(self.logic.players):
            print(
                f"Invalid current_player_index: {self.logic.current_player_index}, max: {len(self.logic.players) - 1}"
            )
            self.logic.current_player_index = 0

        current_player = self.logic.players[self.logic.current_player_index]

        if current_player.get("exited", False) or current_player.get("bankrupt", False):
            print(
                f"Current player {current_player['name']} has exited (exited: {current_player.get('exited', False)}, bankrupt: {current_player.get('bankrupt', False)}), moving to next player"
            )
            self.logic.current_player_index = (
                self.logic.current_player_index + 1
            ) % len(self.logic.players)
            return self.check_and_trigger_ai_turn(recursion_depth + 1)

        player_obj = next(
            (p for p in self.players if p.name == current_player["name"]), None
        )

        if not player_obj:
            print(f"Could not find Player object for {current_player['name']}")
            self.logic.current_player_index = (
                self.logic.current_player_index + 1
            ) % len(self.logic.players)
            return self.check_and_trigger_ai_turn(recursion_depth + 1)

        if player_obj.in_jail != current_player.get("in_jail", False):
            print(f"Synchronizing jail state for {player_obj.name}")
            player_obj.in_jail = current_player.get("in_jail", False)
            current_player["in_jail"] = player_obj.in_jail
            player_obj.jail_turns = current_player.get("jail_turns", 0)
            current_player["jail_turns"] = player_obj.jail_turns

        if player_obj.in_jail and player_obj.stay_in_jail:
            print(
                f"Player {current_player['name']} chose to stay in jail - skipping turn"
            )
            self.board.add_message(
                f"{current_player['name']} is staying in jail - skipping turn"
            )
            self.logic.current_player_index = (
                self.logic.current_player_index + 1
            ) % len(self.logic.players)
            return self.check_and_trigger_ai_turn(recursion_depth + 1)

        if player_obj.is_ai:
            print(
                f"Player {current_player['name']} is an AI - automatically triggering their turn"
            )
            self.current_player_is_ai = True
            pygame.time.delay(500)
            try:
                if player_obj.in_jail and current_player.get("in_jail", False):
                    print(
                        f"AI player {current_player['name']} is in jail - handling jail turn first"
                    )
                    jail_result = self.handle_jail_turn(current_player)
                    if not jail_result:
                        print(
                            f"AI player {current_player['name']} stays in jail - moving to next player"
                        )
                        self.handle_turn_end()
                        return self.check_and_trigger_ai_turn(recursion_depth + 1)

                if self.state == "DEVELOPMENT" and self.development_mode:
                    print(
                        f"AI player {current_player['name']} is in development mode - automatically handling development"
                    )
                    self.development_mode = False
                    self.state = "ROLL"
                    self.selected_property = None
                    self.handle_turn_end()
                    return self.check_and_trigger_ai_turn(recursion_depth + 1)

                if self.state == "ROLL":
                    turn_result = self.play_turn()
                    if turn_result:
                        print(
                            f"AI player {current_player['name']} completed their turn"
                        )
                        return True
                    return False

                return True
            except Exception as e:
                print(f"Error in AI turn for {current_player['name']}: {e}")
                self.logic.current_player_index = (
                    self.logic.current_player_index + 1
                ) % len(self.logic.players)
                return self.check_and_trigger_ai_turn(recursion_depth + 1)
        else:
            print(
                f"Player {current_player['name']} is not an AI - waiting for user input"
            )
            self.current_player_is_ai = False
            return False

    def update_ai_mood(self, ai_player_name, is_happy):

        ai_player_obj = next(
            (p for p in self.players if p.name == ai_player_name and p.is_ai), None
        )

        if not ai_player_obj:
            print(f"Warning: Could not find AI player object for {ai_player_name}")
            return False

        any_updated = False

        for player in self.players:
            if (
                player.is_ai
                and hasattr(player, "ai_controller")
                and hasattr(player.ai_controller, "update_mood")
            ):
                player.ai_controller.update_mood(is_happy)
                any_updated = True

        if any_updated:
            mood_text = "happier" if is_happy else "angrier"
            self.board.add_message(f"All AI players are getting {mood_text}!")
            return True

        return False

    def update_current_player(self):
        if self.logic.current_player_index >= len(self.logic.players):
            print(f"Invalid current player index: {self.logic.current_player_index}")
            if len(self.logic.players) > 0:
                self.logic.current_player_index = 0
            else:
                print("No players left in the game")
                return

        current_logic_player = self.logic.players[self.logic.current_player_index]

        if current_logic_player.get("exited", False):
            print(
                f"Current player {current_logic_player['name']} has exited, moving to next player"
            )
            self.logic.current_player_index = (
                self.logic.current_player_index + 1
            ) % len(self.logic.players)
            return self.update_current_player()

        current_player = next(
            (p for p in self.players if p.name == current_logic_player["name"]),
            None,
        )

        if not current_player or (
            hasattr(current_player, "voluntary_exit") and current_player.voluntary_exit
        ):
            print(
                f"Player {current_logic_player['name']} has no UI representation or has voluntarily exited"
            )
            if not current_logic_player.get("exited", False):
                print(
                    f"Marking player {current_logic_player['name']} as exited in game logic"
                )
                current_logic_player["exited"] = True
            self.logic.current_player_index = (
                self.logic.current_player_index + 1
            ) % len(self.logic.players)
            return self.update_current_player()

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
            self.board.add_message(f"{current_player.name}'s turn")
            if (
                hasattr(current_player, "is_ai")
                and current_player.is_ai
                and hasattr(current_player, "ai_controller")
            ):
                print(f"AI type: {type(current_player.ai_controller).__name__}")
                if hasattr(current_player.ai_controller, "mood_modifier"):
                    print(f"Current mood: {current_player.ai_controller.mood_modifier}")

    def handle_turn_end(self):
        current_player = self.logic.players[self.logic.current_player_index]
        player_obj = next(
            (p for p in self.players if p.name == current_player["name"]), None
        )
        is_ai_player = player_obj and player_obj.is_ai

        print(f"\n=== DEVELOPMENT MODE DEBUG - Turn End ===")
        print(f"Player: {current_player['name']}")
        print(f"Current development_mode: {self.development_mode}")
        print(f"Lap count: {self.lap_count.get(current_player['name'], 0)}")

        owned_properties = [
            prop
            for prop in self.logic.properties.values()
            if prop.get("owner") == current_player["name"]
        ]
        print(f"Owned properties: {len(owned_properties)}")
        for prop in owned_properties:
            print(f"  - {prop['name']} (Group: {prop.get('group', 'None')})")

        can_develop_properties = self.can_develop(current_player)
        print(f"Can develop properties: {can_develop_properties}")

        if (
            is_ai_player
            and not self.development_mode
            and self.can_develop(current_player)
        ):
            print(
                f"AI player {current_player['name']} could develop properties but chose not to"
            )
            self.development_mode = False
            print(f"Development mode set to: {self.development_mode}")
        elif (
            not is_ai_player
            and not self.development_mode
            and self.can_develop(current_player)
        ):
            print(
                f"Human player {current_player['name']} can develop - entering development mode"
            )
            self.state = "DEVELOPMENT"
            self.development_mode = True
            print(f"Development mode set to: {self.development_mode}")

            print(f"\n=== Properties eligible for development ===")
            for prop in owned_properties:
                can_build_house, house_error = self.logic.can_build_house(
                    prop, current_player
                )
                can_build_hotel, hotel_error = self.logic.can_build_hotel(
                    prop, current_player
                )
                print(f"  - {prop['name']} (Houses: {prop.get('houses', 0)})")
                print(
                    f"    Can build house: {can_build_house} {'' if can_build_house else '- ' + (house_error or 'Unknown error')}"
                )
                print(
                    f"    Can build hotel: {can_build_hotel} {'' if can_build_hotel else '- ' + (hotel_error or 'Unknown error')}"
                )

            return

        self.development_mode = False
        print(f"Development mode set to: {self.development_mode}")
        self.logic.current_player_index = (self.logic.current_player_index + 1) % len(
            self.logic.players
        )

        self.update_current_player()

        self.state = "ROLL"
        self.current_property = None
        self.last_roll = None
        self.roll_time = 0
        self.dice_animation = False
        self.dice_values = None

    def can_develop(self, player):
        print(f"\n=== DEVELOPMENT MODE DEBUG - can_develop check ===")
        print(f"Player: {player['name'] if player else 'None'}")

        if not player or not isinstance(player, dict):
            print("Cannot develop: Invalid player data")
            return False

        if self.lap_count.get(player["name"], 0) < 1:
            return False

        owned_properties = [
            prop
            for prop in self.logic.properties.values()
            if prop.get("owner") == player["name"]
        ]
        print(f"Player owns {len(owned_properties)} properties")

        if not owned_properties:
            print("Cannot develop: Player owns no properties")
            return False

        can_develop_property = False
        for prop in owned_properties:
            if self.logic.can_build_house(prop, player) or self.logic.can_build_hotel(
                prop, player
            ):
                return True

        return False
