import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import unittest
from src.Game import Game
from src.Player import Player
from src.Board import Board
import random

class TestPlayer(unittest.TestCase):
    def setUp(self):
        self.player = Player("TestPlayer", player_number=1)
        self.player.money = 1500  # Initial money
    
    def test_initial_money(self):
        """Test player's initial money"""
        self.assertEqual(self.player.money, 1500)
    
    def test_move_player(self):
        """Test player movement"""
        self.player.position = 0
        self.player.move(5)
        self.assertEqual(self.player.position, 5)
    
    def test_pass_go(self):
        """Test player passing GO and receiving money"""
        self.player.position = 38
        self.player.move(5)  # 38 + 5 = 43 (exceeds 40, passes GO)
        self.assertTrue(self.player.position < 40)
        self.assertEqual(self.player.money, 1700)  # Passing GO +200
    
    def test_pay_rent(self):
        """Test player paying rent"""
        initial_money = self.player.money
        rent = 200
        self.player.pay_money(rent)
        self.assertEqual(self.player.money, initial_money - rent)
    
    def test_bankrupt(self):
        """Test player bankruptcy"""
        self.player.money = 50
        self.player.pay_money(100)
        self.assertTrue(self.player.is_bankrupt)
    
class TestGame(unittest.TestCase):
    def setUp(self):
        self.players = [
            Player("Alice", player_number=1),
            Player("Bob", player_number=2, is_ai=True)
        ]
        self.game = Game(self.players, game_mode="full")
    
    def test_game_initialization(self):
        """Test game initialization"""
        self.assertEqual(len(self.game.players), 2)
        self.assertEqual(self.game.game_mode, "full")
    
    def test_turn_order(self):
        """Test turn order switching"""
        initial_player = self.game.logic.current_player_index
        self.game.next_turn()
        new_player = self.game.logic.current_player_index
        self.assertNotEqual(initial_player, new_player)
    
    def test_property_purchase(self):
        """Test property purchase"""
        property_price = 200
        self.players[0].money = 500
        result = self.game.logic.purchase_property(self.players[0], property_price)
        self.assertTrue(result)
        self.assertEqual(self.players[0].money, 300)  # 500 - 200
    
    def test_insufficient_funds_purchase(self):
        """Test property purchase with insufficient funds"""
        self.players[0].money = 100
        result = self.game.logic.purchase_property(self.players[0], 200)
        self.assertFalse(result)
    
    def test_ai_decision(self):
        """Test AI purchase decision"""
        self.players[1].money = 500
        ai_should_buy = random.choice([True, False])
        if ai_should_buy:
            result = self.game.logic.purchase_property(self.players[1], 200)
            self.assertTrue(result)
            self.assertEqual(self.players[1].money, 300)
        else:
            result = self.game.logic.purchase_property(self.players[1], 600)
            self.assertFalse(result)
    
    def test_check_win_condition(self):
        """Test game win condition"""
        self.players[0].money = 10000  # Simulate winning large funds
        self.players[1].money = 0
        self.players[1].is_bankrupt = True
        result = self.game.check_one_player_remains()
        self.assertTrue(result)
    
class TestBoard(unittest.TestCase):
    def setUp(self):
        self.board = Board()
    
    def test_board_initialization(self):
        """Test board initialization"""
        self.assertIsNotNone(self.board.properties)
        self.assertGreater(len(self.board.properties), 0)
    
    def test_get_property_by_position(self):
        """Test retrieving property by position"""
        property_at_1 = self.board.get_property_by_position(1)
        self.assertIsNotNone(property_at_1)
        self.assertEqual(property_at_1.position, 1)
    
if __name__ == '__main__':
    unittest.main()
