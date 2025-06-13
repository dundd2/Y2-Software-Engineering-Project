Main Module
===========

The Main module serves as the entry point for the Property Tycoon game application. It initializes the core game environment, manages the main application loop, orchestrates transitions between different game states (like menus, gameplay, and end screens), and handles the overall flow of the application from startup to shutdown.

The Main module is responsible for:

*   Initializing Pygame, sound, fonts, and logging.
*   Displaying introductory logo screens (`show_company_logo`, `show_logo_screen`).
*   Managing the main menu and navigation between different UI pages (Settings, How To Play, Start Game configuration) within the main `async def main()` loop.
*   Gathering game configuration (players, AI settings, game mode) through interaction with UI pages like `StartPage`, `AIDifficultyPage`, and `GameModePage`.
*   Creating the core `Game` object and `Player` objects via the `create_game` function.
*   Running the main game loop via the `async def run_game()` function, which utilizes `GameRenderer`, `GameEventHandler`, and `GameActions`.
*   Handling the end-game sequence via the `async def handle_end_game()` function, displaying results using `EndGamePage`.
*   Managing window resizing and applying settings via `async def apply_screen_settings()`.
*   Ensuring safe application shutdown via `safe_exit()`.

.. automodule:: Main
   :members:
   :undoc-members:
   :show-inheritance:

High-Level Design
-----------------

Use Case Diagram
~~~~~~~~~~~~~~~~

.. uml::
   :caption: Main Module Use Cases

   @startuml
   left to right direction
   actor User

   rectangle "Property Tycoon Application (Main Module)" {
     User -- (Start Application)
     User -- (Navigate Menus)
     (Navigate Menus) ..> (Configure Game Settings) : includes
     (Navigate Menus) ..> (View How To Play) : includes
     (Navigate Menus) ..> (Start New Game) : includes
     (Start New Game) --> (Play Game)
     (Play Game) --> (View End Game Screen)
     User -- (Exit Application)

     (Start Application) .> (Initialize Environment) : includes
     note right of (Initialize Environment)
       Pygame, Sound, Logging, Fonts
     end note
     (Start Application) .> (Show Logos) : includes

     (Configure Game Settings) ..> (Select Players) : includes
     (Configure Game Settings) ..> (Select AI Difficulty) : includes
     (Configure Game Settings) ..> (Select Game Mode) : includes

     (Play Game) ..> (Handle Game Events) : includes
     (Play Game) ..> (Render Game State) : includes
     (Play Game) ..> (Execute Game Actions) : includes
     (Play Game) ..> (Check Time Limit) : includes
     (Play Game) ..> (Check Game Over) : includes

     (Exit Application) .> (Shutdown Safely) : includes
   }
   @enduml

Domain Model
~~~~~~~~~~~

.. uml::
   :caption: Main Module Core Classes

   @startuml
   skinparam classAttributeIconSize 0
   
   package "Core Game Components" {
     class Game {
       + players: List<Player>
       + board: Board
       + game_mode: String
       + time_limit: int
       + state: GameState
       + initialize()
       + run()
       + check_time_limit()
       + check_game_over()
     }

     class Board {
       + spaces: List<Space>
       + properties: List<Property>
       + initialize()
       + get_space(position: int)
       + draw()
       + update_positions()
     }

     class Player {
       + name: String
       + position: int
       + money: int
       + properties: List<Property>
       + is_ai: boolean
       + move(steps: int)
       + pay(amount: int)
       + receive(amount: int)
     }

     class Property {
       + name: String
       + price: int
       + owner: Player
       + is_mortgaged: boolean
       + calculate_rent()
       + mortgage()
       + unmortgage()
     }

     Game "1" *-- "2..*" Player : contains
     Game "1" *-- "1" Board : has
     Board "1" *-- "*" Property : contains
     Player "1" o-- "*" Property : owns
   }
   @enduml

State Diagram
~~~~~~~~~~~~

