UI Module
=========

The UI Module provides a collection of user interface components and page structures for the Property Tycoon game. It handles rendering visual elements like buttons and input fields, manages different game screens (pages), and processes user interactions (clicks, key presses) related to the UI. It relies heavily on the Pygame library for drawing and event handling, and uses Font_Manager and Sound_Manager for assets.

High-Level Design
-----------------

Use Case Diagram
~~~~~~~~~~~~~~~~

This diagram shows the main interactions a user can have with the UI system.

.. uml::
   :caption: UI Module Use Cases

   @startuml
   skinparam usecase {
     BackgroundColor White
     BorderColor Black
   }
   
   left to right direction
   actor User
   
   rectangle "Property Tycoon UI" {
     usecase "Start New Game" as Start
     usecase "View How to Play" as HowTo
     usecase "View Keyboard Shortcuts" as Shortcuts
     usecase "Change Settings" as Settings
     usecase "Setup Players" as Setup
     usecase "Select Game Mode" as GameMode
     usecase "Select AI Difficulty" as AIDiff
     usecase "View Credits" as Credits
     usecase "Quit Game" as Quit
     usecase "Interact with AI Mood UI" as AIMood
     
     User --> Start
     User --> HowTo
     User --> Shortcuts
     User --> Settings
     User --> Setup
     User --> GameMode
     User --> AIDiff
     User --> Credits
     User --> Quit
     User --> AIMood : <<in-game>>
     
     Start ..> Setup : <<include>>
     Setup ..> AIDiff : <<include>>
     Setup ..> GameMode : <<include>>
     HowTo ..> Shortcuts : <<include>>
   }
   @enduml

Dependency Diagram
~~~~~~~~~~~~~~~~~~

Shows the primary external libraries and internal modules the UI components depend on.

.. uml::
   :caption: UI Module Dependencies

   @startuml
   package "UI Module" {
     (UIButton)
     (UIInput)
     (BasePage)
     (MainMenuPage)
     (SettingsPage)
     (StartPage)
     (HowToPlayPage)
     (KeyboardShortcutsPage)
     (GameModePage)
     (EndGamePage)
     (CreditsPage)
     (AIDifficultyPage)
     (AIEmotionUI)
   }

   package "External Libraries" {
     (pygame)
     (os)
     (webbrowser)
     (random)
     (sys)
     (time)
     (math)
   }

   package "Internal Modules" {
      (Font_Manager)
      (Sound_Manager)
      (Game)
      (AIPlayer)
   }

   (UI Module) --> (pygame)
   (UI Module) --> (os)
   (UI Module) --> (webbrowser)
   (UI Module) --> (random)
   (UI Module) --> (sys)
   (UI Module) --> (time)
   (UI Module) --> (math)

   (UI Module) --> (Font_Manager)
   (UI Module) --> (Sound_Manager)

   (AIEmotionUI) --> (Game)
   (AIEmotionUI) --> (AIPlayer)
   @enduml

Detailed Design
---------------

Class Diagrams
~~~~~~~~~~~~~~

**Core UI Elements**

.. uml::
   :caption: Core UI Elements Class Diagram

   class UIButton {
     - rect: pygame.Rect
     - text: str
     - font: pygame.font.Font
     - color: tuple
     - hover: bool
     - active: bool
     - is_selected: bool
     - image: pygame.Surface
     - shadow_height: int
     - border_width: int
     + draw(screen: pygame.Surface)
     + check_hover(pos: tuple): bool
     - _draw_basic_button(screen: pygame.Surface, base_color: tuple)
   }

   class UIInput {
     - rect: pygame.Rect
     - text: str
     - font: pygame.font.Font
     - active_color: tuple
     - inactive_color: tuple
     - active: bool
     - placeholder: str
     - is_selected: bool
     - error: bool
     - background_alpha: int
     + draw(screen: pygame.Surface)
   }

   UIButton ..> pygame.Rect
   UIButton ..> pygame.font.Font
   UIButton ..> pygame.Surface
   UIInput ..> pygame.Rect
   UIInput ..> pygame.font.Font

**Page Hierarchy**

