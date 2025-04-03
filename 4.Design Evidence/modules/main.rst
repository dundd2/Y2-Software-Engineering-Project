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

This diagram illustrates the main interactions a user (or the system itself) has with the application, primarily managed or initiated by the Main module.

.. uml::

   left to right direction
   actor User

   rectangle "Property Tycoon Application (Main Module)" {
     User -- (Start Application)
     User -- (Navigate Menus)
     (Navigate Menus) ..> (Configure Game Settings) : include
     (Navigate Menus) ..> (View How To Play) : include
     (Navigate Menus) ..> (Start New Game) : include
     (Start New Game) --> (Play Game)
     (Play Game) --> (View End Game Screen)
     User -- (Exit Application)

     (Start Application) .> (Initialize Environment) : include
     note right of (Initialize Environment) : Pygame, Sound, Logging, Fonts
     (Start Application) .> (Show Logos) : include

     (Configure Game Settings) ..> (Select Players) : include
     (Configure Game Settings) ..> (Select AI Difficulty) : include
     (Configure Game Settings) ..> (Select Game Mode) : include

     (Play Game) ..> (Handle Game Events) : include
     (Play Game) ..> (Render Game State) : include
     (Play Game) ..> (Execute Game Actions) : include
     (Play Game) ..> (Check Time Limit) : include
     (Play Game) ..> (Check Game Over) : include

     (Exit Application) .> (Shutdown Safely) : include
   }

 Domain Model (Core Entities Managed/Created by Main)

This diagram shows the primary classes instantiated or orchestrated directly by the functions within `Main.py`.

.. uml::

   package "UI Pages" {
     class BasePage
     class MainMenuPage
     class StartPage
     class GameModePage
     class SettingsPage
     class HowToPlayPage
     class AIDifficultyPage
     class EndGamePage
     class CreditsPage
     class KeyboardShortcutsPage
     MainMenuPage -up-|> BasePage
     StartPage -up-|> BasePage
     GameModePage -up-|> BasePage
     SettingsPage -up-|> BasePage
     HowToPlayPage -up-|> BasePage
     AIDifficultyPage -up-|> BasePage
     EndGamePage -up-|> BasePage
     CreditsPage -up-|> BasePage
     KeyboardShortcutsPage -up-|> BasePage
     note right of BasePage : Managed by main() loop
   }

   package "Game Core" {
     class Game {
       +players : List<Player>
       +game_mode : String
       +time_limit : int
       +renderer : GameRenderer
       +state : String
       +logic : GameLogic
       +board : Board
       +check_time_limit()
       +check_game_over()
     }
     class Player {
       +name : String
       +money : int
       +is_ai : bool
       +position : int
       +ai_controller : AIPlayerLogic
     }
     class GameLogic {
        +players : List<dict>
        +properties : dict
        +play_turn()
        +handle_buy_decision()
        +auction_property()
     }
     class Board {
        +draw()
        +update_board_positions()
     }
     class AIPlayerLogic <<interface>>
     class EasyAIPlayer
     class HardAIPlayer
     EasyAIPlayer -up-|> AIPlayerLogic
     HardAIPlayer -up-|> AIPlayerLogic

     note right of Game : Created by create_game()
     note right of Player : Created by create_game()
     note right of GameLogic : Instantiated within Game
     note right of Board : Instantiated within Game
   }

   package "Game Services" {
      class GameRenderer {
        +draw()
      }
      class GameEventHandler {
         +handle_click()
         +handle_key()
         +handle_motion()
      }
      class GameActions {
         +play_turn()
         +handle_buy_decision()
         +start_auction()
         +handle_ai_turn()
         +end_full_game()
         +end_abridged_game()
         +check_one_player_remains()
      }
      class Sound_Manager {
         +play_sound()
         +play_music()
         +stop_music()
      }
      class Font_Manager {
         +get_font()
         +update_scale_factor()
      }
      note bottom of GameRenderer : Instantiated in run_game()
      note bottom of GameEventHandler : Instantiated in run_game()
      note bottom of GameActions : Instantiated in run_game()
   }

   package "System" {
      class PygameDisplay
      class PygameEvent
      class Logger
      class AsyncioLoop
   }

   ' Relationships driven by Main.py functions
   (main) ..> MainMenuPage : creates/uses
   (main) ..> StartPage : creates/uses
   (main) ..> GameModePage : creates/uses
   (main) ..> SettingsPage : creates/uses
   (main) ..> HowToPlayPage : creates/uses
   (main) ..> AIDifficultyPage : creates/uses
   (main) ..> KeyboardShortcutsPage : creates/uses
   (main) ..> (create_game) : calls
   (main) ..> (run_game) : calls
   (main) ..> (handle_end_game) : calls
   (main) ..> Sound_Manager : uses
   (main) ..> Font_Manager : uses
   (main) ..> (apply_screen_settings) : calls
   (main) ..> AsyncioLoop : runs on

   (create_game) ..> Game : creates
   (create_game) ..> Player : creates
   (create_game) ..> Sound_Manager : uses

   (run_game) ..> Game : uses
   (run_game) ..> GameRenderer : creates/uses
   (run_game) ..> GameEventHandler : creates/uses
   (run_game) ..> GameActions : creates/uses
   (run_game) ..> Sound_Manager : uses
   (run_game) ..> Logger : uses
   (run_game) ..> PygameEvent : handles
   (run_game) ..> PygameDisplay : updates

   (handle_end_game) ..> EndGamePage : creates/uses
   (handle_end_game) ..> CreditsPage : creates/uses
   (handle_end_game) ..> Sound_Manager : uses

   (apply_screen_settings) ..> PygameDisplay : configures
   (apply_screen_settings) ..> Font_Manager : uses

   Game "1" *-- "2..*" Player
   Game o-- GameRenderer
   Game *-- GameLogic
   Game *-- Board
   Player o-- AIPlayerLogic

   (run_game) ..> Game : updates state >
   (run_game) ..> GameRenderer : calls draw() >
   (run_game) ..> GameEventHandler : calls handle_*() >
   (run_game) ..> GameActions : calls handle_ai_turn(), etc. >

 Application State Diagram

