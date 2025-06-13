Font Manager Module
===================

This module provides a centralized `FontManager` class responsible for loading, caching, and scaling fonts used throughout the Property Tycoon application. It ensures consistent font usage and adapts font sizes dynamically based on the current screen resolution, maintaining readability across different display sizes.

The Font Manager module provides:

*   A mechanism to load TrueType Fonts (`.ttf`) from a specified path.
*   Caching of loaded `pygame.font.Font` objects to improve performance by avoiding redundant file loading.
*   Automatic scaling of requested font sizes based on the current screen dimensions relative to a base resolution (1280x720).
*   A global `font_manager` instance for easy access from other modules.
*   Methods to update the font path or recalculate the scale factor, clearing the cache when necessary.


.. automodule:: src.Font_Manager
   :members:
   :undoc-members:
   :show-inheritance:

Detailed Design
---------------

 FontManager Class Diagram

This diagram illustrates the structure of the `FontManager` class, emphasizing its use of class attributes and methods to manage font resources globally.

.. uml::

    @startuml
    class FontManager <<Singleton>> {
        {static} - _instance : FontManager = None ' Conceptual instance, access via class
        {static} - _fonts : Dict(tuple, pygame.font.Font) = {} ' Cache: (path, scaled_size) -> Font
        {static} - _current_font_path : str = None
        {static} - _base_width : int = 1280
        {static} - _base_height : int = 720
        {static} - _scale_factor : float = 1.0

        {static} + get_font(size: int) : pygame.font.Font
        {static} + update_font_path(new_font_path: str)
        {static} + update_scale_factor(width: int, height: int) : float
        {static} + get_scaled_size(base_size: int) : int
        {static} + clear_cache()
    }

    class "pygame.font.Font" as PygameFont

    FontManager ..> PygameFont : creates & caches >
    FontManager ..> os : uses for path operations >
    FontManager ..> pygame : uses for font loading & errors >

    note right of FontManager::_fonts
      Cache stores loaded fonts.
      Key is (font_path, scaled_size).
    end note
    note right of FontManager::_scale_factor
      Determines how much to scale
      base font sizes based on current
      screen resolution vs base resolution.
    end note
    @enduml


 Sequence Diagram: Getting a Font

Shows the process of requesting a font from the `FontManager`, including scaling and cache interaction.

.. uml::

    @startuml
    participant "Client Module" as Client <<e.g., UI, Renderer>>
    participant "font_manager" as FM <<FontManager>>
    participant "pygame" as Pygame

    Client -> FM : get_font(base_size)
    activate FM
    FM -> FM : scaled_size = get_scaled_size(base_size)
    activate FM
    FM -> FM : return int(base_size * _scale_factor)
    deactivate FM
    FM -> FM : cache_key = (_current_font_path, scaled_size)
    alt cache_key in _fonts
        FM -> FM : font = _fonts(cache_key)
        FM --> Client : font
    else cache_key not in _fonts
        FM -> Pygame : font.Font(_current_font_path, scaled_size)
        alt Font Loaded Successfully
            Pygame --> FM : new_font
            FM -> FM : _fonts(cache_key) = new_font
            FM --> Client : new_font
        else Font Load Error (e.g., FileNotFoundError)
            Pygame -->> FM : Raise Exception
            FM -> Pygame : font.Font(None, scaled_size) ' Load default system font
            Pygame --> FM : default_font
            FM -> FM : _fonts(cache_key) = default_font
            FM --> Client : default_font
        end
    end
    deactivate FM
    @enduml


 Sequence Diagram: Updating Scale Factor

Illustrates how the scale factor is updated (e.g., on window resize) and how it affects the cache.

.. uml::

    @startuml
    participant "Main Module" as Main
    participant "font_manager" as FM <<FontManager>>

    Main -> FM : update_scale_factor(new_width, new_height)
    activate FM
    FM -> FM : Calculate width_scale = new_width / _base_width
    FM -> FM : Calculate height_scale = new_height / _base_height
    FM -> FM : _scale_factor = min(width_scale, height_scale)
    FM -> FM : clear_cache()
    activate FM
    FM -> FM : _fonts.clear()
    deactivate FM
    FM --> Main : _scale_factor
    deactivate FM
    @enduml