.. uml::
   :caption: Page Hierarchy Class Diagram

   abstract class BasePage {
     # screen: pygame.Surface
     # logo_image: pygame.Surface
     # background_image: pygame.Surface
     # title_font: pygame.font.Font
     # button_font: pygame.font.Font
     # version_font: pygame.font.Font
     # small_font: pygame.font.Font
     # instructions: list
     + draw_background()
     + draw_title()
     + draw_instructions()
     + draw()
     + handle_click(pos: tuple): any <<virtual>>
     + handle_motion(pos: tuple) <<virtual>>
     + handle_key(event: pygame.Event): any <<virtual>>
   }

   note right of BasePage::handle_click
     Return value often indicates
     navigation or action status.
   end note

   class MainMenuPage extends BasePage {
     - start_button: UIButton
     - how_to_play_button: UIButton
     - settings_button: UIButton
     - youtube_logo: pygame.Surface
     - github_logo: pygame.Surface
     + draw()
     + handle_click(pos: tuple): str
     + handle_motion(pos: tuple)
     + handle_key(event: pygame.Event): str
   }

   class SettingsPage extends BasePage {
     - resolution_options: list
     - font_options: list
     - current_resolution: int
     - current_font: int
     - sound_volume: int
     - music_volume: int
     - resolution_button: UIButton
     - font_button: UIButton
     - sound_volume_button: UIButton
     - music_volume_button: UIButton
     - confirm_button: UIButton
     - back_button: UIButton
     - test_sound_button: UIButton
     - test_music_button: UIButton
     + draw()
     + handle_click(pos: tuple): any
     + handle_motion(pos: tuple)
     + handle_key(event: pygame.Event): any
     + get_settings(): dict
   }

   class StartPage extends BasePage {
     - human_count: int
     - ai_count: int
     - player_names: list
     - ai_names: list
     - token_images: list
     - player_token_indices: list
     - ai_token_indices: list
     - name_inputs: list<UIInput>
     - human_minus_button: UIButton
     - human_plus_button: UIButton
     - ai_minus_button: UIButton
     - ai_plus_button: UIButton
     - start_button: UIButton
     - back_button: UIButton
     - token_selection_active: bool
     + draw()
     + draw_token_selection()
     + handle_click(pos: tuple): any
     + handle_token_selection_click(pos: tuple): bool
     + handle_motion(pos: tuple)
     + handle_key(event: pygame.Event): any
     + get_player_info(): tuple
   }

   class HowToPlayPage extends BasePage {
     - back_button: UIButton
     - shortcuts_button: UIButton
     + draw()
     + handle_click(pos: tuple): any
     + handle_motion(pos: tuple)
     + handle_key(event: pygame.Event): any
   }

   class KeyboardShortcutsPage extends BasePage {
      - back_button: UIButton
      - shortcuts: list
      + draw()
      + handle_click(pos: tuple): any
      + handle_motion(pos: tuple)
      + handle_key(event: pygame.Event): any
   }

   class GameModePage extends BasePage {
     - game_mode: str
     - time_limit: int
     - custom_time_input: UIInput
     - mode_button: UIButton
     - start_button: UIButton
     - back_button: UIButton
     + draw()
     + handle_click(pos: tuple): any
     + handle_motion(pos: tuple)
     + handle_key(event: pygame.Event): any
     + get_game_settings(): dict
   }

   class EndGamePage extends BasePage {
     - winner_name: str
     - final_assets: dict
     - bankrupted_players: list
     - voluntary_exits: list
     - tied_winners: list
     - lap_count: dict
     - credits_button: UIButton
     - confetti: list
     + draw()
     + handle_click(pos: tuple): str
     + handle_motion(pos: tuple)
     + handle_key(event: pygame.Event): str
   }

    class CreditsPage extends BasePage {
      - back_button: UIButton
      - developers: list
      + draw()
      + handle_click(pos: tuple): any
      + handle_motion(pos: tuple)
      + handle_key(event: pygame.Event): any
    }

    class AIDifficultyPage extends BasePage {
      - easy_button: UIButton
      - hard_button: UIButton
      - back_button: UIButton
      + draw()
      + handle_click(pos: tuple): str
      + handle_motion(pos: tuple)
      + handle_key(event: pygame.Event): str
    }

    ' PlayerSelectPage also exists but seems less central than StartPage
    ' class PlayerSelectPage extends BasePage { ... }

    MainMenuPage *-- "many" UIButton
    SettingsPage *-- "many" UIButton
    StartPage *-- "many" UIButton
    StartPage *-- "many" UIInput
    GameModePage *-- "many" UIButton
    GameModePage *-- UIInput
    EndGamePage *-- "many" UIButton
    HowToPlayPage *-- "many" UIButton
    KeyboardShortcutsPage *-- "many" UIButton
    CreditsPage *-- "many" UIButton
    AIDifficultyPage *-- "many" UIButton

    MainMenuPage ..> webbrowser : uses
    SettingsPage ..> Sound_Manager : uses
    StartPage ..> pygame.image : uses
    EndGamePage ..> random : uses
    CreditsPage ..> Sound_Manager : uses

**AI Emotion UI**

