import pygame
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

class GameBankruptcy:
    def __init__(self, screen, game_logic: GameLogic, board: Board):
        self.screen = screen
        self.logic = game_logic
        self.board = board
        self.font = font_manager.get_font(24)
        self.small_font = font_manager.get_font(18)

    # Split from original Game.py to improve code organization
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