This diagram shows the high-level states the application transitions through, managed primarily by the `main()` function loop.

.. uml::

    (*) --> Initializing : Application Start
    Initializing --> ShowingLogos : Initialization Complete
    ShowingLogos --> MainMenu : Logos Shown

    MainMenu --> MainMenu : Navigate Submenus (Settings, HowToPlay)
    MainMenu --> ConfiguringGame : Start New Game
    MainMenu --> (*) : Exit Application

    ConfiguringGame --> ConfiguringGame : Next Step (Players -> AI -> Mode)
    ConfiguringGame --> MainMenu : Back
    ConfiguringGame --> Gameplay : Configuration Complete

    Gameplay --> Gameplay : Game Loop Iteration (Events, Render, AI, Time Check)
    Gameplay --> Paused : Pause Game (Abridged Mode)
    Paused --> Gameplay : Resume Game
    Gameplay --> EndGameScreen : Game Over (Win/Time Limit/1 Player Left)
    Gameplay --> (*) : Exit Application (e.g., via ESC in some contexts or error)

    EndGameScreen --> MainMenu : Play Again
    EndGameScreen --> EndGameScreen : View Credits
    EndGameScreen --> (*) : Quit

Detailed Design
---------------

 Class Interaction Diagram (Main Orchestration)

This diagram shows the key classes and how the functions within `Main.py` orchestrate their creation and interaction. It focuses on the flow controlled by `main()`, `create_game()`, `run_game()`, and `handle_end_game()`.