.. uml::
   :caption: AI Emotion UI Class Diagram

   class AIEmotionUI {
     - screen: pygame.Surface
     - ai_player: AIPlayer ' Assuming AIPlayer class exists
     - game_instance: Game ' Assuming Game class exists
     - visible: bool
     - panel_rect: pygame.Rect
     - happy_button_rect: pygame.Rect
     - angry_button_rect: pygame.Rect
     - happy_image: pygame.Surface
     - angry_image: pygame.Surface
     - happy_hover: bool
     - angry_hover: bool
     - font: pygame.font.Font
     - happy_clicks_after_limit: int
     - angry_clicks_after_limit: int
     - easter_egg_threshold: int
     - youtube_url: str
     - easter_egg_triggered: bool
     + show()
     + hide()
     + draw()
     + check_hover(pos: tuple): bool
     + handle_click(pos: tuple): bool
     + handle_key(event: pygame.Event): bool
     - _check_easter_egg()
   }

   AIEmotionUI ..> Font_Manager : uses
   AIEmotionUI ..> Sound_Manager : uses
   AIEmotionUI ..> webbrowser : uses
   AIEmotionUI ..> "Game" : uses >
   AIEmotionUI ..> "AIPlayer" : uses > ' Or AIController

Sequence Diagrams
~~~~~~~~~~~~~~~~~

**Main Menu Navigation**

.. uml::
   :caption: Sequence Diagram: Main Menu Navigation

   actor User
   participant "main_menu:MainMenuPage" as MainMenu
   participant "main_loop" as Loop

   User -> MainMenu : click(pos)
   activate MainMenu
   MainMenu -> MainMenu : handle_click(pos)
   alt start_button clicked
     MainMenu --> Loop : return "start"
   else how_to_play_button clicked
     MainMenu --> Loop : return "how_to_play"
   else settings_button clicked
     MainMenu --> Loop : return "settings"
   else social media icon clicked
     MainMenu -> webbrowser : open(url)
     MainMenu --> Loop : return None
   else
     MainMenu --> Loop : return None
   end
   deactivate MainMenu

   Loop -> Loop : Change state (e.g., show StartPage)

**Changing a Setting**

.. uml::
   :caption: Sequence Diagram: Changing a Setting

   actor User
   participant "settings_page:SettingsPage" as Settings
   participant "main_loop" as Loop
   participant "font_manager:Font_Manager" as FM
   participant "sound_manager:Sound_Manager" as SM

   User -> Settings : click(pos on resolution_button)
   activate Settings
   Settings -> Settings : handle_click(pos)
   Settings -> Settings : current_resolution = (current_resolution + 1) % len(options)
   Settings -> Settings : show_confirmation = True
   Settings --> User : return False (stay on page)
   deactivate Settings

   User -> Settings : click(pos on sound_volume_button)
   activate Settings
   Settings -> Settings : handle_click(pos)
   Settings -> Settings : sound_volume = (sound_volume + 10) % 110
   Settings -> SM : set_sound_volume(new_volume)
   Settings -> Settings : show_confirmation = True
   Settings --> User : return False (stay on page)
   deactivate Settings

   User -> Settings : click(pos on confirm_button)
   activate Settings
   Settings -> Settings : handle_click(pos)
   opt resolution or font changed
       Settings -> FM : update_font_path(new_path)
       note right: Pygame screen resize might also happen here (handled by main loop based on return value)
       Settings --> Loop : return True (apply changes)
   else
       Settings --> Loop : return False (no changes to apply)
   end
   deactivate Settings

   Loop -> Loop : Handle return value (e.g., recreate screen, change page)

**Player Setup (StartPage)**

.. uml::
    :caption: Sequence Diagram: Player Setup Interaction

    actor User
    participant "start_page:StartPage" as StartPage
    participant "name_input:UIInput" as Input
    participant "main_loop" as Loop

    User -> StartPage : click(pos on human_plus_button)
    activate StartPage
    StartPage -> StartPage : handle_click(pos)
    opt total_players < 5
        StartPage -> StartPage : human_count += 1
        StartPage -> StartPage : update_player_lists()
        StartPage -> StartPage : total_players = human_count + ai_count
    end
    StartPage --> User : return False
    deactivate StartPage

    User -> StartPage : click(pos on name_input field)
    activate StartPage
    StartPage -> StartPage : handle_click(pos)
    StartPage -> StartPage : active_input = index
    StartPage --> User : return False
    deactivate StartPage

    User -> StartPage : key_press(event='A')
    activate StartPage
    StartPage -> StartPage : handle_key(event)
    opt active_input >= 0 and < human_count
        StartPage -> StartPage : player_names(active_input) += 'A'
    end
    StartPage --> User : return False
    deactivate StartPage

    User -> StartPage : click(pos on token icon)
    activate StartPage
    StartPage -> StartPage : handle_click(pos)
    StartPage -> StartPage : token_selection_active = True
    StartPage -> StartPage : token_selection_for_player = index
    StartPage -> StartPage : token_selection_is_ai = is_ai
    StartPage --> User : return False
    deactivate StartPage
    ' (Token selection UI is now drawn)

    User -> StartPage : click(pos on start_button)
    activate StartPage
    StartPage -> StartPage : handle_click(pos)
    opt all names valid and player count valid
        StartPage -> StartPage : get_player_info()
        StartPage --> Loop : return True (start game)
    else
        StartPage --> User : return False
    end
    deactivate StartPage