.. uml::
   :caption: Main Application States

   @startuml
   skinparam state {
     BackgroundColor White
     BorderColor Black
     ArrowColor Black
   }

   [*] --> Initializing : Start Application
   
   state Initializing {
     state "Loading resources" as Loading
     state "Setting up environment" as Setup
     Loading --> Setup
   }

   Initializing --> ShowingLogos : Resources Loaded
   
   state ShowingLogos {
     state "Displaying company logos" as CompanyLogo
     state "Displaying game logo" as GameLogo
     CompanyLogo --> GameLogo
   }

   ShowingLogos --> MainMenu : Logos Complete
   
   state MainMenu {
     state "Display menu options" as MenuOptions
     state "Handle menu navigation" as MenuNav
     MenuOptions --> MenuNav : User Input
   }

   MainMenu --> MainMenu : Navigate Menus
   MainMenu --> ConfiguringGame : Start New Game
   MainMenu --> [*] : Exit Selected

   state ConfiguringGame {
     state "Select players" as Players
     state "Set AI difficulty" as AI
     state "Choose game mode" as Mode
     Players --> AI
     AI --> Mode
   }
   
   ConfiguringGame --> ConfiguringGame : Next Setting
   ConfiguringGame --> MainMenu : Cancel
   ConfiguringGame --> Gameplay : Settings Complete

   state Gameplay {
     state "Process game loop" as Loop
     state "Handle player turns" as Turns
     state "Update game state" as Update
     Loop --> Turns
     Turns --> Update
     Update --> Loop
   }
   
   Gameplay --> Gameplay : Game Loop
   Gameplay --> Paused : Pause Game
   Gameplay --> EndGameScreen : Game Over
   Gameplay --> [*] : Exit Game

   state Paused {
     state "Game state frozen" as Frozen
     state "Display pause menu" as PauseMenu
   }
   
   Paused --> Gameplay : Resume Game

   state EndGameScreen {
     state "Show final scores" as Scores
     state "Display winner" as Winner
     Scores --> Winner
   }
   
   EndGameScreen --> MainMenu : Play Again
   EndGameScreen --> [*] : Quit Game

   @enduml

Detailed Design
---------------

Class Interaction Diagram (Main Orchestration)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. uml::
   :caption: Main Orchestration

   @startuml
   skinparam classAttributeIconSize 0
   
   class Main {
      + main()
      + create_game()
      + run_game()
      + handle_end_game()
      + apply_screen_settings()
      + show_logo_screen()
      + show_company_logo()
      + safe_exit()
   }

   class Game {
      + players: List
      + board: Board
      + logic: GameLogic
      + state: GameState
      + check_time_limit()
      + check_game_over()
   }

   class Player {
      + name: String
      + money: int
      + position: int
      + is_ai: boolean
   }

   class GameRenderer {
      + draw()
   }

   class GameEventHandler {
      + handle_click()
      + handle_key()
      + handle_motion()
   }

   class GameActions {
      + play_turn()
      + handle_ai_turn()
      + end_game()
   }

   abstract class BasePage {
      + {abstract} draw()
      + {abstract} handle_click()
      + {abstract} handle_key()
   }

   class MainMenuPage extends BasePage {
   }

   class StartPage extends BasePage {
   }

   class GameModePage extends BasePage {
   }

   class SettingsPage extends BasePage {
   }

   class HowToPlayPage extends BasePage {
   }

   class EndGamePage extends BasePage {
   }

   class Sound_Manager {
      + play_sound()
      + play_music()
   }

   class Font_Manager {
      + get_font()
   }

   Main --> Game : creates
   Main --> Player : creates
   Main --> GameRenderer : creates
   Main --> GameEventHandler : creates
   Main --> GameActions : creates
   Main --> MainMenuPage : creates
   Main --> StartPage : creates
   Main --> GameModePage : creates
   Main --> SettingsPage : creates
   Main --> HowToPlayPage : creates
   Main --> EndGamePage : creates
   Main --> Sound_Manager : uses
   Main --> Font_Manager : uses

   Game o-- Player : contains
   GameRenderer --> Game : reads
   GameEventHandler --> Game : reads
   GameActions --> Game : modifies
   GameActions --> Player : modifies
   @enduml

Logging Setup Class Diagram
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Illustrates the custom `LogRedirector` used to pipe stdout/stderr to the logging framework.

