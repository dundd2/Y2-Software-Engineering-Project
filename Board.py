# Base on PropertyTycoonCardData.xlsx from canvas 
# script based on Eric's provided flowchart photo (flowchart.drawio.png)
# will add more comment later to reference for which part of code is based on which part of the flowchart

import pygame
import math
import os
from Property import Property
from typing import Optional, List
from loadexcel import load_property_data
from text_scaler import text_scaler

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
MODERN_BG = (18, 18, 18)
ACCENT_COLOR = (75, 139, 190)
SUCCESS_COLOR = (40, 167, 69)
ERROR_COLOR = (220, 53, 69)

class CameraControls:
    def __init__(self):
        self.zoom_level = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.move_speed = 5
        self.zoom_speed = 0.05
        self.min_zoom = 0.5
        self.max_zoom = 2.0

    def handle_camera_controls(self, keys):
        if keys[pygame.K_PLUS] or keys[pygame.K_EQUALS]:
            self.zoom_level = min(self.max_zoom, self.zoom_level + self.zoom_speed)
        if keys[pygame.K_MINUS]:
            self.zoom_level = max(self.min_zoom, self.zoom_level - self.zoom_speed)

        adjusted_speed = self.move_speed * (1 / self.zoom_level)

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.offset_y -= adjusted_speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.offset_y += adjusted_speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.offset_x -= adjusted_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.offset_x += adjusted_speed

        window_size = pygame.display.get_surface().get_size()
        max_offset = window_size[0] // 4
        self.offset_x = max(min(self.offset_x, max_offset), -max_offset)
        self.offset_y = max(min(self.offset_y, max_offset), -max_offset)

        return self.zoom_level, self.offset_x, self.offset_y