.. uml::

   class MainPy <<module>> {
     +apply_screen_settings(resolution)
     +create_game(player_info, game_settings) : Game
     +run_game(game, game_settings) : dict
     +handle_end_game(game_over_data) : bool
     +show_logo_screen(screen, logo_path)
     +show_company_logo(screen)
     +main()
     +safe_exit()
   }

   MainPy ..> Game : creates via create_game()
   MainPy ..> Player : creates via create_game()
   MainPy ..> GameRenderer : creates via run_game()
   MainPy ..> GameEventHandler : creates via run_game()
   MainPy ..> GameActions : creates via run_game()
   MainPy ..> MainMenuPage : creates via main()
   MainPy ..> StartPage : creates via main()
   MainPy ..> GameModePage : creates via main()
   MainPy ..> SettingsPage : creates via main()
   MainPy ..> HowToPlayPage : creates via main()
   MainPy ..> AIDifficultyPage : creates via main()
   MainPy ..> EndGamePage : creates via handle_end_game()
   MainPy ..> CreditsPage : creates via handle_end_game()
   MainPy ..> KeyboardShortcutsPage : creates via main()
   MainPy ..> Sound_Manager : uses
   MainPy ..> Font_Manager : uses
   MainPy ..> Logger : uses
   MainPy ..> PygameDisplay : uses via apply_screen_settings()
   MainPy ..> PygameEvent : uses via run_game()

   GameRenderer ..> Game : reads state
   GameEventHandler ..> Game : reads state
   GameEventHandler ..> GameActions : calls actions
   GameActions ..> Game : modifies state
   GameActions ..> Player : modifies state

   MainMenuPage <|-- UI.BasePage
   StartPage <|-- UI.BasePage
   GameModePage <|-- UI.BasePage
   SettingsPage <|-- UI.BasePage
   HowToPlayPage <|-- UI.BasePage
   AIDifficultyPage <|-- UI.BasePage
   EndGamePage <|-- UI.BasePage
   CreditsPage <|-- UI.BasePage
   KeyboardShortcutsPage <|-- UI.BasePage

   UI.BasePage : +draw()
   UI.BasePage : +handle_click()
   UI.BasePage : +handle_key()
   UI.BasePage : +handle_motion()

 Logging Setup Class Diagram

Illustrates the custom `LogRedirector` used to pipe stdout/stderr to the logging framework.

.. uml::

    class LogRedirector {
        +logger : Logger
        +level : int
        +buffer : str
        +_writing : bool
        +write(buf)
        +flush()
    }

    class "logging.Logger" as Logger {
        +log(level, msg)
        +addHandler(handler)
    }
    class "logging.FileHandler" as FileHandler
    class "logging.StreamHandler" as StreamHandler
    class "sys" as SysModule {
        +stdout
        +stderr
        +__stdout__
        +__stderr__
    }

    LogRedirector o-- Logger
    MainPy ..> Logger : configures
    MainPy ..> FileHandler : creates/adds
    MainPy ..> StreamHandler : creates/adds
    MainPy ..> LogRedirector : creates
    MainPy ..> SysModule : redirects stdout/stderr = LogRedirector instance
    LogRedirector ..> Logger : calls log()
    LogRedirector ..> SysModule : writes to __stdout__ (optional)

 Sequence Diagram: Game Initialization

This diagram shows the sequence of calls from starting the application (`main()`) through creating the game instance.

