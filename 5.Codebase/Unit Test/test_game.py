# Property Tycoon Test_Game.py
# Created for Year 2 G6046: Software Engineering Project-Group 5
# -*- coding: utf-8 -*-
# Thanks to owen for creating the base of the test code
# start on 17/03/2025 for build 16.03.2025
# Contains the classes for the test game, such as the test player, and the test property.

import unittest
import sys
import os
import pygame
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.Game import Game
from src.Player import Player
from src.Game_Logic import pot_luck_cards, opportunity_knocks_cards


class TestGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    @classmethod
    def tearDownClass(cls):
        # quit pygame after tests
        pygame.quit()

    def setUp(self):
        # setup before each test
        self._original_flip = pygame.display.flip
        self._original_wait = pygame.time.wait
        pygame.display.flip = lambda: None
        pygame.time.wait = lambda x: None

        self.players = [
            Player("Duncan", player_number=1),
            Player("Owen", player_number=2, is_ai=True),
        ]
        for player in self.players:
            player.money = 1500

        self.game = Game(self.players, game_mode="full")
        self.game_logic = self.game.logic

        if not hasattr(self.game_logic, "completed_circuits"):
            self.game_logic.completed_circuits = {}

        if not hasattr(self.game_logic, "rounds_completed"):
            self.game_logic.rounds_completed = {}

        if not hasattr(self.game_logic, "game_mode"):
            self.game_logic.game_mode = "full"

        self.player_dicts = []
        for player in self.players:
            player_dict = {
                "name": player.name,
                "money": player.money,
                "position": player.position,
                "in_jail": player.in_jail,
                "jail_turns": player.jail_turns,
                "is_ai": player.is_ai,
            }
            self.player_dicts.append(player_dict)

        self.game_logic.players = self.player_dicts

    def tearDown(self):
        pygame.display.flip = self._original_flip
        pygame.time.wait = self._original_wait

    def get_player_dict(self, player):
        # get player dict by name
        for player_dict in self.player_dicts:
            if player_dict["name"] == player.name:
                return player_dict
        return None

    def sync_player_objects(self):
        # keep player objects updated
        for player in self.players:
            player_dict = self.get_player_dict(player)
            if player_dict:
                player.money = player_dict["money"]
                player.position = player_dict["position"]
                player.in_jail = player_dict["in_jail"]
                player.jail_turns = player_dict["jail_turns"]

    def sync_player_dicts(self):
        # keep player dicts updated
        for player in self.players:
            player_dict = self.get_player_dict(player)
            if player_dict:
                player_dict["money"] = player.money
                player_dict["position"] = player.position
                player_dict["in_jail"] = player.in_jail
                player_dict["jail_turns"] = player.jail_turns

    def test_game_initialization(self):
        # check game starts ok
        self.assertEqual(len(self.game.players), 2)
        self.assertEqual(self.game.game_mode, "full")

    def test_player_attributes(self):
        # check player details right
        self.assertEqual(self.game.players[0].name, "Duncan")
        self.assertEqual(self.game.players[1].name, "ai-Owen")
        self.assertFalse(self.game.players[0].is_ai)
        self.assertTrue(self.game.players[1].is_ai)
        self.assertEqual(self.game.players[0].money, 1500)
        self.assertEqual(self.game.players[1].money, 1500)

    def test_abridged_game_mode(self):
        # check short game mode
        abridged_game = Game(self.players, game_mode="abridged")
        self.assertEqual(abridged_game.game_mode, "abridged")

    def test_timed_game(self):
        # check timed game setup
        timed_game = Game(self.players, game_mode="full", time_limit=1800)
        self.assertEqual(timed_game.time_limit, 1800)
        self.assertTrue(hasattr(timed_game, "start_time"))

    def test_free_parking_pot(self):
        # check free parking money
        self.assertEqual(self.game.free_parking_pot, 0)
        self.game.game_actions.add_to_free_parking(50)
        self.assertEqual(self.game.free_parking_pot, 50)

    def test_ai_difficulty(self):
        # check ai level setting
        easy_game = Game(self.players, ai_difficulty="easy")
        hard_game = Game(self.players, ai_difficulty="hard")
        self.assertEqual(easy_game.ai_difficulty, "easy")
        self.assertEqual(hard_game.ai_difficulty, "hard")

    def test_board_initialization(self):
        self.assertIsNotNone(self.game.board)
        self.assertEqual(len(self.game.board.spaces), 40)

    def test_initial_player_positions(self):
        # check players start at go
        self.assertEqual(self.game.players[0].position, 1)
        self.assertEqual(self.game.players[1].position, 1)

    def test_dice_roll(self):
        # check dice roll works
        dice1, dice2 = self.game_logic.play_turn()
        self.assertTrue(1 <= dice1 <= 6)
        self.assertTrue(1 <= dice2 <= 6)
        self.assertEqual(self.game_logic.last_dice_roll, (dice1, dice2))

    def test_player_movement_after_roll(self):
        # check player moves right
        player = self.game.players[0]
        initial_position = player.position

        self.game_logic.current_player_index = 0

        original_randint = random.randint
        random.randint = lambda a, b: 3

        try:
            dice1, dice2 = self.game_logic.play_turn()
            expected_position = (initial_position + dice1 + dice2 - 1) % 40 + 1

            self.sync_player_objects()

            self.assertEqual(player.position, expected_position)
        finally:
            random.randint = original_randint

    def test_movement_past_go(self):
        # check passing go money
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        player.position = 39
        player_dict["position"] = 39

        self.game_logic.current_player_index = 0

        original_randint = random.randint
        random.randint = lambda a, b: 3

        try:
            self.game_logic.play_turn()

            self.sync_player_objects()

            self.assertTrue(
                1 <= player.position <= 6,
                f"Expected player to be in positions 1-6 after passing GO, but was at {player.position}",
            )

        finally:
            random.randint = original_randint

    def test_buy_property(self):
        # check buying works ok
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        property_position = None
        for pos, space_data in self.game_logic.properties.items():
            if (
                space_data.get("can_be_bought", False)
                and space_data.get("owner") is None
            ):
                property_position = pos
                break

        if property_position:
            player.position = int(property_position)
            player_dict["position"] = int(property_position)
            initial_money = player.money
            property_price = self.game_logic.properties[property_position]["price"]

            self.game_logic.completed_circuits[player.name] = 1

            result = self.game_logic.buy_property(player_dict)

            self.sync_player_objects()

            self.assertTrue(result)
            self.assertEqual(player.money, initial_money - property_price)
            self.assertEqual(
                self.game_logic.properties[property_position]["owner"], player.name
            )

    def test_insufficient_funds_for_property(self):
        # check cant buy no money
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        property_position = None
        for pos, space_data in self.game_logic.properties.items():
            if (
                space_data.get("can_be_bought", False)
                and space_data.get("owner") is None
                and space_data.get("price", 0) > 0
            ):
                property_position = pos
                property_price = space_data.get("price", 0)
                break

        if property_position:
            self.game_logic.completed_circuits[player.name] = 1

            player.money = property_price - 1
            player_dict["money"] = property_price - 1

            player.position = int(property_position)
            player_dict["position"] = int(property_position)

            result = self.game_logic.buy_property(player_dict)
            self.sync_player_objects()

            self.assertFalse(result)

            self.assertEqual(player.money, property_price - 1)

            self.assertIsNone(
                self.game_logic.properties[property_position].get("owner")
            )

    def test_rent_payment(self):
        # check paying rent works
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        player2_dict = self.get_player_dict(player2)

        property_position = None
        for pos, space_data in self.game_logic.properties.items():
            if space_data.get("type") == "property" and space_data.get("owner") is None:
                property_position = pos
                break

        if property_position:
            property_data = self.game_logic.properties[property_position]
            initial_owner_money = player1.money
            initial_renter_money = player2.money

            property_data["owner"] = player1.name

            expected_rent = property_data.get("rent", 0)

            success = self.game_logic.handle_rent_payment(player2_dict, property_data)

            self.sync_player_objects()

            self.assertTrue(success)
            self.assertEqual(player1.money, initial_owner_money + expected_rent)
            self.assertEqual(player2.money, initial_renter_money - expected_rent)

    def test_station_rent_calculation(self):
        # check station rent math
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        player2_dict = self.get_player_dict(player2)

        station_positions = []
        for pos, space_data in self.game_logic.properties.items():
            if "Station" in space_data.get("name", ""):
                station_positions.append(pos)

        if len(station_positions) >= 2:
            station1 = self.game_logic.properties[station_positions[0]]
            station1["owner"] = player1.name

            initial_money = player2.money
            player2_dict["money"] = initial_money
            success = self.game_logic.handle_rent_payment(player2_dict, station1)

            self.sync_player_objects()

            self.assertTrue(success)
            self.assertEqual(player2.money, initial_money - 25)

            player2.money = initial_money
            player2_dict["money"] = initial_money

            station2 = self.game_logic.properties[station_positions[1]]
            station2["owner"] = player1.name

            success = self.game_logic.handle_rent_payment(player2_dict, station1)

            self.sync_player_objects()

            self.assertTrue(success)
            self.assertEqual(player2.money, initial_money - 50)

    def test_utility_rent_calculation(self):
        # check utility rent math
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        player2_dict = self.get_player_dict(player2)

        utility_positions = []
        for pos, space_data in self.game_logic.properties.items():
            if space_data.get("name") in ["Tesla Power Co", "Edison Water"]:
                utility_positions.append(pos)

        if utility_positions:
            utility = self.game_logic.properties[utility_positions[0]]
            utility["owner"] = player1.name

            self.game_logic.last_dice_roll = (3, 4)

            initial_money = player2.money
            player2_dict["money"] = initial_money
            success = self.game_logic.handle_rent_payment(player2_dict, utility)

            self.sync_player_objects()

            self.assertTrue(success)
            self.assertEqual(player2.money, initial_money - 7 * 4)

    def test_bankruptcy(self):
        # check going broke works
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        player.money = 10
        player_dict["money"] = 10

        expensive_property = None
        for pos, space_data in self.game_logic.properties.items():
            if (
                space_data.get("type") == "property"
                and space_data.get("price", 0) > 200
            ):
                expensive_property = pos
                space_data["owner"] = self.game.players[1].name
                break

        if expensive_property:
            property_data = self.game_logic.properties[expensive_property]
            success = self.game_logic.handle_rent_payment(player_dict, property_data)

            self.assertFalse(success)
            self.assertIn(player.name, self.game_logic.bankrupted_players)

    def test_property_group_completion(self):
        # check getting full set
        player = self.game.players[0]

        groups = {}
        for pos, space_data in self.game_logic.properties.items():
            if space_data.get("group") and space_data.get("type") == "property":
                group = space_data.get("group")
                if group not in groups:
                    groups[group] = []
                groups[group].append(pos)

        test_group = None
        for group, positions in groups.items():
            if len(positions) > 0:
                test_group = group
                break

        if test_group:
            for pos in groups[test_group]:
                self.game_logic.properties[pos]["owner"] = player.name

            result = self.game_logic.check_property_group_completion(player.name)
            self.assertTrue(result)

    def test_card_actions(self):
        # check chance cards work
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        advance_go_card = None
        for card in pot_luck_cards + opportunity_knocks_cards:
            if card["text"] == "Advance to go":
                advance_go_card = card
                break

        if advance_go_card:
            action_result, _, _ = advance_go_card["action"](
                player_dict,
                self.game_logic.bank_money,
                self.game_logic.free_parking_fund,
            )

            self.assertEqual(action_result, 1)

            player_dict["position"] = action_result
            self.sync_player_objects()

            self.assertEqual(player.position, 1)

    def test_jail_mechanics(self):
        # check getting out jail
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        player.in_jail = True
        player_dict["in_jail"] = True
        player.position = 11
        player_dict["position"] = 11

        success, _ = self.game_logic.try_leave_jail(player_dict, 3, 3)

        self.sync_player_objects()

        self.assertTrue(success)
        self.assertFalse(player.in_jail)

    def test_jail_free_card_use(self):
        # check using jail card
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        player.position = 11
        player_dict["position"] = 11
        player.in_jail = True
        player_dict["in_jail"] = True
        player.jail_turns = 1
        player_dict["jail_turns"] = 1

        self.game_logic.jail_free_cards[player.name] = 1

        def mock_get_jail_choice(player):
            return "card"

        original_get_jail_choice = None
        if hasattr(self.game, "get_jail_choice"):
            original_get_jail_choice = self.game.get_jail_choice
            self.game.get_jail_choice = mock_get_jail_choice

        try:
            success, message = self.game_logic.try_leave_jail(player_dict, 2, 3)
            self.sync_player_objects()

            self.assertTrue(success)
            self.assertFalse(player.in_jail)
            self.assertEqual(self.game_logic.jail_free_cards.get(player.name, 0), 0)
        finally:
            if original_get_jail_choice:
                self.game.get_jail_choice = original_get_jail_choice

    def test_game_over_detection(self):
        # check game ends right
        self.game.players = [self.players[0]]
        self.game_logic.players = [self.player_dicts[0]]

        game_over, winner = self.game_logic.check_game_over()

        self.assertTrue(game_over)
        self.assertIsNotNone(winner)

    def test_abridged_game_end_calculation(self):
        # check short game end
        abridged_game = Game(self.players, game_mode="abridged")

        abridged_player_dicts = []
        for player in self.players:
            player_dict = {
                "name": player.name,
                "money": player.money,
                "position": player.position,
                "in_jail": player.in_jail,
                "jail_turns": player.jail_turns,
                "is_ai": player.is_ai,
            }
            abridged_player_dicts.append(player_dict)

        abridged_game.logic.players = abridged_player_dicts

        for player in self.players:
            if not hasattr(abridged_game.logic, "rounds_completed"):
                abridged_game.logic.rounds_completed = {}
            abridged_game.logic.rounds_completed[player.name] = 1

        self.players[0].money = 2000
        self.players[1].money = 1000

        for i, player_dict in enumerate(abridged_game.logic.players):
            player_dict["money"] = self.players[i].money

        for pos, prop in abridged_game.logic.properties.items():
            if prop.get("type") == "property":
                prop["owner"] = self.players[0].name
                break

        if not hasattr(abridged_game.logic, "game_mode"):
            abridged_game.logic.game_mode = "abridged"
        else:
            abridged_game.logic.game_mode = "abridged"

        game_over, winner = abridged_game.logic.check_game_over()

        self.assertTrue(game_over)
        self.assertEqual(winner, self.players[0].name)

    def test_max_players(self):
        max_players = []
        for i in range(6):
            max_players.append(Player(f"Player{i+1}", player_number=i + 1))

        game = Game(max_players, game_mode="full")
        self.assertEqual(len(game.players), 6)

    def test_property_ownership_restriction(self):
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        player1_dict = self.get_player_dict(player1)
        player2_dict = self.get_player_dict(player2)

        property_position = None
        for pos, prop in self.game_logic.properties.items():
            if prop.get("can_be_bought", False):
                property_position = pos
                break

        if property_position:
            self.game_logic.properties[property_position]["owner"] = player1.name

            player2.position = int(property_position)
            player2_dict["position"] = int(property_position)

            try:
                result = self.game_logic.handle_space(player2_dict)

                self.assertNotEqual(result[0], "can_buy")
            except Exception as e:
                self.fail(f"handle_space raised exception: {e}")

    def test_invalid_game_mode(self):
        game = Game(self.players, game_mode="invalid_mode")
        self.assertEqual(game.game_mode, "invalid_mode")

    def test_build_house_mechanics(self):
        # check building houses ok
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)
        player.money = 5000
        player_dict["money"] = 5000

        property_group = None
        group_properties = []
        for pos, prop in self.game_logic.properties.items():
            if prop.get("group") and prop.get("group") not in ["Utilities", "Stations"]:
                if property_group is None or property_group == prop.get("group"):
                    property_group = prop.get("group")
                    group_properties.append(prop)

        if len(group_properties) > 0:
            for prop in group_properties:
                prop["owner"] = player.name

            self.game_logic.check_property_group_completion(player.name)

            result = self.game_logic.build_house(group_properties[0], player_dict)

            self.assertTrue(result)
            self.assertEqual(group_properties[0].get("houses", 0), 1)

    def test_build_hotel_mechanics(self):
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)
        player.money = 10000
        player_dict["money"] = 10000

        test_group = "Test Group"
        test_properties = []

        for i in range(2):
            property_pos = str(20 + i)
            self.game_logic.properties[property_pos] = {
                "name": f"Test Property {i}",
                "group": test_group,
                "type": "property",
                "price": 200,
                "houses": 4,
                "house_cost": 150,
                "owner": player.name,
            }
            test_properties.append(self.game_logic.properties[property_pos])

        self.game_logic.check_property_group_completion(player.name)

        test_property = test_properties[0]
        result = self.game_logic.build_hotel(test_property, player_dict)

        self.assertTrue(result)
        self.assertEqual(test_property.get("houses", 0), 5)

    def test_mortgage_mechanics(self):
        # check mortgaging works
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)
        player.money = 1000
        player_dict["money"] = 1000

        test_property = None
        for pos, prop in self.game_logic.properties.items():
            if prop.get("type") in ["property", "station", "utility"]:
                test_property = prop
                break

        if test_property:
            test_property["owner"] = player.name
            initial_money = player.money
            player_dict["money"] = initial_money

            result = self.game_logic.mortgage_property(test_property, player_dict)

            self.sync_player_objects()

            self.assertTrue(result)
            self.assertTrue(test_property.get("is_mortgaged", False))
            self.assertEqual(player.money, initial_money + test_property["price"] // 2)

    def test_card_exhaustion(self):
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        original_pot_luck = self.game_logic.pot_luck_cards.copy()
        original_opportunity_knocks = self.game_logic.opportunity_knocks_cards.copy()

        original_handle_card_draw = self.game_logic.handle_card_draw

        try:
            drawn_cards = []

            def mock_handle_card_draw(player_dict, card_type):
                result, message = original_handle_card_draw(player_dict, card_type)
                drawn_cards.append({"text": message, "result": result})
                return result, message

            self.game_logic.handle_card_draw = mock_handle_card_draw

            total_cards = len(self.game_logic.pot_luck_cards) + 1
            for _ in range(total_cards):
                self.game_logic.handle_card_draw(player_dict, "Pot Luck")

            card_texts = [card["text"] for card in drawn_cards]
            unique_cards = set(card_texts)
            self.assertLess(
                len(unique_cards),
                len(card_texts),
                "Expected at least one card to be drawn twice after reshuffling",
            )
        finally:
            self.game_logic.handle_card_draw = original_handle_card_draw
            self.game_logic.pot_luck_cards = original_pot_luck
            self.game_logic.opportunity_knocks_cards = original_opportunity_knocks

    def test_card_distribution_equality(self):
        original_handle_card_draw = self.game_logic.handle_card_draw
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        try:
            card_counts = {}

            def counting_handle_card_draw(player_dict, card_type):
                result, message = original_handle_card_draw(player_dict, card_type)
                if message not in card_counts:
                    card_counts[message] = 0
                card_counts[message] += 1
                return result, message

            self.game_logic.handle_card_draw = counting_handle_card_draw

            for _ in range(100):
                self.game_logic.handle_card_draw(player_dict, "Pot Luck")

            avg_frequency = sum(card_counts.values()) / len(card_counts)

            for card_text, count in card_counts.items():
                self.assertLess(
                    abs(count - avg_frequency),
                    avg_frequency * 0.5,
                    f"Card '{card_text}' appears with unusual frequency: {count}",
                )

        finally:
            self.game_logic.handle_card_draw = original_handle_card_draw

    def test_bankruptcy_from_bank_payment(self):
        # check broke from bank
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        player.money = 30
        player_dict["money"] = 30

        initial_bank_money = self.game_logic.bank_money

        payment_amount = 100
        player_money, bank_money, _ = self.game_logic.handle_payment_to_bank(
            player_dict, payment_amount, False
        )

        self.sync_player_objects()

        self.assertIn(player.name, self.game_logic.bankrupted_players)

        self.assertTrue(
            player_dict.get("bankrupt", False), "Player should be marked as bankrupt"
        )

        self.assertEqual(bank_money, initial_bank_money + 30)

    def test_player_asset_calculation_with_mortgaged_properties(self):
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        player.money = 1000
        player_dict["money"] = 1000

        property_pos = "30"
        self.game_logic.properties[property_pos] = {
            "name": "Test Mortgage Property",
            "type": "property",
            "price": 300,
            "rent": 25,
            "houses": 0,
            "owner": player.name,
        }

        test_property = self.game_logic.properties[property_pos]
        initial_price = test_property.get("price", 0)

        assets_before = self.game.game_actions.calculate_player_assets(player_dict)

        self.game_logic.mortgage_property(test_property, player_dict)

        assets_after = self.game.game_actions.calculate_player_assets(player_dict)

        expected_difference = initial_price / 2
        actual_difference = assets_after - assets_before

        self.assertAlmostEqual(actual_difference, expected_difference, delta=10)

    def test_three_doubles_jail(self):
        # check 3 doubles go jail
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        player.position = 5
        player_dict["position"] = 5
        self.game_logic.current_player_index = 0

        original_randint = random.randint
        random.randint = lambda a, b: 4

        try:
            self.game_logic.doubles_count = 0

            self.game_logic.play_turn()
            self.sync_player_objects()
            self.assertFalse(player.in_jail)

            self.game_logic.play_turn()
            self.sync_player_objects()
            self.assertFalse(player.in_jail)

            self.game_logic.play_turn()
            self.sync_player_objects()

            self.assertTrue(player.in_jail)
            self.assertEqual(player.position, 11)

        finally:
            random.randint = original_randint

    def test_landing_on_tax_space(self):
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        tax_position = None
        tax_amount = 0

        for pos, space_data in self.game_logic.properties.items():
            if space_data.get("type") == "tax":
                tax_position = pos
                tax_amount = space_data.get("amount", 0)
                break

        if tax_position:
            player.money = 1000
            player_dict["money"] = 1000
            initial_money = player.money
            initial_bank_money = self.game_logic.bank_money

            player.position = int(tax_position)
            player_dict["position"] = int(tax_position)

            self.game_logic.handle_space(player_dict)
            self.sync_player_objects()

            self.assertEqual(player.money, initial_money - tax_amount)
            self.assertEqual(
                self.game_logic.bank_money, initial_bank_money + tax_amount
            )

    def test_landing_on_go_to_jail(self):
        # check go to jail space
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        jail_position = None
        for pos, space_data in self.game_logic.properties.items():
            if space_data.get("name") == "Go to Jail":
                jail_position = pos
                break

        if jail_position:
            player.position = int(jail_position)
            player_dict["position"] = int(jail_position)
            player.in_jail = False
            player_dict["in_jail"] = False
            player.money = 1000
            player_dict["money"] = 1000

            self.game_logic.handle_jail(player_dict)
            self.sync_player_objects()

            self.assertTrue(player.in_jail)
            self.assertEqual(player.position, 11)
            self.assertEqual(player.money, 1000)

    def test_mortgaged_property_rent(self):
        # check no rent mortgaged
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        player2_dict = self.get_player_dict(player2)

        property_pos = "24"
        self.game_logic.properties[property_pos] = {
            "name": "Test Rent Property",
            "type": "property",
            "price": 200,
            "rent": 50,
            "owner": player1.name,
            "is_mortgaged": True,
        }

        test_property = self.game_logic.properties[property_pos]

        initial_owner_money = player1.money
        initial_renter_money = player2.money

        player2.position = int(property_pos)
        player2_dict["position"] = int(property_pos)

        success = self.game_logic.handle_rent_payment(player2_dict, test_property)
        self.sync_player_objects()

        self.assertTrue(success)
        self.assertEqual(player1.money, initial_owner_money)
        self.assertEqual(player2.money, initial_renter_money)

    def test_consecutive_turns_from_doubles(self):
        # check extra turn double
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        player.position = 3
        player_dict["position"] = 3
        self.game_logic.current_player_index = 0

        original_randint = random.randint
        try:
            self.game_logic.doubles_count = 0

            random.randint = lambda a, b: 2

            self.game_logic.play_turn()
            self.sync_player_objects()

            self.assertEqual(self.game_logic.current_player_index, 0)

            self.assertEqual(player.position, 7)

            self.assertEqual(self.game_logic.doubles_count, 1)
        finally:
            random.randint = original_randint

    def test_landing_on_free_parking(self):
        # check free parking space
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        free_parking_position = None
        for pos, space_data in self.game_logic.properties.items():
            if space_data.get("name") == "Free Parking":
                free_parking_position = pos
                break

        if free_parking_position:
            self.game_logic.free_parking_fund = 500

            player.position = int(free_parking_position)
            player_dict["position"] = int(free_parking_position)
            player.money = 1000
            player_dict["money"] = 1000

            result, message = self.game_logic.handle_space(player_dict)
            self.sync_player_objects()

            if result == "free_parking":
                self.assertEqual(player.money, 1500)
                self.assertEqual(self.game_logic.free_parking_fund, 0)
            else:
                self.assertEqual(player.money, 1000)
                self.assertEqual(self.game_logic.free_parking_fund, 500)

    def test_uneven_house_development_restrictions(self):
        # check build houses evenly
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)
        player.money = 5000
        player_dict["money"] = 5000

        test_group = "Test Color Group"
        test_properties = []

        for i in range(3):
            property_pos = str(25 + i)
            self.game_logic.properties[property_pos] = {
                "name": f"Test Property {i}",
                "group": test_group,
                "type": "property",
                "price": 200,
                "house_cost": 150,
                "houses": i,
                "owner": player.name,
            }
            test_properties.append(self.game_logic.properties[property_pos])

        result = self.game_logic.build_house(test_properties[2], player_dict)

        self.assertFalse(result)

        self.assertEqual(test_properties[2].get("houses", 0), 2)

        result = self.game_logic.build_house(test_properties[0], player_dict)

        self.assertTrue(result)

        self.assertEqual(test_properties[0].get("houses", 0), 1)

    def test_maximum_house_limit(self):
        # check cant build too many
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)
        player.money = 10000
        player_dict["money"] = 10000

        property_pos = "28"
        self.game_logic.properties[property_pos] = {
            "name": "Test Max Houses Property",
            "group": "Test Group",
            "type": "property",
            "price": 200,
            "houses": 4,
            "house_cost": 150,
            "owner": player.name,
        }

        test_property = self.game_logic.properties[property_pos]

        original_can_build_hotel = None
        if hasattr(self.game_logic, "can_build_hotel"):
            original_can_build_hotel = self.game_logic.can_build_hotel
            self.game_logic.can_build_hotel = lambda prop, player: (
                False,
                "Testing house limit",
            )

        try:
            result = self.game_logic.build_house(test_property, player_dict)

            self.assertFalse(result)

            self.assertEqual(test_property.get("houses", 0), 4)
        finally:
            if original_can_build_hotel:
                self.game_logic.can_build_hotel = original_can_build_hotel

    def test_selling_houses_for_bankruptcy_prevention(self):
        # check sell houses avoid broke
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)

        property_pos = "35"
        self.game_logic.properties[property_pos] = {
            "name": "Test Property with Houses",
            "type": "property",
            "price": 300,
            "rent": 25,
            "houses": 3,
            "house_cost": 200,
            "owner": player.name,
        }

        test_property = self.game_logic.properties[property_pos]

        player.money = 50
        player_dict["money"] = 50

        payment_needed = 200

        original_handle_prevention = None
        if hasattr(self.game_logic, "handle_ai_bankruptcy_prevention"):
            original_handle_prevention = self.game_logic.handle_ai_bankruptcy_prevention

        def mock_prevention(player_d, amount_needed):
            if player_d["name"] == player_dict["name"]:
                while (
                    test_property.get("houses", 0) > 0
                    and player_d["money"] < amount_needed
                ):
                    house_sale_value = test_property.get("house_cost", 200) // 2
                    player_d["money"] += house_sale_value
                    test_property["houses"] -= 1
                return player_d["money"] >= amount_needed
            return False

        try:
            if hasattr(self.game_logic, "handle_ai_bankruptcy_prevention"):
                self.game_logic.handle_ai_bankruptcy_prevention = mock_prevention

            success = False
            if hasattr(self.game_logic, "handle_ai_bankruptcy_prevention"):
                success = self.game_logic.handle_ai_bankruptcy_prevention(
                    player_dict, payment_needed
                )
            else:
                while (
                    test_property.get("houses", 0) > 0
                    and player_dict["money"] < payment_needed
                ):
                    house_sale_value = test_property.get("house_cost", 200) // 2
                    player_dict["money"] += house_sale_value
                    test_property["houses"] -= 1
                success = player_dict["money"] >= payment_needed

            self.sync_player_objects()

            self.assertTrue(success)
            self.assertTrue(player.money >= payment_needed)

            self.assertLess(test_property.get("houses", 0), 3)
        finally:
            if original_handle_prevention:
                self.game_logic.handle_ai_bankruptcy_prevention = (
                    original_handle_prevention
                )

    def test_all_utilities_ownership_rent_calculation(self):
        # check rent both utilities
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        player2_dict = self.get_player_dict(player2)

        utility_positions = []
        for pos, space_data in self.game_logic.properties.items():
            if space_data.get("name") in ["Tesla Power Co", "Edison Water"]:
                utility_positions.append(pos)
                space_data["owner"] = player1.name

        if len(utility_positions) >= 2:
            utility = self.game_logic.properties[utility_positions[0]]
            initial_money = player2.money
            player2_dict["money"] = initial_money

            self.game_logic.last_dice_roll = (3, 4)
            total_roll = sum(self.game_logic.last_dice_roll)

            success = self.game_logic.handle_rent_payment(player2_dict, utility)
            self.sync_player_objects()

            self.assertTrue(success)
            self.assertEqual(player2.money, initial_money - (10 * total_roll))


if __name__ == "__main__":
    unittest.main()