**Game Mode Selection**

.. uml::
    :caption: Sequence Diagram: Game Mode Selection

    actor User
    participant "mode_page:GameModePage" as ModePage
    participant "time_input:UIInput" as Input
    participant "main_loop" as Loop

    User -> ModePage : click(pos on mode_button)
    activate ModePage
    ModePage -> ModePage : handle_click(pos)
    ModePage -> ModePage : game_mode = "abridged" / "full"
    opt game_mode == "abridged"
        ModePage -> ModePage : time_limit = default or current input value
    else
        ModePage -> ModePage : time_limit = None
    end
    ModePage --> User : return False
    deactivate ModePage

    User -> ModePage : click(pos on time_input)
    activate ModePage
    ModePage -> ModePage : handle_click(pos)
    opt game_mode == "abridged"
        ModePage -> Input : active = True
    end
    ModePage --> User : return False
    deactivate ModePage

    User -> ModePage : key_press(event='5')
    activate ModePage
    ModePage -> ModePage : handle_key(event)
    opt Input.active == True
        ModePage -> Input : text += '5'
    end
    ModePage --> User : return False
    deactivate ModePage

    User -> ModePage : click(pos on start_button)
    activate ModePage
    ModePage -> ModePage : handle_click(pos)
    opt game_mode == "abridged"
        ModePage -> ModePage : validate time_input.text
        alt valid time
            ModePage -> ModePage : time_limit = parsed_time * 60
            ModePage -> ModePage : get_game_settings()
            ModePage --> Loop : return True
        else invalid time
            ModePage -> ModePage : input_error = "Error message"
            ModePage --> User : return False
        end
    else game_mode == "full"
        ModePage -> ModePage : get_game_settings()
        ModePage --> Loop : return True
    end
    deactivate ModePage

**AI Mood Interaction**

.. uml::
    :caption: Sequence Diagram: AI Mood Interaction

    actor User
    participant "emotion_ui:AIEmotionUI" as EmotionUI
    participant "game:Game" as Game
    participant "sound_manager:Sound_Manager" as SM
    participant "webbrowser" as WB

    User -> EmotionUI : click(pos on happy_button)
    activate EmotionUI
    EmotionUI -> EmotionUI : handle_click(pos)
    EmotionUI -> SM : play_sound("happy_click")
    EmotionUI -> Game : update_ai_mood(ai_player.name, False)
    EmotionUI -> EmotionUI : check mood limit
    opt mood >= limit
        EmotionUI -> EmotionUI : happy_clicks_after_limit += 1
        EmotionUI -> EmotionUI : _check_easter_egg()
        opt clicks >= threshold and not triggered
            EmotionUI -> WB : open(youtube_url)
            EmotionUI -> EmotionUI : easter_egg_triggered = True
        end
    end
    EmotionUI --> User : return True
    deactivate EmotionUI


Key Classes Overview
--------------------

*   **UIButton**: A standard clickable button with text or image, hover effects, and active/inactive states.
*   **UIInput**: A text input field allowing user text entry, with active/inactive states and placeholder text.
*   **BasePage**: The foundation for all game screens, providing common drawing logic (background, title) and defining the interface for handling events.
*   **MainMenuPage**: The initial screen with options to start, view instructions, or change settings. Includes social media links.
*   **SettingsPage**: Allows modification of screen resolution, font, and sound/music volume. Interacts with `Sound_Manager` and `Font_Manager`.
*   **StartPage**: Handles the setup of human and AI players, including name entry and token selection. Manages player counts and associated data.
*   **HowToPlayPage**: Displays basic game instructions.
*   **KeyboardShortcutsPage**: Displays a list of keyboard shortcuts for game actions.
*   **GameModePage**: Allows selection between a full game or an abridged (timed) game, including setting a time limit.
*   **EndGamePage**: Shown after the game concludes, displaying the winner, final scores, and options to play again or quit. Includes a confetti effect.
*   **CreditsPage**: Displays the list of developers and special thanks.
*   **AIDifficultyPage**: Allows the user to select the difficulty level for AI opponents.
*   **AIEmotionUI**: An in-game UI element specifically for interacting with an AI player's mood, featuring visual feedback and an easter egg.

API Documentation
-----------------

.. automodule:: src.UI
   :members:
   :undoc-members:
   :show-inheritance: