UI Module
========

This module contains the user interface components of the game, providing a modern, interactive interface for players to navigate menus, configure game settings, and interact with the game.

Key Features
-----------

* **Modern UI Components**: Custom buttons, input fields, and interactive elements
* **Multiple Game Pages**: Various screens for different game states and configurations
* **Responsive Design**: Adapts to different screen resolutions
* **Visual Effects**: Gradients, shadows, and animations for enhanced visual appeal
* **User Input Handling**: Comprehensive mouse and keyboard interaction
* **Game Configuration**: Settings for player count, AI difficulty, and game modes
* **Consistent Styling**: Unified color scheme and design language

UI Components
------------

The UI module implements several reusable components:

1. **ModernButton**: Interactive buttons with hover effects, images, and selection states
2. **ModernInput**: Text input fields for player names and other user input
3. **BasePage**: Foundation class for all game pages with common functionality

Color Scheme
-----------

The UI uses a consistent color palette:

* **Background**: Dark modern background (18, 18, 18)
* **Accent Color**: Blue highlight (75, 139, 190)
* **Text Colors**: White, light gray, and black for different contexts
* **Status Colors**: Red for errors, green for success
* **Player Colors**: Green for human players, red for AI players

Game Pages
---------

The module implements various game pages:

1. **MainMenuPage**: The main entry point with options to start game, adjust settings, etc.
2. **SettingsPage**: Configure game settings like screen resolution
3. **StartPage**: Set up players, including human and AI players
4. **PlayerSelectPage**: Alternative player selection interface
5. **GameModePage**: Select game mode and time limits
6. **EndGamePage**: Display game results and winner information
7. **HowToPlayPage**: Instructions for new players
8. **AIDifficultyPage**: Configure AI difficulty levels

Input Handling
------------

Each page implements three key methods for user interaction:

* **handle_click**: Process mouse clicks on UI elements
* **handle_motion**: Track mouse movement for hover effects
* **handle_key**: Process keyboard input for navigation and text entry


Class Documentation
-----------------

.. automodule:: src.ui
   :members:
   :undoc-members:
   :show-inheritance:

BasePage Class
------------

The ``BasePage`` class serves as the foundation for all game pages with the following features:

* **Background Rendering**: Draws the game background with gradients
* **Title Display**: Shows the game logo with visual effects
* **Font Management**: Initializes and manages different font sizes
* **Instructions Display**: Shows help text and instructions

ModernButton Class
---------------

The ``ModernButton`` class implements interactive buttons with:

* **Visual States**: Normal, hover, active, and selected states
* **Custom Styling**: Configurable colors and appearance
* **Image Support**: Optional button images
* **Interaction Handling**: Methods to check for mouse hover and clicks

ModernInput Class
--------------

The ``ModernInput`` class provides text input fields with:

* **Text Entry**: Support for keyboard text input
* **Visual Feedback**: Active, inactive, and error states
* **Placeholder Text**: Default text when empty
* **Selection State**: Visual indication when selected

Page Navigation
-------------

The UI system implements a page-based navigation flow:

1. The game starts at the MainMenuPage
2. User selections trigger transitions to other pages
3. Each page returns results that determine the next page
4. The game loop manages page transitions based on user input

Responsive Design
--------------

The UI adapts to different screen resolutions:

* **Dynamic Sizing**: UI elements scale based on screen size
* **Text Scaling**: Font sizes adjust for readability
* **Resolution Options**: Multiple resolution options in settings
* **Window Management**: Proper handling of window resizing 