.. uml::
   :caption: Logging Setup

   @startuml
   skinparam classAttributeIconSize 0
   
   class LogRedirector {
       + logger: Logger
       + level: int
       + buffer: str
       - _writing: boolean
       + write(buf: str)
       + flush()
   }

   class "logging.Logger" as Logger {
       + log(level: int, msg: str)
       + addHandler(handler: Handler)
   }

   class "logging.FileHandler" as FileHandler
   class "logging.StreamHandler" as StreamHandler
   
   class "sys" as SysModule {
       + stdout: TextIO
       + stderr: TextIO
       + __stdout__: TextIO
       + __stderr__: TextIO
   }

   LogRedirector o-- Logger : uses
   MainPy ..> Logger : configures
   MainPy ..> FileHandler : creates >
   MainPy ..> StreamHandler : creates >
   MainPy ..> LogRedirector : creates >
   MainPy ..> SysModule : redirects stdout/stderr
   LogRedirector ..> Logger : calls log()
   LogRedirector ..> SysModule : writes to __stdout__
   @enduml

Sequence Diagram: Game Initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This diagram shows the sequence of calls from starting the application (`main()`) through creating the game instance.

.. uml::
   :caption: Game Initialization

   @startuml
   skinparam sequenceMessageAlign center
   
   actor User
   participant "Main()" as MainFunc
   participant "ApplySettings" as ApplySettings
   participant "Pygame" as Pygame
   participant "FontManager" as FM
   participant "SoundManager" as SM
   participant "ShowLogo" as ShowLogo
   participant "MenuUI" as MenuUI
   participant "StartUI" as StartUI
   participant "AIUI" as AIUI
   participant "ModeUI" as ModeUI
   participant "CreateGame" as CreateGame
   participant "Player" as PlayerClass
   participant "Game" as GameClass
   participant "RunGame" as RunGame

   User -> MainFunc : Start Application
   activate MainFunc
   
   MainFunc -> ApplySettings : apply_screen_settings()
   activate ApplySettings
   ApplySettings -> Pygame : display.set_mode()
   ApplySettings -> FM : update_scale_factor()
   ApplySettings --> MainFunc : screen
   deactivate ApplySettings
   
   MainFunc -> SM : load_sounds()
   MainFunc -> SM : load_music()
   MainFunc -> ShowLogo : show_company_logo()
   activate ShowLogo
   ShowLogo -> SM : play_sound()
   ShowLogo -> Pygame : display.flip()
   ShowLogo --> MainFunc
   deactivate ShowLogo
   
   MainFunc -> MenuUI : create()
   activate MenuUI
   MainFunc -> MenuUI : draw()
   User -> MenuUI : Interact
   MenuUI -> MainFunc : result
   deactivate MenuUI
   
   MainFunc -> StartUI : create()
   activate StartUI
   MainFunc -> StartUI : draw()
   User -> StartUI : Enter Info
   StartUI -> MainFunc : player_info
   deactivate StartUI
   
   MainFunc -> AIUI : create()
   activate AIUI
   MainFunc -> AIUI : draw()
   User -> AIUI : Select Difficulty
   AIUI -> MainFunc : ai_difficulty
   deactivate AIUI
   
   MainFunc -> ModeUI : create()
   activate ModeUI
   MainFunc -> ModeUI : draw()
   User -> ModeUI : Select Mode
   ModeUI -> MainFunc : game_settings
   deactivate ModeUI
   
   MainFunc -> CreateGame : create_game()
   activate CreateGame
   CreateGame -> PlayerClass : create()
   CreateGame -> GameClass : create()
   CreateGame -> SM : play_sound()
   CreateGame --> MainFunc : game
   deactivate CreateGame
   
   MainFunc -> RunGame : run_game()
   deactivate MainFunc
   @enduml

Sequence Diagram: Game Configuration Flow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Details the user interactions within the `main()` loop to configure and start a new game.

