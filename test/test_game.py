import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.Board import Board
from src.Game import Game
from src.Player import Player

class TestGame(unittest.TestCase):
    def setUp(self):
        self.players = [
            Player("Alice", player_number=1),
            Player("Bob", player_number=2, is_ai=True)
        ]
        self.game = Game(self.players, game_mode="full")

    def test_game_initialization(self):
        """测试游戏初始化"""
        self.assertEqual(len(self.game.players), 2)
        self.assertEqual(self.game.game_mode, "full")

if __name__ == "__main__":
    unittest.main()
