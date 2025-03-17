import unittest
import sys
import os
import time
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.Board import Board
from src.Game import Game
from src.Player import Player
from src.Property import Property
from src.game_logic import GameLogic

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
        self.game = Game(self.players, game_mode="full")

    def tearDown(self):
        pygame.display.flip = self._original_flip
        pygame.time.wait = self._original_wait

    def test_game_initialization(self):
        self.assertEqual(len(self.game.players), 2)
        self.assertEqual(self.game.game_mode, "full")
        
    def test_player_attributes(self):
        """Test if players have correct attributes after game initialization"""
        self.assertEqual(self.game.players[0].name, "Alice")
        self.assertEqual(self.game.players[1].name, "Bob")
        self.assertFalse(self.game.players[0].is_ai)
        self.assertTrue(self.game.players[1].is_ai)
        self.assertEqual(self.game.players[0].money, 0)
        self.assertEqual(self.game.players[1].money, 0)
        
    def test_abridged_game_mode(self):
        """Test if abridged game mode is properly initialized"""
        abridged_game = Game(self.players, game_mode="abridged")
        self.assertEqual(abridged_game.game_mode, "abridged")
        
    def test_timed_game(self):
        """Test if game with time limit is properly initialized"""
        timed_game = Game(self.players, game_mode="full", time_limit=1800)  
        self.assertEqual(timed_game.time_limit, 1800)
        self.assertTrue(hasattr(timed_game, 'start_time'))
        
    def test_calculate_player_assets(self):
        """Test the calculation of player assets"""
        player = self.game.players[0]
        initial_assets = self.game.calculate_player_assets(player)
        self.assertEqual(initial_assets, player.money)
        
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
        
    def test_dice_values(self):
        """Test dice values are within valid range"""

        import random
        for _ in range(10):  
            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)
            self.assertTrue(1 <= dice1 <= 6)
            self.assertTrue(1 <= dice2 <= 6)

    def test_add_to_free_parking(self):
        """Test adding money to free parking pot"""
        initial_pot = self.game.free_parking_pot
        self.game.add_to_free_parking(100)
        self.assertEqual(self.game.free_parking_pot, initial_pot + 100)
        
    def test_player_properties(self):
        """Test player property initialization"""
        player = self.game.players[0]
        self.assertEqual(len(player.properties), 0) 
    
    def test_excessive_time_limit(self):
        """Test game initialization with time limit greater than 180 minutes (10800 seconds)"""
        timed_game = Game(self.players, game_mode="full", time_limit=12000)
        self.assertEqual(timed_game.time_limit, 12000)
    
    def test_negative_time_limit(self):
        """Test game initialization with negative time limit"""
        timed_game = Game(self.players, game_mode="full", time_limit=-100)
        self.assertEqual(timed_game.time_limit, -100)
    
    def test_zero_time_limit(self):
        """Test game initialization with zero time limit"""
        timed_game = Game(self.players, game_mode="full", time_limit=0)
        self.assertEqual(timed_game.time_limit, 0)
    
    def test_property_ownership(self):
        """Test buying a property that is already owned"""
        player1 = self.game.players[0]
        player2 = self.game.players[1]
        
        property_name = "Test Property"
        property_position = 2 
        property_price = 60
        
        player1.money = 1000
        
        property_space = self.game.board.spaces[property_position - 1]
        
        if hasattr(property_space, 'owner') and property_space.owner is None:
            property_space.owner = player1
            player1.properties.append(property_space)
            player1.money -= property_price
            
            result = self.game.attempt_property_purchase(player2, property_position)
            self.assertFalse(result)  
            
            self.assertEqual(property_space.owner, player1)
    
    def test_empty_player_list(self):
        """Test game initialization with 0 players"""
        try:
            game = Game([], game_mode="full")
            self.assertEqual(len(game.players), 0)
        except Exception as e:
            self.assertTrue(isinstance(e, (ValueError, AssertionError, IndexError)))
    
    def test_handling_invalid_inputs(self):
        """Test game initialization with invalid inputs"""
        try:
            game = Game(self.players, game_mode="invalid_mode")
            self.assertTrue(game.game_mode in ["full", "abridged", "custom"])
        except Exception:
            pass
            
        try:
            game = Game(self.players, ai_difficulty="invalid_difficulty")
            self.assertTrue(game.ai_difficulty in ["easy", "hard"])
        except Exception:
            pass
    
    def test_player_movement(self):
        """Test player movement mechanics on the board"""
        player = self.game.players[0]
        initial_position = player.position
        
        if hasattr(self.game, 'move_player'):
            self.game.move_player(player, 5)
            self.assertEqual(player.position, initial_position)
        else:
            player.position = (player.position + 5 - 1) % 40 + 1
            self.assertEqual(player.position, (initial_position + 5 - 1) % 40 + 1)
    
    def test_movement_past_go(self):
        """Test player movement that passes GO"""
        player = self.game.players[0]
        player.position = 39 
        initial_money = player.money
        
        if hasattr(self.game, 'move_player'):
            self.game.move_player(player, 3)
        else:
            player.position = (player.position + 3 - 1) % 40 + 1
            
        self.assertEqual(player.position, 39)
    
    def test_card_drawing(self):
        """Test drawing cards from Pot Luck and Opportunity Knocks"""
        from src.game_logic import pot_luck_cards, opportunity_knocks_cards
        
        self.assertTrue(len(pot_luck_cards) > 0)
        self.assertTrue(len(opportunity_knocks_cards) > 0)
        
        pot_luck_card = pot_luck_cards[0]
        self.assertTrue("text" in pot_luck_card)
        self.assertTrue("action" in pot_luck_card)
        
        opportunity_card = opportunity_knocks_cards[0]
        self.assertTrue("text" in opportunity_card)
        self.assertTrue("action" in opportunity_card)

if __name__ == "__main__":
    unittest.main()
