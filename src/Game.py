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
from typing import Optional
import string
from src.UI import DevelopmentNotification, AIEmotionUI

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

    def add_message(self, text):
        self.board.add_message(text)

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

        if (
            self.development_mode
            and self.dev_notification
            and self.dev_notification.check_click(pos)
        ):
            print("Continuing from development mode")
            self.development_mode = False
            print(f"Development mode set to: {self.development_mode}")
            self.selected_property = None
            self.state = "ROLL"
            self.dev_notification = None
            self.notification = None
            self.logic.current_player_index = (
                self.logic.current_player_index + 1
            ) % len(self.logic.players)
            return False

        if hasattr(self, "auction_just_started") and self.auction_just_started:
            print("Auction just started - ignoring click to prevent state transition")
            self.auction_just_started = False
            return False

        if self.state == "ROLL":
            if (
                not self.current_player_is_ai
                and self.game_mode == "abridged"
                and self.time_limit
                and self.pause_button.collidepoint(pos)
            ):
                current_time = pygame.time.get_ticks()

                if self.game_paused:
                    pause_duration = current_time - self.pause_start_time
                    self.total_pause_time += pause_duration
                    self.game_paused = False
                    self.board.add_message("Game resumed")
                else:
                    self.game_paused = True
                    self.pause_start_time = current_time
                    self.board.add_message("Game paused")

                return False

            if not self.current_player_is_ai and self.roll_button.collidepoint(pos):
                if (
                    self.game_mode == "abridged"
                    and self.time_limit
                    and self.game_paused
                ):
                    self.board.add_message("Game is paused. Click Continue to resume.")
                    return False
                elif self.development_mode:
                    self.board.add_message(
                        "Current player must complete development before the next player can roll"
                    )
                    return False
                else:
                    return self.play_turn()

            human_players_remaining = any(
                not p.is_ai and not p.voluntary_exit and not p.bankrupt
                for p in self.players
            )

            if (
                not self.current_player_is_ai
                and human_players_remaining
                and self.quit_button.collidepoint(pos)
            ):
                confirm_exit = self.show_exit_confirmation()

                if confirm_exit:
                    current_player = self.logic.players[self.logic.current_player_index]

                    final_assets = self.calculate_player_assets(current_player)

                    result = self.handle_voluntary_exit(
                        current_player["name"], final_assets
                    )

                    if isinstance(result, dict):
                        return result
                    elif result:
                        self.board.add_message(
                            f"{current_player['name']} has voluntarily exited the game"
                        )

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
                if (
                    hasattr(self.logic, "current_auction")
                    and self.logic.current_auction
                ):
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

                        if prop_data.get("owner") == current_player["name"]:
                            print(
                                f"Player {current_player['name']} clicked on their property {prop_data['name']}"
                            )
                            self.selected_property = prop_data
                            self.state = "DEVELOPMENT"
                            return False
                        else:
                            owner = prop_data.get("owner", "Bank")
                            print(
                                f"Property {prop_data['name']} is owned by {owner}, not {current_player['name']}"
                            )
                            self.board.add_message(
                                f"Property {prop_data['name']} is owned by {owner}"
                            )
                    else:
                        print(f"No property data found for position {property_pos}")

        elif self.state == "BUY" and self.current_property is not None:
            current_player = self.logic.players[self.logic.current_player_index]
            if current_player.get("in_jail", False):
                self.board.add_message(
                    f"{current_player['name']} cannot buy property while in jail!"
                )
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

            if auction_result == True and not hasattr(self, "auction_completed"):
                print("Auction completed - changing state to ROLL")
                self.state = "ROLL"
                self.current_property = None
                self.board.update_ownership(self.logic.properties)
                self.update_current_player()
            else:
                print(
                    "Auction continues or completion in progress - maintaining AUCTION state"
                )
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
            hover_buttons = [
                self.roll_button.collidepoint(pos),
                self.quit_button.collidepoint(pos),
            ]

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
        if any_player_moving and event.key not in [
            pygame.K_LEFT,
            pygame.K_RIGHT,
            pygame.K_UP,
            pygame.K_DOWN,
        ]:
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
                    result = self.handle_voluntary_exit(
                        current_player["name"], final_assets
                    )
                    if result:
                        self.board.add_message(
                            f"{current_player['name']} has voluntarily exited the game"
                        )
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
        pygame.draw.rect(
            bg_surface,
            (*ACCENT_COLOR[:3], 230),
            bg_surface.get_rect(),
            border_radius=10,
        )

        for i in range(3):
            alpha = 100 - i * 30
            pygame.draw.rect(
                bg_surface,
                (*ACCENT_COLOR[:3], alpha),
                (-i, -i, bg_width + i * 2, bg_height + i * 2),
                border_radius=10,
            )

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
        pygame.draw.rect(
            self.screen,
            ACCENT_COLOR,
            pygame.Rect(card_x, card_y + header_height - 15, card_width, 15),
        )

        header_text = self.font.render(card["type"], True, WHITE)
        header_shadow = self.font.render(card["type"], True, BLACK)
        header_rect = header_text.get_rect(
            center=(card_x + card_width // 2, card_y + header_height // 2)
        )
        shadow_rect = header_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        self.screen.blit(header_shadow, shadow_rect)
        self.screen.blit(header_text, header_rect)

        player_y = card_y + header_height + 20
        player_text = self.font.render(f"Player: {player['name']}", True, BLACK)
        self.screen.blit(player_text, (card_x + 20, player_y))

        message_y = player_y + 40
        message_lines = self.wrap_text(card["message"], card_width - 40)
        for i, line in enumerate(message_lines):
            message_text = self.small_font.render(line, True, BLACK)
            self.screen.blit(message_text, (card_x + 20, message_y + i * 30))

        continue_y = card_y + card_height - 25
        continue_text = self.small_font.render(
            "Tap or click to continue...", True, GRAY
        )
        continue_rect = continue_text.get_rect(
            centerx=card_x + card_width // 2, bottom=continue_y
        )
        self.screen.blit(continue_text, continue_rect)

    def wrap_text(self, text, max_width):
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            test_surface = self.small_font.render(test_line, True, BLACK)
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []

        if current_line:
            lines.append(" ".join(current_line))

        return lines

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

        self.draw()
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

    def draw_free_parking_pot(self):
        window_size = self.screen.get_size()

        panel_width = 200
        panel_height = 100
        panel_x = 10
        panel_y = 230

        glow_surface = pygame.Surface(
            (panel_width + 10, panel_height + 10), pygame.SRCALPHA
        )
        for i in range(5):
            alpha = int(100 * (1 - i / 5))
            pygame.draw.rect(
                glow_surface,
                (*ACCENT_COLOR[:3], alpha),
                pygame.Rect(i, i, panel_width + 10 - i * 2, panel_height + 10 - i * 2),
                border_radius=10,
            )
        self.screen.blit(glow_surface, (panel_x - 5, panel_y - 5))

        panel = pygame.Surface((panel_width, panel_height))
        panel.fill(UI_BG)
        self.screen.blit(panel, (panel_x, panel_y))

        title_text = self.small_font.render("Free Parking Pot", True, LIGHT_GRAY)
        title_rect = title_text.get_rect(
            centerx=panel_x + panel_width // 2, top=panel_y + 10
        )
        self.screen.blit(title_text, title_rect)

        money_color = SUCCESS_COLOR if self.free_parking_pot > 0 else LIGHT_GRAY
        money_text = self.font.render(f"£{self.free_parking_pot:,}", True, money_color)
        money_rect = money_text.get_rect(
            centerx=panel_x + panel_width // 2, top=title_rect.bottom + 10
        )
        self.screen.blit(money_text, money_rect)

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

        self.draw()
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

