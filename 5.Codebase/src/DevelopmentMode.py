# Property Tycoon DevelopmentMode.py
# Contains the classes for the development mode, such as the development notification, and the development mode.

import pygame
import math
import os
from src.Font_Manager import font_manager

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
YELLOW = (255, 255, 0)

ACCENT_COLOR = BURGUNDY
BUTTON_HOVER = (160, 20, 40)
ERROR_COLOR = (220, 53, 69)
SUCCESS_COLOR = DARK_GREEN
MODE_COLOR = DARK_BLUE
TIME_COLOR = (255, 180, 100)
HUMAN_COLOR = DARK_GREEN
AI_COLOR = DARK_RED

GROUP_COLORS = {
    "Brown": (102, 51, 0),
    "Blue": (0, 200, 255),
    "Purple": (128, 0, 128),
    "Orange": (255, 128, 0),
    "Red": (255, 0, 0),
    "Yellow": (255, 236, 93),
    "Green": (0, 153, 0),
    "Deep blue": (0, 0, 153),
    "Stations": (128, 128, 128),
    "Utilities": (192, 192, 192),
}


class DevelopmentMode:
    def __init__(self, game, game_actions):
        self.game = game
        self.game_actions = game_actions
        self.screen = game.screen
        self.font = game.font
        self.small_font = game.small_font
        self.tiny_font = game.tiny_font

        self.is_active = False
        self.buttons = {}
        self.last_star_flash_time = 0
        self.show_property_stars = True

    def activate(self, player):
        if player.get("is_ai", False):
            if self.can_develop_ai(player):
                self.is_active = True
                self.game.selected_property = None
                print(f"Development mode ACTIVATED for AI {player['name']}")
                return True
            else:
                self.is_active = False
                print(
                    f"Development mode NOT activated for AI {player['name']} (cannot develop)"
                )
                return False
        else:
            owned_properties = [
                prop
                for prop in self.game.logic.properties.values()
                if prop.get("owner") == player["name"]
            ]
            if owned_properties:
                self.is_active = True
                self.game.selected_property = None
                print(f"Development mode ACTIVATED for human player {player['name']}")
                if self.game.lap_count.get(player["name"], 0) >= 1:
                    self.game.board.add_message(
                        "Development Mode: Click on your properties to manage them"
                    )
                return True
            else:
                self.is_active = False
                print(
                    f"Development mode NOT activated for human player {player['name']} (no properties)"
                )
                return False

    def can_develop_ai(self, player):
        if not player or not isinstance(player, dict):
            print("Development: Cannot develop - Invalid player data")
            return False

        if self.game.lap_count.get(player["name"], 0) < 1:
            print(
                f"Development: Cannot develop - {player['name']} has not completed a lap."
            )
            return False

        owned_properties = [
            prop
            for prop in self.game.logic.properties.values()
            if prop.get("owner") == player["name"]
        ]

        if not owned_properties:
            print(f"Development: Cannot develop - {player['name']} owns no properties")
            return False

        for prop in owned_properties:
            can_build_house, _ = self.game.logic.can_build_house(prop, player)
            can_build_hotel, _ = self.game.logic.can_build_hotel(prop, player)
            can_mortgage = prop.get("houses", 0) == 0 and not prop.get(
                "is_mortgaged", False
            )
            can_unmortgage = prop.get("is_mortgaged", False) and player["money"] >= int(
                (prop.get("price", 0) // 2) * 1.1
            )
            can_sell = prop.get("houses", 0) > 0

            if (
                can_build_house
                or can_build_hotel
                or can_mortgage
                or can_unmortgage
                or can_sell
            ):
                print(
                    f"Development: {player['name']} CAN develop (found developable property: {prop.get('name')})"
                )
                return True

        print(
            f"Development: Cannot develop - {player['name']} owns properties, but none are currently developable/manageable."
        )
        return False

    def deactivate(self):
        print("Development mode DEACTIVATED")
        self.is_active = False
        self.game.selected_property = None
        self.buttons = {}
        if self.game.state == "DEVELOPMENT":
            self.game.state = "ROLL"

    def draw(self, mouse_pos):
        if not self.is_active:
            return

        if self.game.selected_property:
            self._draw_development_ui(self.game.selected_property, mouse_pos)
        elif self.game.state == "DEVELOPMENT":
            self._draw_property_stars()

    def handle_click(self, pos):
        if not self.is_active:
            return None

        current_player = self.game.logic.players[self.game.logic.current_player_index]

        if self.game.selected_property:
            clicked_action = None
            for action, button_rect in self.buttons.items():
                if button_rect.collidepoint(pos):
                    clicked_action = action
                    break

            if clicked_action:
                print(f"Development UI button clicked: {clicked_action}")
                if clicked_action == "close":
                    self.game.selected_property = None
                    return False
                elif clicked_action == "build_house":
                    result = self.game.logic.build_house(
                        self.game.selected_property, current_player
                    )
                    if result:
                        self.game.board.add_message(
                            f"{current_player['name']} built a house on {self.game.selected_property['name']}"
                        )
                        self.game.board.update_ownership(self.game.logic.properties)
                    return False
                elif clicked_action == "build_hotel":
                    result = self.game.logic.build_hotel(
                        self.game.selected_property, current_player
                    )
                    if result:
                        self.game.board.add_message(
                            f"{current_player['name']} built a hotel on {self.game.selected_property['name']}"
                        )
                        self.game.board.update_ownership(self.game.logic.properties)
                    return False
                elif clicked_action == "sell_property":
                    houses = self.game.selected_property.get("houses", 0)
                    if houses == 0:
                        property_value = self.game.selected_property.get("price", 0)
                        is_mortgaged = self.game.selected_property.get(
                            "is_mortgaged", False
                        )
                        sell_property_value = (
                            property_value if not is_mortgaged else property_value // 2
                        )

                        current_player["money"] += sell_property_value

                        self.game.selected_property["owner"] = None
                        if is_mortgaged:
                            self.game.selected_property["is_mortgaged"] = False

                        property_name = self.game.selected_property["name"]
                        sell_message = f"{current_player['name']} sold {property_name} to the bank for £{sell_property_value}"

                        self.game.selected_property = None
                        self.game.state = "ROLL"

                        self.game.board.add_message(sell_message)
                        self.game.board.update_ownership(self.game.logic.properties)

                        owned_properties = [
                            prop
                            for prop in self.game.logic.properties.values()
                            if prop.get("owner") == current_player["name"]
                        ]

                        if not owned_properties:
                            print(
                                "Player sold their last property - deactivating development mode."
                            )
                            self.deactivate()

                    else:
                        self.game.board.add_message(
                            "Cannot sell property with buildings. Sell houses/hotel first."
                        )
                    return False
                elif clicked_action == "mortgage":
                    is_mortgaged = self.game.selected_property.get(
                        "is_mortgaged", False
                    )
                    if is_mortgaged:
                        result = self.game.logic.unmortgage_property(
                            self.game.selected_property, current_player
                        )
                        if result:
                            self.game.board.add_message(
                                f"{current_player['name']} unmortgaged {self.game.selected_property['name']}"
                            )
                    else:
                        result = self.game.logic.mortgage_property(
                            self.game.selected_property, current_player
                        )
                        if result:
                            self.game.board.add_message(
                                f"{current_player['name']} mortgaged {self.game.selected_property['name']}"
                            )
                    if result:
                        self.game.board.update_ownership(self.game.logic.properties)
                    return False
                elif clicked_action == "sell":
                    houses = self.game.selected_property.get("houses", 0)
                    if houses == 5:
                        result = self.game.logic.sell_hotel(
                            self.game.selected_property, current_player
                        )
                        if result:
                            self.game.board.add_message(
                                f"{current_player['name']} sold a hotel from {self.game.selected_property['name']}"
                            )
                    elif houses > 0:
                        result = self.game.logic.sell_house(
                            self.game.selected_property, current_player
                        )
                        if result:
                            self.game.board.add_message(
                                f"{current_player['name']} sold a house from {self.game.selected_property['name']}"
                            )
                    else:
                        self.game.board.add_message("No houses/hotels to sell")
                        result = False
                    if result:
                        self.game.board.update_ownership(self.game.logic.properties)
                    return False

            window_size = self.screen.get_size()
            card_width = int(window_size[0] * 0.35)
            card_height = int(window_size[1] * 0.62)
            card_x = (window_size[0] - card_width) // 2
            card_y = (window_size[1] - card_height) // 2
            ui_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            if ui_rect.collidepoint(pos):
                return False

        property_pos_index = self.game.board.property_clicked(pos)
        if property_pos_index:
            pos_str = str(property_pos_index)
            if pos_str in self.game.logic.properties:
                prop_data = self.game.logic.properties[pos_str]
                if prop_data.get("owner") == current_player["name"]:
                    print(f"Selected property for development: {prop_data['name']}")
                    self.game.selected_property = prop_data
                    self.game.state = "DEVELOPMENT"
                    return False
                else:
                    owner = prop_data.get("owner", "Bank")
                    self.game.board.add_message(
                        f"Property {prop_data['name']} is owned by {owner}"
                    )
                    return False

        return None

    def handle_key(self, event):
        if not self.is_active:
            return None

        current_player = self.game.logic.players[self.game.logic.current_player_index]
        if not current_player.get("is_ai", False):
            return None

        if event.key == pygame.K_ESCAPE and self.game.selected_property:
            self.game.selected_property = None
            return False

        if self.game.selected_property:
            if event.key == pygame.K_1:
                houses = self.game.selected_property.get("houses", 0)
                if houses < 4:
                    result = self.game.logic.build_house(
                        self.game.selected_property, current_player
                    )
                    if result:
                        self.game.board.add_message(
                            f"{current_player['name']} built a house on {self.game.selected_property['name']}"
                        )
                else:
                    result = self.game.logic.build_hotel(
                        self.game.selected_property, current_player
                    )
                    if result:
                        self.game.board.add_message(
                            f"{current_player['name']} built a hotel on {self.game.selected_property['name']}"
                        )
                if result:
                    self.game.board.update_ownership(self.game.logic.properties)
                return False

            elif event.key == pygame.K_2:
                is_mortgaged = self.game.selected_property.get("is_mortgaged", False)
                if is_mortgaged:
                    result = self.game.logic.unmortgage_property(
                        self.game.selected_property, current_player
                    )
                    if result:
                        self.game.board.add_message(
                            f"{current_player['name']} unmortgaged {self.game.selected_property['name']}"
                        )
                else:
                    result = self.game.logic.mortgage_property(
                        self.game.selected_property, current_player
                    )
                    if result:
                        self.game.board.add_message(
                            f"{current_player['name']} mortgaged {self.game.selected_property['name']}"
                        )
                if result:
                    self.game.board.update_ownership(self.game.logic.properties)
                return False

            elif event.key == pygame.K_3:
                houses = self.game.selected_property.get("houses", 0)
                if houses == 5:
                    result = self.game.logic.sell_hotel(
                        self.game.selected_property, current_player
                    )
                    if result:
                        self.game.board.add_message(
                            f"{current_player['name']} sold a hotel from {self.game.selected_property['name']}"
                        )
                elif houses > 0:
                    result = self.game.logic.sell_house(
                        self.game.selected_property, current_player
                    )
                    if result:
                        self.game.board.add_message(
                            f"{current_player['name']} sold a house from {self.game.selected_property['name']}"
                        )
                else:
                    self.game.board.add_message("No houses/hotels to sell")
                    result = False
                if result:
                    self.game.board.update_ownership(self.game.logic.properties)
                return False

            elif event.key == pygame.K_4:
                self.game.selected_property["owner"] = None
                self.game.board.add_message(
                    f"{current_player['name']} put {self.game.selected_property['name']} up for auction"
                )
                self.game_actions.start_auction(self.game.selected_property)
                self.game.board.update_ownership(self.game.logic.properties)
                self.game.selected_property = None
                self.deactivate()
                self.game.state = "AUCTION"
                return False

        return None

    def _draw_property_stars(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_star_flash_time >= 500:
            self.last_star_flash_time = current_time
            self.show_property_stars = not self.show_property_stars

        if not self.show_property_stars:
            return

        current_player_logic = self.game.logic.players[
            self.game.logic.current_player_index
        ]

        owned_properties = [
            prop
            for prop in self.game.logic.properties.values()
            if prop.get("owner") == current_player_logic["name"]
        ]

        for prop in owned_properties:
            if "position" in prop:
                position = int(prop["position"])
                property_center = self.game.board.get_property_position(position)
                if property_center:
                    self._draw_star(property_center[0], property_center[1])

    def _draw_star(self, x, y):
        size = 15
        points = []
        for i in range(10):
            angle = math.pi / 2 + (2 * math.pi / 10) * i
            radius = size / 2 if i % 2 == 0 else size / 4
            point_x = x + radius * math.cos(angle)
            point_y = y + radius * math.sin(angle)
            points.append((point_x, point_y))

        pygame.draw.polygon(self.screen, YELLOW, points)
        pygame.draw.polygon(self.screen, BLACK, points, 1)

    def _draw_development_ui(self, property_data, mouse_pos):
        window_size = self.screen.get_size()
        card_width = int(window_size[0] * 0.3)
        card_height = int(window_size[1] * 0.6)
        card_x = (window_size[0] - card_width) // 2
        card_y = (window_size[1] - card_height) // 2

        overlay = pygame.Surface(window_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        shadow_offset = 6
        shadow_rect = pygame.Rect(
            card_x + shadow_offset, card_y + shadow_offset, card_width, card_height
        )
        shadow = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 140), shadow.get_rect(), border_radius=15)
        self.screen.blit(shadow, shadow_rect)

        pygame.draw.rect(
            self.screen,
            WHITE,
            (card_x, card_y, card_width, card_height),
            border_radius=15,
        )

        current_player = self.game.logic.players[self.game.logic.current_player_index]

        header_height = 60
        if property_data.get("group"):
            group_color = GROUP_COLORS.get(property_data["group"], GRAY)
            pygame.draw.rect(
                self.screen,
                group_color,
                (card_x, card_y, card_width, header_height),
                border_top_left_radius=15,
                border_top_right_radius=15,
            )
            gradient = pygame.Surface((card_width, header_height), pygame.SRCALPHA)
            for i in range(header_height):
                alpha = int(128 * (1 - i / header_height))
                pygame.draw.line(
                    gradient, (255, 255, 255, alpha), (0, i), (card_width, i)
                )
            self.screen.blit(gradient, (card_x, card_y))

        close_btn_size = 24
        close_btn_margin = 10
        close_btn_rect = pygame.Rect(
            card_x + card_width - close_btn_size - close_btn_margin,
            card_y + close_btn_margin,
            close_btn_size,
            close_btn_size,
        )
        self.buttons["close"] = close_btn_rect
        pygame.draw.circle(
            self.screen, ERROR_COLOR, close_btn_rect.center, close_btn_size // 2
        )

        line_color = WHITE
        line_width = 2
        offset = close_btn_size // 4
        pygame.draw.line(
            self.screen,
            line_color,
            (close_btn_rect.left + offset, close_btn_rect.top + offset),
            (close_btn_rect.right - offset, close_btn_rect.bottom - offset),
            line_width,
        )
        pygame.draw.line(
            self.screen,
            line_color,
            (close_btn_rect.right - offset, close_btn_rect.top + offset),
            (close_btn_rect.left + offset, close_btn_rect.bottom - offset),
            line_width,
        )

        header_text = self.font.render(
            property_data["name"],
            True,
            WHITE if property_data.get("group") else ACCENT_COLOR,
        )
        header_rect = header_text.get_rect(
            center=(card_x + card_width // 2, card_y + header_height // 2)
        )
        self.screen.blit(header_text, header_rect)

        y_offset = card_y + header_height + 15
        padding = 20
        info_font = self.small_font
        line_height = info_font.get_height() + 5

        info_section_height = 100
        pygame.draw.rect(
            self.screen,
            (245, 245, 245),
            (card_x + padding, y_offset, card_width - 2 * padding, info_section_height),
            border_radius=8,
        )

        y_info = y_offset + 10
        price_text = info_font.render(
            f"💰 Price: £{property_data['price']}", True, BLACK
        )
        self.screen.blit(price_text, (card_x + padding + 8, y_info))

        houses = property_data.get("houses", 0)
        house_symbol = "🏠" if houses < 5 else "🏨"
        house_text = info_font.render(
            f"{house_symbol} Buildings: {houses if houses < 5 else 'Hotel'}",
            True,
            BLACK,
        )
        self.screen.blit(house_text, (card_x + padding + 8, y_info + line_height))

        rent = self.game.logic.calculate_space_rent(property_data, current_player)
        rent_text = info_font.render(f"💲 Rent: £{rent}", True, DARK_GREEN)
        self.screen.blit(rent_text, (card_x + padding + 8, y_info + line_height * 2))

        if property_data.get("is_mortgaged", False):
            mortgage_text = info_font.render("🏦 Status: MORTGAGED", True, ERROR_COLOR)
            self.screen.blit(
                mortgage_text, (card_x + padding + 8, y_info + line_height * 3)
            )
        else:
            mortgage_val = property_data.get("price", 0) // 2
            mortgage_text = info_font.render(
                f"🏦 Mortgage: £{mortgage_val}", True, GRAY
            )
            self.screen.blit(
                mortgage_text, (card_x + padding + 8, y_info + line_height * 3)
            )

        y_offset += info_section_height + 20

        button_width = card_width - (padding * 2.5)
        button_height = 35
        button_margin = 8

        section_label = info_font.render("Development Actions", True, DARK_BLUE)
        self.screen.blit(section_label, (card_x + padding, y_offset))
        y_offset += 25

        house_cost = property_data.get("house_cost", property_data.get("price", 0) // 2)
        can_build_house, house_error = self.game.logic.can_build_house(
            property_data, current_player
        )
        can_build_hotel, hotel_error = self.game.logic.can_build_hotel(
            property_data, current_player
        )

        can_build_house_ui = houses < 4 and can_build_house
        house_text = (
            f"Add House (£{house_cost})" if can_build_house_ui else f"Cannot Add House"
        )

        self.buttons["build_house"] = pygame.Rect(
            card_x + padding, y_offset, button_width, button_height
        )
        self._draw_button(
            self.buttons["build_house"],
            house_text,
            mouse_pos,
            active=can_build_house_ui,
            color=SUCCESS_COLOR,
        )
        y_offset += button_height + button_margin

        can_build_hotel_ui = houses == 4 and can_build_hotel
        hotel_text = (
            f"Add Hotel (£{house_cost})" if can_build_hotel_ui else f"Cannot Add Hotel"
        )

        self.buttons["build_hotel"] = pygame.Rect(
            card_x + padding, y_offset, button_width, button_height
        )
        self._draw_button(
            self.buttons["build_hotel"],
            hotel_text,
            mouse_pos,
            active=can_build_hotel_ui,
            color=SUCCESS_COLOR,
        )
        y_offset += button_height + button_margin

        section_label = info_font.render("Property Management", True, DARK_BLUE)
        self.screen.blit(section_label, (card_x + padding, y_offset))
        y_offset += 25

        can_sell = houses > 0
        sell_value = house_cost // 2
        sell_text = "No Buildings to Sell"
        if houses == 5:
            sell_text = f"Sell Hotel (£{sell_value * 5})"
        elif houses > 0:
            sell_text = f"Sell House (£{sell_value})"

        self.buttons["sell"] = pygame.Rect(
            card_x + padding, y_offset, button_width, button_height
        )
        self._draw_button(
            self.buttons["sell"],
            sell_text,
            mouse_pos,
            active=can_sell,
            color=MODE_COLOR,
        )
        y_offset += button_height + button_margin

        property_value = property_data.get("price", 0)
        is_mortgaged = property_data.get("is_mortgaged", False)
        can_sell_property = houses == 0
        sell_property_value = (
            property_value if not is_mortgaged else property_value // 2
        )

        sell_property_text = (
            f"Sell Property (£{sell_property_value})"
            if can_sell_property
            else "Remove Buildings First"
        )

        self.buttons["sell_property"] = pygame.Rect(
            card_x + padding, y_offset, button_width, button_height
        )
        self._draw_button(
            self.buttons["sell_property"],
            sell_property_text,
            mouse_pos,
            active=can_sell_property,
            color=ERROR_COLOR,
        )
        y_offset += button_height + button_margin

        mortgage_value = property_data.get("price", 0) // 2
        if is_mortgaged:
            unmortgage_cost = int(mortgage_value * 1.1)
            can_unmortgage = current_player["money"] >= unmortgage_cost
            mortgage_text = (
                f"Pay Unmortgage (£{unmortgage_cost})"
                if can_unmortgage
                else "Cannot Unmortgage"
            )
            can_mortgage_action = can_unmortgage
        else:
            can_mortgage = property_data.get("houses", 0) == 0
            mortgage_text = (
                f"Get Mortgage (£{mortgage_value})"
                if can_mortgage
                else "Sell Buildings First"
            )
            can_mortgage_action = can_mortgage

        self.buttons["mortgage"] = pygame.Rect(
            card_x + padding, y_offset, button_width, button_height
        )
        self._draw_button(
            self.buttons["mortgage"],
            mortgage_text,
            mouse_pos,
            active=can_mortgage_action,
            color=MODE_COLOR,
        )

        if "close" not in self.buttons or close_btn_rect != self.buttons["close"]:
            y_offset += button_height + button_margin * 1.5

            self.buttons["close_bottom"] = pygame.Rect(
                card_x + padding, y_offset, button_width, button_height
            )
            self._draw_button(
                self.buttons["close_bottom"],
                "Close Window",
                mouse_pos,
                active=True,
                color=ERROR_COLOR,
            )

    def _draw_button(
        self, button_rect, text, mouse_pos, active=True, color=ACCENT_COLOR
    ):
        hover = button_rect.collidepoint(mouse_pos) and active

        if not active:
            base_color = GRAY
        else:
            base_color = BUTTON_HOVER if hover else color

        shadow_rect_copy = button_rect.copy()
        shadow_rect_copy.y += 4
        shadow = pygame.Surface(button_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*BLACK, 128), shadow.get_rect(), border_radius=10)
        self.screen.blit(shadow, shadow_rect_copy)

        button_surface = pygame.Surface(button_rect.size, pygame.SRCALPHA)

        pygame.draw.rect(
            button_surface, base_color, button_surface.get_rect(), border_radius=10
        )

        gradient = pygame.Surface(button_rect.size, pygame.SRCALPHA)
        for i in range(button_rect.height):
            alpha = 255 - int(i * 1.2)
            pygame.draw.line(gradient, (*WHITE, alpha), (0, i), (button_rect.width, i))
        button_surface.blit(gradient, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        border_color = GOLD if hover else CREAM
        pygame.draw.rect(
            button_surface,
            border_color,
            button_surface.get_rect(),
            width=2,
            border_radius=10,
        )

        if hover:
            highlight = pygame.Surface(button_rect.size, pygame.SRCALPHA)
            highlight.fill((255, 255, 255, 60))
            button_surface.blit(highlight, (0, 0))

        self.screen.blit(button_surface, button_rect)

        text_color = CREAM if active else LIGHT_GRAY
        text_shadow_surf = self.small_font.render(text, True, BLACK)
        text_surf = self.small_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=button_rect.center)
        shadow_text_rect = text_rect.copy()
        shadow_text_rect.topleft = (text_rect.left + 1, text_rect.top + 1)

        self.screen.blit(text_shadow_surf, shadow_text_rect)
        self.screen.blit(text_surf, text_rect)
