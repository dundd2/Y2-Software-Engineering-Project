import pygame
import sys
import os
from src.Game_Logic import GameLogic
from src.Board import Board
from src.Font_Manager import font_manager

# Color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
UI_BG = (18, 18, 18)
BURGUNDY = (128, 0, 32)
ACCENT_COLOR = BURGUNDY
ERROR_COLOR = (220, 53, 69)
SUCCESS_COLOR = (0, 100, 0)
BUTTON_HOVER = (160, 20, 40)

class GameAuction:
    def __init__(self, screen, game_logic: GameLogic, board: Board):
        self.screen = screen
        self.logic = game_logic
        self.board = board
        self.font = font_manager.get_font(24)
        self.small_font = font_manager.get_font(18)
        self.auction_data = None
        self.auction_bid_amount = ""
        self.auction_just_started = False

    def draw_auction(self, auction_data):
        if self.show_card:
            print("Card is showing - not drawing auction UI")
            return

        if auction_data is None:
            print("Warning: Auction data is None in draw_auction")
            self.state = "ROLL"
            return

        required_keys = [
            "property",
            "current_bid",
            "minimum_bid",
            "highest_bidder",
            "current_bidder_index",
            "active_players",
        ]

        for key in required_keys:
            if key not in auction_data:
                print(
                    f"Warning: Auction data missing key '{key}' - resetting to ROLL state"
                )
                self.state = "ROLL"
                return

        if (
            not isinstance(auction_data["property"], dict)
            or "name" not in auction_data["property"]
        ):
            print("Warning: Auction property data is invalid - resetting to ROLL state")
            self.state = "ROLL"
            return

        current_bidder_index = auction_data.get("current_bidder_index", 0)
        if current_bidder_index < len(auction_data["active_players"]):
            current_bidder = auction_data["active_players"][current_bidder_index]
            if current_bidder.get("is_ai", False):
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
            current_bidder = auction_data["active_players"][
                auction_data["current_bidder_index"]
            ]
            print(f"Current bidder: {current_bidder['name']}")

        print(f"Passed players: {auction_data.get('passed_players', set())}")
        print(
            f"Active players: {[p['name'] for p in auction_data.get('active_players', [])]}"
        )
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
            shadow_rect = pygame.Rect(
                card_x + shadow_offset, card_y + shadow_offset, card_width, card_height
            )
            shadow = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            shadow_alpha = 100 - (i * 20)
            pygame.draw.rect(
                shadow, (*BLACK, shadow_alpha), shadow.get_rect(), border_radius=15
            )
            self.screen.blit(shadow, shadow_rect)

        pygame.draw.rect(
            self.screen,
            WHITE,
            (card_x, card_y, card_width, card_height),
            border_radius=15,
        )

        current_time = pygame.time.get_ticks()
        time_remaining = max(
            0,
            (auction_data["start_time"] + auction_data["duration"] - current_time)
            // 1000,
        )

        current_bidder = auction_data["active_players"][
            auction_data["current_bidder_index"]
        ]
        current_bidder_obj = next(
            (p for p in self.players if p.name == current_bidder["name"]), None
        )

        header_color = ERROR_COLOR if time_remaining <= 10 else ACCENT_COLOR
        header_text = self.font.render(
            f"{current_bidder['name']}'s Turn", True, header_color
        )
        timer_text = self.font.render(f"Time: {time_remaining}s", True, header_color)

        header_y = card_y + 20
        self.screen.blit(header_text, (card_x + 20, header_y))
        self.screen.blit(
            timer_text, (card_x + card_width - timer_text.get_width() - 20, header_y)
        )

        title_y = header_y + 50
        title = self.font.render("AUCTION", True, BLACK)
        property_name = self.font.render(auction_data["property"]["name"], True, BLACK)
        self.screen.blit(
            title, (card_x + (card_width - title.get_width()) // 2, title_y)
        )
        self.screen.blit(property_name, (card_x + 20, title_y + 40))

        info_y = title_y + 90
        current_bid = self.font.render(
            f"Current Bid: £{auction_data['current_bid']}", True, BLACK
        )
        min_bid = self.font.render(
            f"Minimum Bid: £{auction_data['minimum_bid']}", True, BLACK
        )
        self.screen.blit(current_bid, (card_x + 20, info_y))
        self.screen.blit(min_bid, (card_x + 20, info_y + 40))

        if auction_data["highest_bidder"]:
            highest_y = info_y + 80
            highest_text = self.font.render(
                f"Highest Bidder: {auction_data['highest_bidder']['name']}",
                True,
                SUCCESS_COLOR,
            )
            self.screen.blit(highest_text, (card_x + 20, highest_y))

        can_bid = current_bidder["name"] not in auction_data.get(
            "passed_players", set()
        )
        is_human = current_bidder_obj and not current_bidder_obj.is_ai

        if is_human and can_bid:
            self.auction_input = pygame.Rect(
                card_x + 20, card_y + card_height - 120, 200, 40
            )
            pygame.draw.rect(self.screen, WHITE, self.auction_input)
            pygame.draw.rect(self.screen, ACCENT_COLOR, self.auction_input, 2)

            if self.auction_bid_amount:
                bid_text = self.font.render(self.auction_bid_amount, True, BLACK)
            else:
                bid_text = self.small_font.render("Enter bid amount...", True, GRAY)
            self.screen.blit(
                bid_text,
                (
                    self.auction_input.x + 10,
                    self.auction_input.y
                    + (self.auction_input.height - bid_text.get_height()) // 2,
                ),
            )

            button_width = 100
            button_height = 40
            button_margin = 20

            self.auction_buttons = {
                "bid": pygame.Rect(
                    card_x + 20, card_y + card_height - 60, button_width, button_height
                ),
                "pass": pygame.Rect(
                    card_x + 20 + button_width + button_margin,
                    card_y + card_height - 60,
                    button_width,
                    button_height,
                ),
            }

            mouse_pos = pygame.mouse.get_pos()
            for btn_name, btn_rect in self.auction_buttons.items():
                mouse_over = btn_rect.collidepoint(mouse_pos)
                color = BUTTON_HOVER if mouse_over else ACCENT_COLOR
                pygame.draw.rect(self.screen, color, btn_rect, border_radius=5)

                btn_text = self.font.render(btn_name.title(), True, WHITE)
                self.screen.blit(
                    btn_text,
                    (
                        btn_rect.centerx - btn_text.get_width() // 2,
                        btn_rect.centery - btn_text.get_height() // 2,
                    ),
                )

        if auction_data.get("passed_players"):
            passed_text = self.small_font.render(
                "Passed: " + ", ".join(auction_data["passed_players"]), True, GRAY
            )
            self.screen.blit(passed_text, (card_x + 20, card_y + card_height - 30))

    def handle_auction_input(self, event):
        if (
            not hasattr(self.logic, "current_auction")
            or self.logic.current_auction is None
        ):
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
            print(
                f"Invalid current_bidder_index: {auction_data['current_bidder_index']} (active players: {len(auction_data['active_players'])})"
            )
            return

        current_bidder = auction_data["active_players"][
            auction_data["current_bidder_index"]
        ]
        current_bidder_obj = next(
            (p for p in self.players if p.name == current_bidder["name"]), None
        )

        print(f"Processing auction input for {current_bidder['name']}")

        if current_bidder.get("in_jail", False):
            self.board.add_message(
                f"{current_bidder['name']} cannot bid while in jail!"
            )
            auction_data["passed_players"].add(current_bidder["name"])
            self.logic.move_to_next_bidder()
            return

        if current_bidder_obj and not current_bidder_obj.is_ai:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.auction_bid_amount = self.auction_bid_amount[:-1]
                    print(
                        f"Backspace pressed - new bid amount: {self.auction_bid_amount}"
                    )

                elif event.key in [
                    pygame.K_0,
                    pygame.K_1,
                    pygame.K_2,
                    pygame.K_3,
                    pygame.K_4,
                    pygame.K_5,
                    pygame.K_6,
                    pygame.K_7,
                    pygame.K_8,
                    pygame.K_9,
                ]:
                    if len(self.auction_bid_amount) < 6:
                        self.auction_bid_amount += event.unicode
                        print(
                            f"Number key pressed - new bid amount: {self.auction_bid_amount}"
                        )

                elif event.key == pygame.K_RETURN:
                    print(
                        f"Enter key pressed - submitting bid: {self.auction_bid_amount}"
                    )
                    self._process_auction_bid(current_bidder)

                elif event.key == pygame.K_ESCAPE:
                    print(f"Escape key pressed - passing")
                    success, message = self.logic.process_auction_pass(current_bidder)
                    if message:
                        self.board.add_message(message)
                    if success:
                        print(f"{current_bidder['name']} passed successfully")
                    else:
                        print(f"Pass failed: {message}")

    def _process_auction_bid(self, current_bidder):
        try:
            bid_amount = int(self.auction_bid_amount or "0")
            success, message = self.logic.process_auction_bid(
                current_bidder, bid_amount
            )
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

    def handle_auction_click(self, pos):
        print("\n=== Auction Click Debug ===")

        if (
            not hasattr(self.logic, "current_auction")
            or self.logic.current_auction is None
        ):
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

        current_bidder = auction_data["active_players"][
            auction_data["current_bidder_index"]
        ]

        if current_bidder.get("exited", False):
            print(f"Current bidder {current_bidder['name']} has exited - skipping")
            auction_data["passed_players"].add(current_bidder["name"])
            self.logic.move_to_next_bidder()
            return False

        current_bidder_obj = next(
            (p for p in self.players if p.name == current_bidder["name"]), None
        )

        if not current_bidder_obj or (
            hasattr(current_bidder_obj, "voluntary_exit")
            and current_bidder_obj.voluntary_exit
        ):
            print(
                f"Current bidder {current_bidder['name']} doesn't have UI representation or has voluntarily exited"
            )
            auction_data["passed_players"].add(current_bidder["name"])
            self.logic.move_to_next_bidder()
            return False

        if current_bidder.get("in_jail", False) and current_bidder.get("is_ai", False):
            print(f"AI bidder {current_bidder['name']} is in jail - auto-passing")
            auction_data["passed_players"].add(current_bidder["name"])
            self.logic.move_to_next_bidder()
            return False

        print(f"Current bidder: {current_bidder['name']}")
        print(f"Is AI: {current_bidder_obj.is_ai if current_bidder_obj else 'Unknown'}")
        print(f"Current bid amount input: {self.auction_bid_amount}")

        print(f"Bid button rect: {self.auction_buttons['bid']}")
        print(f"Pass button rect: {self.auction_buttons['pass']}")
        print(f"Click position: {pos}")
        print(f"Bid button collision: {self.auction_buttons['bid'].collidepoint(pos)}")
        print(
            f"Pass button collision: {self.auction_buttons['pass'].collidepoint(pos)}"
        )

        if not current_bidder_obj or current_bidder_obj.is_ai:
            print("Current bidder is AI or not found - ignoring click")
            return False

        if self.auction_buttons["bid"].collidepoint(pos):
            print(f"Bid button clicked by {current_bidder['name']}")
            try:
                bid_amount = int(self.auction_bid_amount or "0")
                success, message = self.logic.process_auction_bid(
                    current_bidder, bid_amount
                )
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

        elif self.auction_buttons["pass"].collidepoint(pos):
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

            if hasattr(self.logic, "current_auction") and self.logic.current_auction:
                auction_data = self.logic.current_auction
                if auction_data and auction_data.get("highest_bidder"):
                    winner = auction_data["highest_bidder"]
                    property_name = auction_data["property"]["name"]
                    bid_amount = auction_data["current_bid"]
                    self.board.add_message(
                        f"{winner['name']} won {property_name} for £{bid_amount}"
                    )
                else:
                    property_name = auction_data["property"]["name"]
                    self.board.add_message(f"No one bid on {property_name}")

            self.auction_end_time = pygame.time.get_ticks()
            self.auction_end_delay = 3000
            self.auction_completed = True

            self.board.update_ownership(self.logic.properties)
            return False

        print("Auction continues - returning False")
        return False