.. uml::
   :caption: Game Configuration Flow

   @startuml
   skinparam sequenceMessageAlign center
   
   actor User
   participant "Main()" as MainFunc
   participant "UI Pages" as UI

   activate MainFunc
   MainFunc -> MainMenuPage : create()
   
   loop Until Game Starts
       activate UI
       MainFunc -> UI : draw()
       User -> UI : Interact
       UI -> MainFunc : result
       deactivate UI
       
       alt result == "start"
           MainFunc -> StartPage : create()
       else result == "how_to_play"
           MainFunc -> HowToPlayPage : create()
       else result == "settings"
           MainFunc -> SettingsPage : create()
       else result == "back"
           MainFunc -> MainMenuPage : create()
       else result == "player_info"
           MainFunc -> AIDifficultyPage : create()
       else result == "ai_difficulty"
           MainFunc -> GameModePage : create()
       else result == "game_settings"
           MainFunc -> MainFunc : create_game()
           MainFunc -> MainFunc : run_game()
           break Game Started
       else result == "quit"
           MainFunc -> MainFunc : safe_exit()
           break Exit Application
       end
   end
   deactivate MainFunc
   @enduml

Sequence Diagram: Main Game Loop (Simplified)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This diagram shows a simplified overview of the main `run_game` loop, highlighting event handling, rendering, and AI turn processing.

.. uml::
   :caption: Main Game Loop

   @startuml
   skinparam sequenceMessageAlign center
   
   participant "RunGame" as RunGame
   participant "Pygame" as Pygame
   participant "Game" as GameObj
   participant "Renderer" as Renderer
   participant "EventHandler" as EvHandler
   participant "GameActions" as Actions
   participant "Logger" as Log
   participant "SoundManager" as SM
   participant "Asyncio" as Asyncio

   activate RunGame
   RunGame -> Renderer : create()
   RunGame -> EvHandler : create()
   RunGame -> SM : play_music()

   loop while running
     RunGame -> Asyncio : await asyncio.sleep(0)
     RunGame -> Pygame : time.get_ticks()
     RunGame -> Log : flush()
     
     RunGame -> GameObj : check_time_limit()
     
     RunGame -> Renderer : draw()
     activate Renderer
     Renderer -> Pygame : display.flip()
     deactivate Renderer

     RunGame -> Pygame : event.get()
     
     alt event == QUIT
       RunGame -> RunGame : safe_exit()
       break
     else event == MOUSEBUTTONDOWN
       RunGame -> EvHandler : handle_click()
       activate EvHandler
       RunGame -> SM : play_sound()
       deactivate EvHandler
     else event == KEYDOWN
       RunGame -> EvHandler : handle_key()
     end
     
     RunGame -> Actions : handle_ai_turn()
     activate Actions
     Actions -> GameObj : update state
     deactivate Actions
     
     RunGame -> Actions : check_one_player_remains()
     
     RunGame -> Pygame : clock.tick()
   end
   
   RunGame -> SM : stop_music()
   deactivate RunGame
   @enduml

Sequence Diagram: Safe Shutdown
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Illustrates the steps performed when the application exits via `safe_exit()`.

.. uml::
   :caption: Safe Shutdown

   @startuml
   skinparam sequenceMessageAlign center
   
   participant "Caller" as Caller
   participant "safe_exit()" as SafeExit
   participant "Logger" as Log
   participant "FileHandler" as FH
   participant "sys" as Sys
   participant "logging" as LoggingModule
   participant "pygame" as Pygame

   activate Caller
   Caller -> SafeExit : safe_exit(code)
   activate SafeExit
   
   SafeExit -> Log : info("Game is shutting down...")
   activate Log
   
   SafeExit -> Sys : stdout = sys.__stdout__
   SafeExit -> Sys : stderr = sys.__stderr__
   
   loop for handler in logger.handlers
       alt handler is FileHandler
           SafeExit -> FH : flush()
           activate FH
           deactivate FH
       end
   end
   
   SafeExit -> Log : info("=== Game Session Ended ===")
   deactivate Log
   
   SafeExit -> LoggingModule : shutdown()
   SafeExit -> Pygame : quit()
   SafeExit -> Sys : exit(code)
   
   deactivate SafeExit
   deactivate Caller
   @enduml