.. uml::

   actor User
   participant "main()" as MainFunc <<async>>
   participant "apply_screen_settings()" as ApplySettings <<async>>
   participant "pygame" as Pygame
   participant "Font_Manager" as FM
   participant "Sound_Manager" as SM
   participant "show_company_logo()" as ShowLogo <<async>>
   participant "MainMenuPage" as MenuUI
   participant "StartPage" as StartUI
   participant "AIDifficultyPage" as AIUI
   participant "GameModePage" as ModeUI
   participant "create_game()" as CreateGame
   participant "Player" as PlayerClass
   participant "Game" as GameClass
   participant "run_game()" as RunGame <<async>>

   User -> MainFunc : Start Application
   MainFunc -> ApplySettings : apply_screen_settings(WINDOW_SIZE)
   ApplySettings -> Pygame : display.set_mode()
   ApplySettings -> FM : update_scale_factor()
   ApplySettings --> MainFunc : screen
   MainFunc -> SM : load_sounds()
   MainFunc -> SM : load_music()
   MainFunc -> ShowLogo : show_company_logo(screen)
   ShowLogo -> SM : play_sound(...)
   ShowLogo -> Pygame : display.flip()
   ShowLogo --> MainFunc
   loop Menu Navigation (See Configuration Flow Diagram)
     MainFunc -> MenuUI : create()
     MainFunc -> MenuUI : draw()
     User -> MenuUI : Interact (e.g., Click Start)
     MenuUI -> MainFunc : result ("start")
     MainFunc -> StartUI : create()
     MainFunc -> StartUI : draw()
     User -> StartUI : Enter Player Info, Click Next
     StartUI -> MainFunc : result (player_info)
     alt AI Players Selected
        MainFunc -> AIUI : create()
        MainFunc -> AIUI : draw()
        User -> AIUI : Select Difficulty, Click Next
        AIUI -> MainFunc : result (ai_difficulty)
     end
     MainFunc -> ModeUI : create()
     MainFunc -> ModeUI : draw()
     User -> ModeUI : Select Mode, Click Start
     ModeUI -> MainFunc : result (game_settings)
   end
   MainFunc -> CreateGame : create_game(player_info, game_settings)
   CreateGame -> PlayerClass : create()
   CreateGame -> PlayerClass : create()
   ...
   CreateGame -> GameClass : create(players, settings)
   CreateGame -> SM : play_sound("game_start")
   CreateGame --> MainFunc : game
   MainFunc -> RunGame : run_game(game, game_settings)
   Note right of RunGame : Enters main game loop...

 Sequence Diagram: Game Configuration Flow

Details the user interactions within the `main()` loop to configure and start a new game.

.. uml::

    actor User
    participant "main()" as MainFunc <<async>>
    participant "CurrentPage" as UI <<UI.BasePage>>

    MainFunc -> MainMenuPage : current_page = create()
    loop Until Game Starts or Exits
        MainFunc -> UI : draw()
        User -> UI : Interact (Click/Key)
        UI -> MainFunc : result = handle_click/handle_key()
        alt result is "start" (from MainMenu)
            MainFunc -> StartPage : current_page = create()
        else result is "how_to_play" (from MainMenu)
            MainFunc -> HowToPlayPage : current_page = create()
        else result is "settings" (from MainMenu)
            MainFunc -> SettingsPage : current_page = create()
        else result is "back" (from StartPage, etc.)
            MainFunc -> MainMenuPage : current_page = create() ' Or previous page
        else result is player_info (from StartPage)
            MainFunc -> StartPage : player_info = get_player_info()
            opt AI players > 0
                MainFunc -> AIDifficultyPage : current_page = create()
            else
                MainFunc -> GameModePage : current_page = create()
            end
        else result is ai_difficulty (from AIDifficultyPage)
            MainFunc -> AIDifficultyPage : ai_difficulty = result
            MainFunc -> GameModePage : current_page = create()
        else result is game_settings (from GameModePage)
            MainFunc -> GameModePage : game_settings = get_game_settings()
            opt ai_difficulty is set
                 MainFunc -> game_settings : add ai_difficulty
            end
            MainFunc -> create_game() : Call with player_info, game_settings
            create_game() --> MainFunc : game instance
            MainFunc -> run_game() : Call with game, game_settings
            break loop
        else result is "quit" or similar
            MainFunc -> safe_exit()
            break loop
        else other navigation (e.g., Keyboard Shortcuts)
             MainFunc -> SpecificPage : current_page = create()
        end
    end

 Sequence Diagram: Main Game Loop (Simplified)

This diagram shows a simplified overview of the main `run_game` loop, highlighting event handling, rendering, and AI turn processing.

