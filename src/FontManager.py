import pygame
import os
from src.text_scaler import text_scaler

class FontManager:
    _instance = None
    _fonts = {}
    _current_font_path = None
    
    @classmethod
    def get_font(cls, size):
        if cls._current_font_path is None:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cls._current_font_path = os.path.join(base_path, "assets", "font", "Ticketing.ttf")
            
        cache_key = (cls._current_font_path, size)
        if cache_key not in cls._fonts:
            try:
                cls._fonts[cache_key] = pygame.font.Font(cls._current_font_path, size)
            except (pygame.error, FileNotFoundError) as e:
                print(f"Error loading font {cls._current_font_path}: {e}")
                cls._fonts[cache_key] = pygame.font.Font(None, size)
        return cls._fonts[cache_key]
    
    @classmethod
    def update_font_path(cls, new_font_path):
        if cls._current_font_path != new_font_path:
            cls._current_font_path = new_font_path
            cls._fonts.clear() 

    @classmethod
    def clear_cache(cls):
        """Clear the font cache"""
        cls._fonts.clear()
        
    @classmethod
    def update_scale_factor(cls, width, height):
        """Update font scaling when resolution changes"""
        cls.clear_cache()  
        return text_scaler.update_scale_factor(width, height)