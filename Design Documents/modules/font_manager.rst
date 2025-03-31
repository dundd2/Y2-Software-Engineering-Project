Font Manager Module
===================

This module contains the FontManager class that manages font loading, caching, and rendering throughout the Property Tycoon game.

Key Features
------------

* **Font Loading**: Loading and caching of game fonts for efficient reuse
* **Text Rendering**: Utilities for rendering text with various styles
* **Font Sizing**: Dynamic font size adjustment based on screen resolution
* **Font Types**: Support for different font styles (regular, bold, italic)
* **Efficient Caching**: Optimization through font caching for performance
* **Text Measurements**: Calculation of text dimensions for UI layout

FontManager Class
-----------------

The FontManager class handles all font-related operations:

.. plantuml::

   @startuml
   
   class FontManager {
     -fonts : Dict
     -font_files : Dict
     -default_font : String
     -cache : Dict
     
     +__init__()
     +load_fonts()
     +get_font(name, size)
     +render_text(text, font_name, size, color, antialias)
     +get_text_dimensions(text, font_name, size)
     +get_wrapped_text(text, font_name, size, max_width)
     +clear_cache()
     +add_font(name, path)
     +get_font_height(font_name, size)
     +get_line_height(font_name, size)
     +adjust_size_for_resolution(base_size, current_resolution, base_resolution)
}}}}}}}}}}}}}}}
   
   @enduml

Font Loading System
-------------------

The module implements a font loading system:

.. plantuml::

   @startuml
   
   title Font Loading System
   
   start
   
   :Initialize FontManager;
   
   :Define Font Paths;
   note right
     Map font names to
     file paths
   end note
   
   repeat
     :Load Font Resource;
     
     if (Font Already Loaded?) then (Yes)
       :Use Cached Font;
     else (No)
       :Load Font from File;
       
       if (Loading Successful?) then (Yes)
         :Add Font to Cache;
       else (No)
         :Use Fallback Font;
         note right
           Default to system font
           if font file missing
         end note
       endif
     endif
   repeat while (More Fonts?) is (Yes)
   
   :All Fonts Loaded;
   
   stop
   
   @enduml

Text Rendering
--------------

The module provides utilities for text rendering:

.. plantuml::

   @startuml
   
   title Text Rendering Process
   
   start
   
   :Request Text Rendering;
   
   :Get Font Parameters;
   note right
     - Font name
     - Size
     - Color
     - Style
   end note
   
   :Generate Cache Key;
   
   if (Text in Cache?) then (Yes)
     :Retrieve Rendered Surface;
   else (No)
     :Get Font Object;
     
     if (Font Available?) then (Yes)
       :Render Text to Surface;
       :Store in Cache;
     else (No)
       :Use Default Font;
       :Render Text to Surface;
       :Store in Cache;
     endif
   endif
   
   :Return Rendered Text Surface;
   
   stop
   
   @enduml

Text Wrapping System
--------------------

The module includes functionality for wrapping text:

.. plantuml::

   @startuml
   
   title Text Wrapping System
   
   start
   
   :Request Text Wrapping;
   
   :Get Font and Size;
   
   :Calculate Text Dimensions;
   
   if (Text Width > Max Width?) then (Yes)
     :Split Text into Words;
     
     :Initialize Line Buffer;
     
     repeat
       :Add Word to Current Line;
       
       :Calculate Current Line Width;
       
       if (Line Width > Max Width?) then (Yes)
         :Remove Last Word;
         :Add Line to Result;
         :Start New Line with Word;
       endif
     repeat while (More Words?) is (Yes)
     
     :Add Final Line to Result;
     
     :Join Lines with Line Breaks;
   else (No)
     :Return Original Text;
   endif
   
   :Return Wrapped Text;
   
   stop
   
   @enduml

Font Types
----------

The module supports different font types for various game contexts:

.. plantuml::

   @startuml
   
   title Font Types
   
   package "Game Fonts" {
     class "Title Font" as TitleFont {
       LibreBaskerville-Bold.ttf
       Used for game title and
       major headings
}}}}}}}}}}}}}}
     
     class "UI Font" as UIFont {
       Play-Regular.ttf
       Used for UI elements
       and buttons
}}}}}}}}}}}
     
     class "Property Font" as PropFont {
       Ticketing.ttf
       Used for property cards
       and prices
}}}}}}}}}}
     
     class "Body Font" as BodyFont {
       britrdn_.ttf
       Used for general text
       and descriptions
}}}}}}}}}}}}}}}}
   }
   
   class FontManager {
     +get_font(name, size)
}
   
   FontManager --> TitleFont : manages
   FontManager --> UIFont : manages
   FontManager --> PropFont : manages
   FontManager --> BodyFont : manages
   
   @enduml

Integration with Other Modules
------------------------------

The FontManager integrates with several other modules:

.. plantuml::

   @startuml
   
   title FontManager Integration
   
   class FontManager {
     +get_font(name, size)
     +render_text(text, font, color)
     +get_text_dimensions(text, font, size)
}}}}}}}}}}}}}}}}}}
   
   class UI {
     -font_manager : FontManager
     +draw_text(text, position, font, color)
     +create_button(text, position)
}}}}}}}}}}
   
   class Game {
     -font_manager : FontManager
     +initialize_resources()
}}}
   
   class PropertyCard {
     +draw(screen, font_manager)
}}}}}}}
   
   class PlayerInfoPanel {
     +draw(screen, font_manager)
}}}}}}}
   
   UI --> FontManager : uses
   Game --> FontManager : initializes
   PropertyCard --> FontManager : uses for rendering
   PlayerInfoPanel --> FontManager : uses for rendering
   
   @enduml

Performance Optimization
------------------------

The module implements several performance optimizations:

* **Font Caching**: Fonts are cached by name and size to avoid repeated loading
* **Rendered Text Caching**: Commonly used text renderings are cached
* **Lazy Loading**: Fonts are loaded only when needed
* **Memory Management**: Unused cache items can be cleared to free memory
* **Fallback System**: Default fonts are used when requested fonts are unavailable

Class Documentation
-----------------

.. automodule:: src.Font_Manager
   :members:
   :undoc-members:
   :show-inheritance: