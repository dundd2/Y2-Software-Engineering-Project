Font Manager Module
===================

This module provides a `FontManager` class to handle loading and caching fonts. It supports scaling font sizes based on the current screen resolution to maintain visual consistency across different display sizes.

.. automodule:: src.Font_Manager
   :members:
   :undoc-members:
   :show-inheritance:

Diagrams
--------

**FontManager Class Structure**

.. uml::
   :caption: Structure of the FontManager class (using class methods)

   @startuml
   class FontManager {
       {static} - _instance: FontManager <<deprecated?>>
       {static} - _fonts: dict<tuple, pygame.font.Font>
       {static} - _current_font_path: str
       {static} - _base_width: int
       {static} - _base_height: int
       {static} - _scale_factor: float
       {static} + get_font(size: int) : pygame.font.Font
       {static} + update_font_path(new_font_path: str)
       {static} + update_scale_factor(width: int, height: int) : float
       {static} + get_scaled_size(base_size: int) : int
       {static} + clear_cache()
   }

   FontManager ..> "pygame.font" : uses >

   note right of FontManager
     Acts like a singleton through class methods.
     Caches loaded fonts for efficiency.
     Scales font sizes based on screen resolution.
     `_instance` seems unused if only class methods are used.
   end note
   @enduml

**Get Font Sequence (`get_font`)**