.. uml::

   participant "run_game()" as RunGame <<async>>
   participant "pygame" as Pygame
   participant "Game" as GameObj
   participant "GameRenderer" as Renderer
   participant "GameEventHandler" as EvHandler
   participant "GameActions" as Actions
   participant "Logger" as Log
   participant "Sound_Manager" as SM
   participant "asyncio" as Asyncio

   activate RunGame
   RunGame -> Renderer : create(game, actions)
   RunGame -> EvHandler : create(game, actions)
   RunGame -> SM : play_music()

   loop while running
     RunGame -> Asyncio : await asyncio.sleep(0)
     RunGame -> Pygame : time.get_ticks()
     RunGame -> Log : flush() periodically
     opt Abridged Mode Time Check
       RunGame -> GameObj : check_time_limit()
       alt Time Limit Reached
         RunGame -> Actions : end_abridged_game()
         RunGame --> MainFunc : game_over_data
         break
       end
     end

     opt AI Turn Timeout Check
        RunGame -> Log : warning("AI timeout")
        RunGame -> GameObj : Advance turn (simplified)
        RunGame -> Actions : check_and_trigger_ai_turn()
     end

     RunGame -> Renderer : draw()
     RunGame -> Pygame : display.flip()

     RunGame -> Pygame : event.get()
     alt Event Found
       alt event == QUIT
         RunGame -> MainFunc : safe_exit()
       alt event == MOUSEBUTTONDOWN
         RunGame -> EvHandler : handle_click(pos)
         EvHandler --> RunGame : game_over_data
         RunGame -> SM : play_sound("menu_click")
         opt game_over_data is not None
            RunGame --> MainFunc : game_over_data
            break
         end
       alt event == KEYDOWN
         RunGame -> EvHandler : handle_key(event)
         EvHandler --> RunGame : game_over_data
         opt game_over_data is not None
            RunGame --> MainFunc : game_over_data
            break
         end
       alt event == VIDEORESIZE
         RunGame -> MainFunc : apply_screen_settings() via await
       else other events...
         RunGame -> EvHandler : handle_motion(pos)
       end
     end

     opt AI's Turn (State == ROLL and not moving)
       RunGame -> Actions : handle_ai_turn(current_player)
       Actions --> RunGame : game_over_data
       opt game_over_data is not None
         RunGame --> MainFunc : game_over_data
         break
       end
     end

     opt Auction AI Logic (State == AUCTION)
        RunGame -> GameObj : Access auction data (game.logic.current_auction)
        RunGame -> GameObj : Process AI bid/pass (game.logic.process_auction_bid/pass)
        RunGame -> GameObj : Check auction end (game.logic.check_auction_end)
     end

     opt Check Game End Condition (e.g., one player left)
       RunGame -> Actions : check_one_player_remains()
       alt Only One Player Left
         RunGame -> Actions : end_full_game() or end_abridged_game()
         Actions --> RunGame : game_over_data
         RunGame --> MainFunc : game_over_data
         break
       end
     end

     RunGame -> Pygame : clock.tick(FPS)

   end loop
   RunGame -> SM : stop_music()
   deactivate RunGame

 Sequence Diagram: Safe Shutdown

Illustrates the steps performed when the application exits via `safe_exit()`.

.. uml::

    participant "Caller" as Caller <<e.g., run_game, main>>
    participant "safe_exit()" as SafeExit
    participant "Logger" as Log
    participant "FileHandler" as FH <<logging.FileHandler>>
    participant "sys" as Sys
    participant "logging" as LoggingModule
    participant "pygame" as Pygame

    Caller -> SafeExit : safe_exit(code)
    activate SafeExit
    SafeExit -> Log : info("Game is shutting down...")
    SafeExit -> Sys : Restore stdout = sys.__stdout__
    SafeExit -> Sys : Restore stderr = sys.__stderr__
    loop for handler in logger.handlers
        alt handler is FileHandler
            SafeExit -> FH : flush()
        end
    end
    SafeExit -> Log : info("=== Game Session Ended ===")
    SafeExit -> LoggingModule : shutdown()
    SafeExit -> Pygame : quit()
    SafeExit -> Sys : exit(code)
    deactivate SafeExit