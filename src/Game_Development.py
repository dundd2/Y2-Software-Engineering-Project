import pygame
from src.Game_Logic import GameLogic
from src.Board import Board
from src.Font_Manager import font_manager
from src.UI import DevelopmentNotification

# Color constants
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
UI_BG = (18, 18, 18)
BURGUNDY = (128, 0, 32)
DARK_GREEN = (0, 100, 0)
ACCENT_COLOR = BURGUNDY
ERROR_COLOR = (220, 53, 69)
SUCCESS_COLOR = DARK_GREEN
BUTTON_HOVER = (160, 20, 40)

class GameDevelopment:
    def __init__(self, screen, game_logic: GameLogic, board: Board):
        self.screen = screen
        self.logic = game_logic
        self.board = board
        self.font = font_manager.get_font(24)
        self.small_font = font_manager.get_font(18)
        self.development_mode = False
        self.selected_property = None
        self.dev_notification = None

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


    def draw_development_ui(self, property_data):
        print("\n=== Property Development Debug ===")
        print(f"Drawing development UI for {property_data.get('name', 'Unknown')}")

        if not property_data:
            print("Warning: Property data is None in draw_development_ui")
            return

        current_player = self.logic.players[self.logic.current_player_index]
        player_obj = next(
            (p for p in self.players if p.name == current_player["name"]), None
        )

        if player_obj and player_obj.is_ai:
            print(
                f"Auto-handling development decision for AI player {current_player['name']}"
            )
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

        pygame.draw.rect(
            self.screen,
            WHITE,
            (card_x, card_y, card_width, card_height),
            border_radius=15,
        )

        current_player = self.logic.players[self.logic.current_player_index]

        header_text = self.font.render(
            f"Develop {property_data['name']}", True, ACCENT_COLOR
        )
        self.screen.blit(header_text, (card_x + 20, card_y + 20))

        y_offset = card_y + 70
        padding = 20

        price_text = self.font.render(f"Price: £{property_data['price']}", True, BLACK)
        self.screen.blit(price_text, (card_x + padding, y_offset))
        y_offset += 35

        houses = property_data.get("houses", 0)
        house_text = self.font.render(
            f"Houses: {houses if houses < 5 else '0 (Hotel)'}", True, BLACK
        )
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

        house_cost = property_data.get("house_cost", 0)
        can_build_house = False
        can_build_hotel = False

        if houses < 4:
            can_build_house, error = self.logic.can_build_house(
                property_data, current_player
            )
            upgrade_text = f"Upgrade (-£{house_cost})"
            upgrade_color = ACCENT_COLOR if can_build_house else GRAY
        else:
            can_build_hotel, error = self.logic.can_build_hotel(
                property_data, current_player
            )
            upgrade_text = f"Build Hotel (-£{house_cost})"
            upgrade_color = ACCENT_COLOR if can_build_hotel else GRAY

        self.development_buttons["upgrade"] = pygame.Rect(
            card_x + 20, y_offset, button_width, button_height
        )
        mouse_pos = pygame.mouse.get_pos()
        hover = self.development_buttons["upgrade"].collidepoint(mouse_pos) and (
            can_build_house or can_build_hotel
        )
        color = BUTTON_HOVER if hover else upgrade_color
        pygame.draw.rect(
            self.screen, color, self.development_buttons["upgrade"], border_radius=5
        )

        btn_text = self.small_font.render(upgrade_text, True, WHITE)
        text_rect = btn_text.get_rect(center=self.development_buttons["upgrade"].center)
        self.screen.blit(btn_text, text_rect)
        y_offset += button_height + button_margin

        self.development_buttons["auction"] = pygame.Rect(
            card_x + 20, y_offset, button_width, button_height
        )
        hover = self.development_buttons["auction"].collidepoint(mouse_pos)
        pygame.draw.rect(
            self.screen,
            BUTTON_HOVER if hover else ACCENT_COLOR,
            self.development_buttons["auction"],
            border_radius=5,
        )

        btn_text = self.small_font.render("Auction to Player", True, WHITE)
        text_rect = btn_text.get_rect(center=self.development_buttons["auction"].center)
        self.screen.blit(btn_text, text_rect)
        y_offset += button_height + button_margin

        mortgage_value = property_data.get("price", 0) // 2
        is_mortgaged = property_data.get("is_mortgaged", False)

        if is_mortgaged:
            unmortgage_cost = int(mortgage_value * 1.1)
            can_unmortgage = current_player["money"] >= unmortgage_cost
            mortgage_text = (
                f"Unmortgage (-£{unmortgage_cost})"
                if can_unmortgage
                else "Cannot Unmortgage"
            )
            mortgage_color = ACCENT_COLOR if can_unmortgage else GRAY
        else:
            can_mortgage = property_data.get("houses", 0) == 0
            mortgage_text = (
                f"Mortgage (+£{mortgage_value})" if can_mortgage else "Cannot Mortgage"
            )
            mortgage_color = ACCENT_COLOR if can_mortgage else GRAY

        self.development_buttons["mortgage"] = pygame.Rect(
            card_x + 20, y_offset, button_width, button_height
        )

        if is_mortgaged:
            hover = (
                self.development_buttons["mortgage"].collidepoint(mouse_pos)
                and can_unmortgage
            )
        else:
            hover = (
                self.development_buttons["mortgage"].collidepoint(mouse_pos)
                and can_mortgage
            )

        color = BUTTON_HOVER if hover else mortgage_color
        pygame.draw.rect(
            self.screen, color, self.development_buttons["mortgage"], border_radius=5
        )

        btn_text = self.small_font.render(mortgage_text, True, WHITE)
        text_rect = btn_text.get_rect(
            center=self.development_buttons["mortgage"].center
        )
        self.screen.blit(btn_text, text_rect)
        y_offset += button_height + button_margin

        can_sell = houses > 0
        sell_value = house_cost // 2
        sell_text = (
            f"Sell House (+£{sell_value})"
            if houses > 0 and houses < 5
            else (
                f"Sell Hotel (+£{sell_value * 5})" if houses == 5 else "Nothing to Sell"
            )
        )

        self.development_buttons["sell"] = pygame.Rect(
            card_x + 20, y_offset, button_width, button_height
        )
        hover = self.development_buttons["sell"].collidepoint(mouse_pos) and can_sell
        color = BUTTON_HOVER if hover else (ACCENT_COLOR if can_sell else GRAY)
        pygame.draw.rect(
            self.screen, color, self.development_buttons["sell"], border_radius=5
        )

        btn_text = self.small_font.render(sell_text, True, WHITE)
        text_rect = btn_text.get_rect(center=self.development_buttons["sell"].center)
        self.screen.blit(btn_text, text_rect)
        y_offset += button_height + button_margin

        self.development_buttons["close"] = pygame.Rect(
            card_x + 20, y_offset, button_width, button_height
        )
        hover = self.development_buttons["close"].collidepoint(mouse_pos)
        pygame.draw.rect(
            self.screen,
            BUTTON_HOVER if hover else ERROR_COLOR,
            self.development_buttons["close"],
            border_radius=5,
        )

        btn_text = self.small_font.render("Close", True, WHITE)
        text_rect = btn_text.get_rect(center=self.development_buttons["close"].center)
        self.screen.blit(btn_text, text_rect)

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