class Board:
    def __init__(self, players):
        self.players = players
        self.spaces = [None] * 40
        self.properties_data = load_property_data()
        self.camera = CameraControls()
        
        self.project_root = os.path.abspath(os.path.dirname(__file__))
        
        try:
            self.board_image = pygame.image.load(os.path.join(self.project_root, "assets/image/board.png"))
            self.board_image = self.board_image.convert_alpha() if self.board_image.get_alpha() else self.board_image.convert()
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load board image: {e}")
            self.board_image = None
            
        try:
            self.background_image = pygame.image.load(os.path.join(self.project_root, "assets/image/background.jpg"))
            self.background_image = self.background_image.convert()
        except (pygame.error, FileNotFoundError) as e:
            print(f"Could not load background image: {e}")
            self.background_image = None

        self.board_rects = self._create_board_rects()
        self.messages = []
        self.message_times = []
        self.message_font = pygame.font.Font('assets/font/Play-Regular.ttf', text_scaler.get_scaled_size(20))

    def add_message(self, text):
        self.messages.append(text)
        self.message_times.append(pygame.time.get_ticks())
        if len(self.messages) > 10:
            self.messages.pop(0)
            self.message_times.pop(0)

    def _create_board_rects(self):
        screen_info = pygame.display.Info()
        window_width = screen_info.current_w
        window_height = screen_info.current_h
        base_board_size = min(window_width, window_height) * 0.8
        board_size = base_board_size * self.camera.zoom_level
        
        corner_size = board_size // 11
        normal_width = corner_size
        normal_height = int(normal_width * (5/8))
        
        start_x = ((window_width - board_size) // 2) + self.camera.offset_x
        start_y = ((window_height - board_size) // 2) + self.camera.offset_y
        
        rects = []
        
        for i in range(11):
            width = corner_size if (i == 0 or i == 10) else normal_width
            height = corner_size if (i == 0 or i == 10) else normal_height
            x = start_x + board_size - (i + 1) * normal_width
            y = start_y + board_size - height
            rects.append(pygame.Rect(x, y, width, height))
        
        for i in range(11, 21):
            width = corner_size if i == 20 else normal_height
            height = corner_size if i == 20 else normal_width
            x = start_x
            y = start_y + board_size - ((i - 9) * normal_width)
            rects.append(pygame.Rect(x, y, width, height))
        
        for i in range(21, 31):
            width = corner_size if (i == 20 or i == 30) else normal_width
            height = corner_size if (i == 20 or i == 30) else normal_height
            x = start_x + (i - 20) * normal_width
            y = start_y
            rects.append(pygame.Rect(x, y, width, height))
        
        # Right column (positions 31-39)
        for i in range(31, 40):
            width = corner_size if i == 30 else normal_height
            height = corner_size if i == 30 else normal_width
            x = start_x + board_size - width
            y = start_y + (i - 30) * normal_width
            rects.append(pygame.Rect(x, y, width, height))
        
        return rects

    def update_board_positions(self):
        self.board_rects = self._create_board_rects()
        for player in self.players:
            if 1 <= player.position <= 40:
                player_rect = self.board_rects[player.position - 1]
                player.rect = player_rect

    def draw_player(self, screen, player, rect, index):
        is_corner = rect.width > rect.height + 10 or rect.height > rect.width + 10
        row = index // 2
        col = index % 2
        base_padding = 12 if is_corner else 8
        spacing = 35 if is_corner else 30
        
        if rect.width > rect.height + 10:
            pos_x = rect.x + base_padding + (col * spacing)
            pos_y = rect.y + (rect.height - 40) // 2 + (row * spacing // 2)
        elif rect.height > rect.width + 10:
            pos_x = rect.x + (rect.width - 40) // 2 + (col * spacing // 2)
            pos_y = rect.y + base_padding + (row * spacing)
        else:
            pos_x = rect.x + base_padding + (col * spacing)
            pos_y = rect.y + base_padding + (row * spacing)

        glow_surface = pygame.Surface((44, 44), pygame.SRCALPHA)
        for i in range(4):
            alpha = int(100 * (1 - i/4))
            pygame.draw.rect(glow_surface, (*player.color[:3], alpha),
                            pygame.Rect(i, i, 44 - i*2, 44 - i*2),
                            border_radius=5)
        screen.blit(glow_surface, (pos_x - 2, pos_y - 2 - player.animation_offset))

        if player.player_image:
            token_rect = pygame.Rect(pos_x, pos_y - player.animation_offset, 40, 40)
            screen.blit(player.player_image, token_rect)
        else:
            pygame.draw.circle(screen, player.color, (pos_x + 20, pos_y + 20 - player.animation_offset), 20)

    def draw(self, screen):
        window_width = screen.get_width()
        window_height = screen.get_height()
        base_board_size = int(window_height * 0.9)
        board_size = int(base_board_size * self.camera.zoom_level)
        board_size = max(1, board_size)

        game_surface = pygame.Surface((window_width, window_height))
        game_surface.fill(WHITE)

        if self.background_image:
            game_surface.blit(self.background_image, (0, 0))
        else:
            game_surface.fill(MODERN_BG)

        keys = pygame.key.get_pressed()
        zoom, offset_x, offset_y = self.camera.handle_camera_controls(keys)
        self.camera.zoom_level = zoom
        self.camera.offset_x = offset_x
        self.camera.offset_y = offset_y
        
        self.update_board_positions()

        board_x = ((window_width - board_size) // 2) + self.camera.offset_x
        board_y = ((window_height - board_size) // 2) + self.camera.offset_y

        board_surface = pygame.Surface((board_size, board_size))
        board_surface.fill(WHITE)
        if self.board_image:
            scaled_board = pygame.transform.scale(self.board_image, (board_size, board_size))
            board_surface.blit(scaled_board, (0, 0))
        game_surface.blit(board_surface, (board_x, board_y))

        transparent_surface = pygame.Surface((window_width, window_height), pygame.SRCALPHA)
        
        for player in self.players:
            if not isinstance(player.position, int):
                player.position = 1
            pos_index = max(0, min(player.position - 1, len(self.board_rects) - 1))
            player_rect = self.board_rects[pos_index]
            self.draw_player(transparent_surface, player, player_rect, player.player_number)

        info_panel_width = 300
        info_panel_height = 100
        info_panel_x = 20
        info_panel_y = window_height - info_panel_height - 20

        panel_shadow = pygame.Surface((info_panel_width + 8, info_panel_height + 8), pygame.SRCALPHA)
        for i in range(4):
            alpha = int(100 * (1 - i/4))
            pygame.draw.rect(panel_shadow, (*BLACK, alpha),
                           pygame.Rect(i, i, info_panel_width + 8 - i*2, info_panel_height + 8 - i*2),
                           border_radius=10)
        transparent_surface.blit(panel_shadow, (info_panel_x - 4, info_panel_y - 4))
        
        info_panel = pygame.Surface((info_panel_width, info_panel_height), pygame.SRCALPHA)
        pygame.draw.rect(info_panel, (*MODERN_BG, 200), info_panel.get_rect(), border_radius=10)
        transparent_surface.blit(info_panel, (info_panel_x, info_panel_y))
        
        line_height = self.message_font.get_height() + 5
        max_messages = (info_panel_height - 20) // line_height
        visible_messages = self.messages[-max_messages:]
        text_y = info_panel_y + 10
        
        for message in visible_messages:
            text = self.message_font.render(message, True, WHITE)
            transparent_surface.blit(text, (info_panel_x + 10, text_y))
            text_y += line_height
            
        game_surface.blit(transparent_surface, (0, 0))
        screen.blit(game_surface, (0, 0))

    def get_space(self, position):
        array_pos = (position - 1) % 40
        if 0 <= array_pos < len(self.spaces):
            return self.spaces[array_pos]
        return None

    def update_ownership(self, properties_data):
        for position_str, prop_data in properties_data.items():
            try:
                position = int(position_str)
                array_pos = position - 1
                if 0 <= array_pos < 40 and self.spaces[array_pos]:
                    self.spaces[array_pos].owner = prop_data.get("owner")
            except (ValueError, TypeError) as e:
                print(f"Error updating ownership for position {position_str}: {e}")

    def get_property_group(self, position):
        if str(position) in self.properties_data:
            return self.properties_data[str(position)].get("group")
        return None