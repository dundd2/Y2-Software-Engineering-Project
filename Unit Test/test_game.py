# Property Tycoon test_game.py
# Created for Year 2 G6046: Software Engineering Project-Group 5
# -*- coding: utf-8 -*-
# Thanks to owen for creating the base of the test code
# start on 17/03/2025 for build 16.03.2025

import unittest
import sys
import os
import time
import pygame
import random

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.Board import Board
from src.Game import Game
from src.Player import Player
from src.Property import Property
from src.game_logic import GameLogic, pot_luck_cards, opportunity_knocks_cards

class TestGame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        
    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self._original_flip = pygame.display.flip
        self._original_wait = pygame.time.wait
        pygame.display.flip = lambda: None
        pygame.time.wait = lambda x: None
        
        self.players = [
            Player("Alice", player_number=1),
            Player("Bob", player_number=2, is_ai=True)
        ]
        for player in self.players:
            player.money = 1500
            
        self.game = Game(self.players, game_mode="full")
        self.game_logic = self.game.logic

        if not hasattr(self.game_logic, 'completed_circuits'):
            self.game_logic.completed_circuits = {}
        
        if not hasattr(self.game_logic, 'rounds_completed'):
            self.game_logic.rounds_completed = {}
        
        if not hasattr(self.game_logic, 'game_mode'):
            self.game_logic.game_mode = 'full'
            
        self.player_dicts = []
        for player in self.players:
            player_dict = {
                'name': player.name,
                'money': player.money,
                'position': player.position,
                'in_jail': player.in_jail,
                'jail_turns': player.jail_turns,
                'is_ai': player.is_ai
            }
            self.player_dicts.append(player_dict)
        
        self.game_logic.players = self.player_dicts

    def tearDown(self):
        pygame.display.flip = self._original_flip
        pygame.time.wait = self._original_wait

    def get_player_dict(self, player):
        """Get the dictionary representation of a player for game logic"""
        for player_dict in self.player_dicts:
            if player_dict['name'] == player.name:
                return player_dict
        return None
        
    def sync_player_objects(self):
        """Sync player objects with their dictionary representations"""
        for player in self.players:
            player_dict = self.get_player_dict(player)
            if player_dict:
                player.money = player_dict['money']
                player.position = player_dict['position']
                player.in_jail = player_dict['in_jail']
                player.jail_turns = player_dict['jail_turns']
                
    def sync_player_dicts(self):
        """Sync player dictionaries with their object representations"""
        for player in self.players:
            player_dict = self.get_player_dict(player)
            if player_dict:
                player_dict['money'] = player.money
                player_dict['position'] = player.position
                player_dict['in_jail'] = player.in_jail
                player_dict['jail_turns'] = player.jail_turns

    def test_game_initialization(self):
        self.assertEqual(len(self.game.players), 2)
        self.assertEqual(self.game.game_mode, "full")
        
    def test_player_attributes(self):
        """Test if players have correct attributes after game initialization"""
        self.assertEqual(self.game.players[0].name, "Alice")
        self.assertEqual(self.game.players[1].name, "Bob")
        self.assertFalse(self.game.players[0].is_ai)
        self.assertTrue(self.game.players[1].is_ai)
        self.assertEqual(self.game.players[0].money, 1500)
        self.assertEqual(self.game.players[1].money, 1500)
        
    def test_abridged_game_mode(self):
        """Test if abridged game mode is properly initialized"""
        abridged_game = Game(self.players, game_mode="abridged")
        self.assertEqual(abridged_game.game_mode, "abridged")
        
    def test_timed_game(self):
        """Test if game with time limit is properly initialized"""
        timed_game = Game(self.players, game_mode="full", time_limit=1800)  
        self.assertEqual(timed_game.time_limit, 1800)
        self.assertTrue(hasattr(timed_game, 'start_time'))
        
    def test_free_parking_pot(self):
        """Test free parking pot functionality"""
        self.assertEqual(self.game.free_parking_pot, 0) 
        self.game.add_to_free_parking(50)
        self.assertEqual(self.game.free_parking_pot, 50)
        
    def test_ai_difficulty(self):
        """Test if AI difficulty is correctly set"""
        easy_game = Game(self.players, ai_difficulty="easy")
        hard_game = Game(self.players, ai_difficulty="hard")
        self.assertEqual(easy_game.ai_difficulty, "easy")
        self.assertEqual(hard_game.ai_difficulty, "hard")
        
    def test_board_initialization(self):
        """Test if the board is properly initialized"""
        self.assertIsNotNone(self.game.board)
        self.assertEqual(len(self.game.board.spaces), 40)  
        
    def test_initial_player_positions(self):
        """Test that players start at position 1 (GO)"""
        self.assertEqual(self.game.players[0].position, 1)
        self.assertEqual(self.game.players[1].position, 1)
    
    def test_dice_roll(self):
        """Test the game's dice rolling mechanism"""
        dice1, dice2 = self.game_logic.play_turn()
        self.assertTrue(1 <= dice1 <= 6)
        self.assertTrue(1 <= dice2 <= 6)
        self.assertEqual(self.game_logic.last_dice_roll, (dice1, dice2))

    def test_player_movement_after_roll(self):
        """Test player actually moves after rolling dice"""
        player = self.game.players[0]
        initial_position = player.position
        player_dict = self.get_player_dict(player)
        
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
        """Test player movement that passes GO and receives money"""
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)
        
        player.position = 39
        player_dict['position'] = 39
        initial_money = player.money
        
        self.game_logic.current_player_index = 0  
        
        original_randint = random.randint
        random.randint = lambda a, b: 3  
        
        try:
            self.game_logic.play_turn()
            
            self.sync_player_objects()
            
            self.assertTrue(1 <= player.position <= 6, 
                          f"Expected player to be in positions 1-6 after passing GO, but was at {player.position}")
            
        finally:
            random.randint = original_randint
    
    def test_buy_property(self):
        """Test buying an unowned property"""
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)
        
        property_position = None
        for pos, space_data in self.game_logic.properties.items():
            if space_data.get('can_be_bought', False) and space_data.get('owner') is None:
                property_position = pos
                break
                
        if property_position:
            player.position = int(property_position)
            player_dict['position'] = int(property_position)
            initial_money = player.money
            property_price = self.game_logic.properties[property_position]['price']
            
            self.game_logic.completed_circuits[player.name] = 1
            
            result = self.game_logic.buy_property(player_dict)
            
            self.sync_player_objects()
            
            self.assertTrue(result)
            self.assertEqual(player.money, initial_money - property_price)
            self.assertEqual(self.game_logic.properties[property_position]['owner'], player.name)
    
    def test_rent_payment(self):
        """Test rent payment mechanics"""
        player1 = self.game.players[0]  
        player2 = self.game.players[1]  
        player1_dict = self.get_player_dict(player1)
        player2_dict = self.get_player_dict(player2)
        
        property_position = None
        for pos, space_data in self.game_logic.properties.items():
            if space_data.get('type') == 'property' and space_data.get('owner') is None:
                property_position = pos
                break
                
        if property_position:
            property_data = self.game_logic.properties[property_position]
            initial_owner_money = player1.money
            initial_renter_money = player2.money
            
            property_data['owner'] = player1.name
            
            expected_rent = property_data.get('rent', 0)
            
            success = self.game_logic.handle_rent_payment(player2_dict, property_data)
            
            self.sync_player_objects()
            
            self.assertTrue(success)
            self.assertEqual(player1.money, initial_owner_money + expected_rent)
            self.assertEqual(player2.money, initial_renter_money - expected_rent)
    
    def test_station_rent_calculation(self):
        """Test station rent calculations based on ownership"""
        player1 = self.game.players[0]  
        player2 = self.game.players[1]  
        player1_dict = self.get_player_dict(player1)
        player2_dict = self.get_player_dict(player2)
        
        station_positions = []
        for pos, space_data in self.game_logic.properties.items():
            if "Station" in space_data.get('name', ''):
                station_positions.append(pos)
                
        if len(station_positions) >= 2:
            station1 = self.game_logic.properties[station_positions[0]]
            station1['owner'] = player1.name
            
            initial_money = player2.money
            player2_dict['money'] = initial_money
            success = self.game_logic.handle_rent_payment(player2_dict, station1)
            
            self.sync_player_objects()
            
            self.assertTrue(success)
            self.assertEqual(player2.money, initial_money - 25)  
            
            player2.money = initial_money
            player2_dict['money'] = initial_money
            
            station2 = self.game_logic.properties[station_positions[1]]
            station2['owner'] = player1.name
            
            success = self.game_logic.handle_rent_payment(player2_dict, station1)
            
            self.sync_player_objects()
            
            self.assertTrue(success)
            self.assertEqual(player2.money, initial_money - 50)  
    
    def test_utility_rent_calculation(self):
        """Test utility rent calculations"""
        player1 = self.game.players[0]  
        player2 = self.game.players[1]  
        player1_dict = self.get_player_dict(player1)
        player2_dict = self.get_player_dict(player2)
        
        utility_positions = []
        for pos, space_data in self.game_logic.properties.items():
            if space_data.get('name') in ["Tesla Power Co", "Edison Water"]:
                utility_positions.append(pos)
                
        if utility_positions:
            utility = self.game_logic.properties[utility_positions[0]]
            utility['owner'] = player1.name
            
            self.game_logic.last_dice_roll = (3, 4)  
            
            initial_money = player2.money
            player2_dict['money'] = initial_money
            success = self.game_logic.handle_rent_payment(player2_dict, utility)
            
            self.sync_player_objects()
            
            self.assertTrue(success)
            self.assertEqual(player2.money, initial_money - 7*4)  
    
    def test_bankruptcy(self):
        """Test bankruptcy mechanics"""
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)
        
        player.money = 10
        player_dict['money'] = 10
        
        expensive_property = None
        for pos, space_data in self.game_logic.properties.items():
            if space_data.get('type') == 'property' and space_data.get('price', 0) > 200:
                expensive_property = pos
                space_data['owner'] = self.game.players[1].name  
                break
                
        if expensive_property:
            property_data = self.game_logic.properties[expensive_property]
            
            original_player_count = len(self.game.players)
            
            success = self.game_logic.handle_rent_payment(player_dict, property_data)
            
            self.assertFalse(success)
            
            self.assertIn(player.name, self.game_logic.bankrupted_players)
    
    def test_property_group_completion(self):
        """Test the monopoly recognition when a player owns all properties in a group"""
        player = self.game.players[0]
        
        groups = {}
        for pos, space_data in self.game_logic.properties.items():
            if space_data.get('group') and space_data.get('type') == 'property':
                group = space_data.get('group')
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
                self.game_logic.properties[pos]['owner'] = player.name
            
            result = self.game_logic.check_property_group_completion(player.name)
            self.assertTrue(result)
    
    def test_card_actions(self):
        """Test card action execution"""
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)
        initial_position = player.position
        initial_money = player.money
        
        advance_go_card = None
        for card in pot_luck_cards + opportunity_knocks_cards:
            if card['text'] == "Advance to go":
                advance_go_card = card
                break
        
        if advance_go_card:
            action_result, _, _ = advance_go_card['action'](player_dict, self.game_logic.bank_money, self.game_logic.free_parking_fund)
            
            self.assertEqual(action_result, 1)
            
            player_dict['position'] = action_result
            self.sync_player_objects()
            
            self.assertEqual(player.position, 1)
    
    def test_jail_mechanics(self):
        """Test jail mechanics - going to jail and leaving jail"""
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)
        
        player.in_jail = True
        player_dict['in_jail'] = True
        player.position = 11  
        player_dict['position'] = 11
        
        success, _ = self.game_logic.try_leave_jail(player_dict, 3, 3)  
        
        self.sync_player_objects()
        
        self.assertTrue(success)
        self.assertFalse(player.in_jail)
    
    def test_game_over_detection(self):
        """Test if the game correctly detects game over conditions"""
        self.game.players = [self.players[0]]  
        self.game_logic.players = [self.player_dicts[0]]  
        
        game_over, winner = self.game_logic.check_game_over()
        
        self.assertTrue(game_over)
        self.assertIsNotNone(winner)
    
    def test_abridged_game_end_calculation(self):
        """Test the end game calculation for abridged mode"""
        abridged_game = Game(self.players, game_mode="abridged")
        
        abridged_player_dicts = []
        for player in self.players:
            player_dict = {
                'name': player.name,
                'money': player.money,
                'position': player.position,
                'in_jail': player.in_jail,
                'jail_turns': player.jail_turns,
                'is_ai': player.is_ai
            }
            abridged_player_dicts.append(player_dict)
        
        abridged_game.logic.players = abridged_player_dicts
        
        for player in self.players:
            if not hasattr(abridged_game.logic, 'rounds_completed'):
                abridged_game.logic.rounds_completed = {}
            abridged_game.logic.rounds_completed[player.name] = 1
        
        self.players[0].money = 2000
        self.players[1].money = 1000
        
        for i, player_dict in enumerate(abridged_game.logic.players):
            player_dict['money'] = self.players[i].money
        
        for pos, prop in abridged_game.logic.properties.items():
            if prop.get('type') == 'property':
                prop['owner'] = self.players[0].name
                break
        
        if not hasattr(abridged_game.logic, 'game_mode'):
            abridged_game.logic.game_mode = "abridged"
        else:
            abridged_game.logic.game_mode = "abridged"
            
        game_over, winner = abridged_game.logic.check_game_over()
        
        self.assertTrue(game_over)
        self.assertEqual(winner, self.players[0].name)
    
    def test_max_players(self):
        """Test game with maximum number of players"""
        max_players = []
        for i in range(6):  
            max_players.append(Player(f"Player{i+1}", player_number=i+1))
            
        game = Game(max_players, game_mode="full")
        self.assertEqual(len(game.players), 6)
    
    def test_property_ownership_restriction(self):
        """Test buying a property that is already owned"""
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        player1_dict = self.get_player_dict(player1)
        player2_dict = self.get_player_dict(player2)
        
        property_position = None
        for pos, prop in self.game_logic.properties.items():
            if prop.get('can_be_bought', False):
                property_position = pos
                break
                
        if property_position:
            self.game_logic.properties[property_position]['owner'] = player1.name
            
            player2.position = int(property_position)
            player2_dict['position'] = int(property_position)
            
            try:
                result = self.game_logic.handle_space(player2_dict)
                
                self.assertNotEqual(result[0], "can_buy")
            except Exception as e:
                self.fail(f"handle_space raised exception: {e}")
    
    def test_invalid_game_mode(self):
        """Test handling of invalid game mode"""
        game = Game(self.players, game_mode="invalid_mode")
        self.assertEqual(game.game_mode, "invalid_mode")
    
    def test_build_house_mechanics(self):
        """Test house building mechanics"""
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)
        player.money = 5000  
        player_dict['money'] = 5000
        
        property_group = None
        group_properties = []
        for pos, prop in self.game_logic.properties.items():
            if prop.get('group') and prop.get('group') not in ["Utilities", "Stations"]:
                if property_group is None or property_group == prop.get('group'):
                    property_group = prop.get('group')
                    group_properties.append(prop)
        
        if len(group_properties) > 0:
            for prop in group_properties:
                prop['owner'] = player.name
            
            self.game_logic.check_property_group_completion(player.name)
            
            result = self.game_logic.build_house(group_properties[0], player_dict)
            
            self.assertTrue(result)
            self.assertEqual(group_properties[0].get('houses', 0), 1)
            
    def test_build_hotel_mechanics(self):
        """Test hotel building mechanics"""
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)
        player.money = 10000  
        player_dict['money'] = 10000
        
        property_group = None
        group_properties = []
        for pos, prop in self.game_logic.properties.items():
            if prop.get('group') and prop.get('group') not in ["Utilities", "Stations"]:
                if property_group is None or property_group == prop.get('group'):
                    property_group = prop.get('group')
                    group_properties.append(prop)
        
        if len(group_properties) >= 2:
            for prop in group_properties:
                prop['owner'] = player.name
            
            self.game_logic.check_property_group_completion(player.name)
            
            test_property = group_properties[0]
            for prop in group_properties:
                prop['houses'] = 4  
                
            result = self.game_logic.build_hotel(test_property, player_dict)
            
            self.assertTrue(result)
            self.assertEqual(test_property.get('houses', 0), 5)  
        else:
            self.skipTest("No suitable property group found for hotel building test")
    
    def test_mortgage_mechanics(self):
        """Test mortgage mechanics"""
        player = self.game.players[0]
        player_dict = self.get_player_dict(player)
        player.money = 1000
        player_dict['money'] = 1000
        
        test_property = None
        for pos, prop in self.game_logic.properties.items():
            if prop.get('type') in ['property', 'station', 'utility']:
                test_property = prop
                break
                
        if test_property:
            test_property['owner'] = player.name
            initial_money = player.money
            player_dict['money'] = initial_money
            
            result = self.game_logic.mortgage_property(test_property, player_dict)
            
            self.sync_player_objects()
            
            self.assertTrue(result)
            self.assertTrue(test_property.get('is_mortgaged', False))
            self.assertEqual(player.money, initial_money + test_property['price'] // 2)

if __name__ == "__main__":
    unittest.main()

def test_property_trading(self):
    """Test property trading between players"""
    player1 = self.game.players[0]
    player2 = self.game.players[1]
    player1_dict = self.get_player_dict(player1)
    player2_dict = self.get_player_dict(player2)
    
    property1 = None
    property2 = None
    for pos, prop in self.game_logic.properties.items():
        if prop.get('type') == 'property' and prop.get('can_be_bought', False):
            if property1 is None:
                property1 = prop
                property1['owner'] = player1.name
            elif property2 is None:
                property2 = prop
                property2['owner'] = player2.name
                break
    
    if property1 and property2:
        initial_property1_owner = property1['owner']
        initial_property2_owner = property2['owner']
        
        trade_offer = {
            'from_player': player1.name,
            'to_player': player2.name,
            'properties_offered': [property1],
            'properties_requested': [property2],
            'money_offered': 0,
            'money_requested': 0
        }
        
        result = self.game_logic.execute_trade(trade_offer)
        
        self.assertTrue(result)
        self.assertEqual(property1['owner'], player2.name)
        self.assertEqual(property2['owner'], player1.name)
        
        property1['owner'] = initial_property1_owner
        property2['owner'] = initial_property2_owner
        
        initial_player1_money = player1.money
        initial_player2_money = player2.money
        player1_dict['money'] = initial_player1_money
        player2_dict['money'] = initial_player2_money
        
        money_amount = 100
        trade_offer_with_money = {
            'from_player': player1.name,
            'to_player': player2.name,
            'properties_offered': [property1],
            'properties_requested': [],
            'money_offered': 0,
            'money_requested': money_amount
        }
        
        result = self.game_logic.execute_trade(trade_offer_with_money)
        
        self.sync_player_objects()
        
        self.assertTrue(result)
        self.assertEqual(property1['owner'], player2.name)
        self.assertEqual(player1.money, initial_player1_money - money_amount)
        self.assertEqual(player2.money, initial_player2_money + money_amount)

def test_property_auction(self):
    """Test property auction when no player buys a property"""
    player1 = self.game.players[0]
    player2 = self.game.players[1]
    player1_dict = self.get_player_dict(player1)
    player2_dict = self.get_player_dict(player2)
    
    auction_property = None
    for pos, prop in self.game_logic.properties.items():
        if prop.get('type') == 'property' and prop.get('can_be_bought', False) and prop.get('owner') is None:
            auction_property = prop
            auction_property_pos = pos
            break
    
    if auction_property:
        player1.position = int(auction_property_pos)
        player1_dict['position'] = int(auction_property_pos)
        
        initial_player1_money = player1.money
        initial_player2_money = player2.money
        player1_dict['money'] = initial_player1_money
        player2_dict['money'] = initial_player2_money
        
        auction_bids = {
            player1.name: 200,  
            player2.name: 250   
        }
        
        result = self.game_logic.conduct_auction(auction_property, auction_bids)
        
        self.sync_player_objects()
        
        self.assertEqual(result, player2.name)  
        self.assertEqual(auction_property['owner'], player2.name)
        self.assertEqual(player2.money, initial_player2_money - 250)  
        self.assertEqual(player1.money, initial_player1_money)  

def test_card_action_variety(self):
    """Test various card actions beyond just 'Advance to GO'"""
    player = self.game.players[0]
    player_dict = self.get_player_dict(player)
    
    payment_card = None
    for card in pot_luck_cards + opportunity_knocks_cards:
        if "pay" in card['text'].lower() or "fine" in card['text'].lower():
            payment_card = card
            break
    
    if payment_card:
        initial_money = player.money
        player_dict['money'] = initial_money
        initial_bank_money = self.game_logic.bank_money
        
        new_position, money_change, free_parking_change = payment_card['action'](
            player_dict, self.game_logic.bank_money, self.game_logic.free_parking_fund
        )
        
        self.sync_player_objects()
        
        self.assertLess(player.money, initial_money, "Card should have deducted money")
    
    movement_card = None
    for card in pot_luck_cards + opportunity_knocks_cards:
        if "go to" in card['text'].lower() and "go" not in card['text'].lower():
            movement_card = card
            break
    
    if movement_card:
        initial_position = player.position
        player_dict['position'] = initial_position
        
        new_position, _, _ = movement_card['action'](
            player_dict, self.game_logic.bank_money, self.game_logic.free_parking_fund
        )
        
        player_dict['position'] = new_position
        self.sync_player_objects()
        
        self.assertNotEqual(player.position, initial_position, 
                        f"Card should have moved player from position {initial_position}")
        
    jail_card = None
    for card in pot_luck_cards + opportunity_knocks_cards:
        if "jail" in card['text'].lower() and "free" in card['text'].lower():
            jail_card = card
            break
    
    if jail_card:
        initial_jail_cards = player.jail_cards
        player_dict['jail_cards'] = initial_jail_cards
        
        _, _, _ = jail_card['action'](
            player_dict, self.game_logic.bank_money, self.game_logic.free_parking_fund
        )
        
        self.sync_player_objects()
        
        self.assertGreater(player.jail_cards, initial_jail_cards, 
                        "Player should have received a Get Out of Jail Free card")