Game Renderer Module
====================

The Game Renderer module is the primary engine for visualizing the Property Tycoon game during active play. It acts as an interface between the game's internal state (managed by `Game`, `GameLogic`, `Board`, `Player`, etc.) and the visual output presented to the user via the Pygame display surface. Its core responsibility is to accurately and efficiently draw all necessary game elements frame by frame, including static components like the board, dynamic elements like player tokens and dice, and context-sensitive UI panels for actions like buying, auctioning, or managing properties.

High-Level Design
-----------------

Use Case Diagram (What it Renders)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This diagram outlines the key visual components and information that the `GameRenderer` is tasked with displaying during a typical game session. The "Game Loop" represents the main process invoking the renderer.

.. uml::
   :caption: Game Renderer Responsibilities

   @startuml
   actor "Game Loop" as GameLoop
   rectangle "Game Rendering" {
     GameLoop -- (Render Game Board)
     GameLoop -- (Render Player Info Panel)
     GameLoop -- (Render Player Tokens/Animations)
     GameLoop -- (Render Dice)
     GameLoop -- (Render Property Cards/Tooltips)
     GameLoop -- (Render Action Buttons) : e.g., Roll, Buy, Pass, Bid
     GameLoop -- (Render Notifications/Popups)
     GameLoop -- (Render Auction UI)
     GameLoop -- (Render Jail Options UI)
     GameLoop -- (Render Development UI)
     GameLoop -- (Render Time Remaining/Warnings)
     GameLoop -- (Render Free Parking Pot)
     GameLoop -- (Render AI Emotion UI)
     (Render Game Board) ..> (Render Property Stars) : include
     (Render Player Info Panel) ..> (Render Player Money) : include
     (Render Player Info Panel) ..> (Render Owned Properties) : include
     (Render Player Info Panel) ..> (Render Player Status) : e.g., Jail, Bankrupt
   }
   @enduml

Dependency Diagram
~~~~~~~~~~~~~~~~~~

This diagram illustrates the main modules and libraries that the `GameRenderer` relies upon to function. It highlights its central role in accessing game state and utilizing utility modules for presentation.

.. uml::
   :caption: Game Renderer Dependencies

   @startuml
   skinparam package {
     BackgroundColor white
     BorderColor black
     ArrowColor black
   }

   package "Game Renderer Module" {
     [GameRenderer]
   }

   package "Game Core" {
     [Game]
     [GameActions]
     [GameLogic]
     [Board]
     [Player]
     [DevelopmentManager]
   }

   package "UI Module" {
     [AIEmotionUI]
   }

   package "Utility Modules" {
     [Font_Manager]
   }

   package "External Libraries" {
     [pygame]
     [math]
     [os]
   }

   [GameRenderer] --> [Game]
   [GameRenderer] --> [GameActions]
   [GameRenderer] --> [GameLogic]
   [GameRenderer] --> [Board]
   [GameRenderer] --> [Player]
   [GameRenderer] --> [DevelopmentManager]
   [GameRenderer] --> [AIEmotionUI]
   [GameRenderer] --> [Font_Manager]
   [GameRenderer] --> [pygame]
   [GameRenderer] --> [math]
   @enduml

Simplified State-Based Rendering Logic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The main `draw()` method adapts its output based significantly on the current `game.state`. This state diagram shows the primary rendering paths determined by the game state.

.. uml::
    :caption: State Diagram: GameRenderer Draw Logic by Game State

    @startuml
    skinparam state {
      BackgroundColor white
      BorderColor black
      ArrowColor black
    }

    [*] --> Idle
    Idle --> DrawingBase : Frame Start
    DrawingBase --> DrawingPlayerInfo
    DrawingPlayerInfo --> DrawingCommonUI

    DrawingCommonUI --> CheckState
    
    CheckState --> DrawRollState : state == "ROLL"
    CheckState --> DrawBuyState : state == "BUY"
    CheckState --> DrawAuctionState : state == "AUCTION"
    CheckState --> DrawDevelopmentState : state == "DEVELOPMENT"
    CheckState --> DrawOtherState : else

    DrawRollState --> DrawingDice
    DrawBuyState --> DrawingDice
    DrawAuctionState --> DrawingDice
    DrawDevelopmentState --> DrawingDice
    DrawOtherState --> DrawingDice

    DrawingDice --> DrawingOverlays
    DrawingOverlays --> DrawingFinalFlip
    DrawingFinalFlip --> [*]

    state DrawingBase {
        [*] --> RenderBackground
        RenderBackground --> RenderBoard
        RenderBoard --> RenderPlayerAnimations
        RenderPlayerAnimations --> [*]
    }
    
    state DrawingPlayerInfo {
        [*] --> RenderPlayerStatusPanel
        RenderPlayerStatusPanel --> RenderPropertyTooltips
        RenderPropertyTooltips --> [*]
    }
    
    state DrawingCommonUI {
        [*] --> RenderTimeRemaining
        RenderTimeRemaining --> RenderFreeParkingPot
        RenderFreeParkingPot --> RenderAIEmotionUI
        RenderAIEmotionUI --> [*]
    }
    @enduml

Detailed Design
---------------

Class Diagram
~~~~~~~~~~~~~

This diagram details the structure of the `GameRenderer` class itself, showing its attributes (dependencies and fonts) and its public methods responsible for drawing specific elements.

.. uml::
   :caption: GameRenderer Class Diagram

   @startuml
   skinparam class {
     BackgroundColor white
     BorderColor black
     ArrowColor black
   }

   class GameRenderer {
     - game: Game
     - game_actions: GameActions
     - screen: pygame.Surface
     - font: pygame.font.Font
     - small_font: pygame.font.Font
     - tiny_font: pygame.font.Font
     - button_font: pygame.font.Font
     - message_font: pygame.font.Font
     + draw_button(button: pygame.Rect, text: str, hover: bool, active: bool): void
     + draw_time_remaining(): void
     + draw(): void
     + draw_dice(dice1: int, dice2: int, is_rolling: bool): void
     + draw_property_card(property_data: dict): void
     + draw_buy_options(mouse_pos: tuple): void
     + draw_property_tooltip(property_data: dict, mouse_pos: tuple): void
     + draw_notification(): void
     + draw_card_alert(card: dict, player: dict): void
     + wrap_text(text: str, max_width: int): list<str>
     + draw_popup_message(): void
     + draw_auction(auction_data: dict): void
     + draw_jail_options(player: dict): void
     + draw_free_parking_pot(): void
     + draw_development_ui(property_data: dict): void
     + handle_development_click(pos: tuple, property_data: dict): any
   }

   note right of GameRenderer::draw
     Main rendering loop called each frame.
     Delegates to other draw methods based on game state.
   end note

   GameRenderer ..> Game : uses >
   GameRenderer ..> GameActions : uses >
   GameRenderer ..> Font_Manager : uses >
   GameRenderer ..> "pygame.Surface" : uses >
   GameRenderer ..> "pygame.Rect" : uses >
   GameRenderer ..> "pygame.font.Font" : uses >
   GameRenderer ..> AIEmotionUI : uses >
   @enduml

Activity Diagram: Drawing Dice
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This diagram details the logic within the `draw_dice` method, including handling the rolling animation state and the special effect for doubles.

.. uml::
    :caption: Activity Diagram: draw_dice Method

    @startuml
    skinparam activity {
      BackgroundColor white
      BorderColor black
      ArrowColor black
    }

    start
    :Get window size;
    :Calculate dice size and position;
    :Draw Dice 1 Shadow;
    :Draw Dice 1 Background;
    if (Value 1 in dice_images?) then (yes)
      :Load and scale image 1;
      :Blit image 1;
    else (no)
      :Render text value 1;
      :Blit text value 1;
    endif
    :Draw Dice 1 Border (color based on is_rolling);

    :Draw Dice 2 Shadow;
    :Draw Dice 2 Background;
     if (Value 2 in dice_images?) then (yes)
      :Load and scale image 2;
      :Blit image 2;
    else (no)
      :Render text value 2;
      :Blit text value 2;
    endif
    :Draw Dice 2 Border (color based on is_rolling);

    if (is_rolling == false AND dice1 == dice2?) then (yes)
      :Get current time;
      :Calculate sparkle positions and colors based on time;
      :Draw multiple sparkle effects around dice;
    endif
    stop
    @enduml

Sequence Diagrams
~~~~~~~~~~~~~~~~~

**Main Draw Sequence**

Illustrates the high-level flow of execution when the main `GameRenderer.draw()` method is invoked by the game loop.

.. uml::
   :caption: Sequence Diagram: Main Draw Call

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "main_loop" as Loop
   participant "renderer:GameRenderer" as Renderer
   participant "game:Game" as Game
   participant "board:Board" as Board
   participant "dev_manager:DevelopmentManager" as DevMan
   participant "emotion_ui:AIEmotionUI" as EmotionUI
   participant "player:Player" as Player

   Loop -> Renderer : draw()
   activate Renderer
   Renderer -> Game : check_time_limit()
   Renderer -> Renderer : screen.fill() / draw gradient
   Renderer -> Board : draw(screen)
   Renderer -> Game : dev_manager.is_active
   opt dev_manager is active
     Renderer -> DevMan : draw(mouse_pos)
     opt complete_button exists and player not AI
       Renderer -> Renderer : draw_button(complete_button, ...)
     end
   end

   Renderer -> Game : emotion_uis.values()
   loop for each emotion_ui
     Renderer -> EmotionUI : draw()
   end

   Renderer -> Game : synchronize_player_positions()
   Renderer -> Game : synchronize_player_money()
   Renderer -> Game : synchronize_free_parking_pot()

   Renderer -> Game : players
   loop for each player
     Renderer -> Player : update_animation()
   end

   Renderer -> Board : draw(screen)
   Renderer -> DevMan : _draw_property_stars()

   Renderer -> Renderer : draw Player Info Panel
   Renderer -> Renderer : draw_time_remaining()
   Renderer -> Renderer : draw_free_parking_pot()
   Renderer -> Renderer : draw_notification()

   Renderer -> Game : state
   alt game.state == "ROLL"
     Renderer -> Renderer : draw_button(roll_button, ...)
     opt can_develop
        Renderer -> Renderer : draw_button(develop_button, ...)
     end
     opt abridged mode
        Renderer -> Renderer : draw_button(pause_button, ...)
     end
     opt human players remain
        Renderer -> Renderer : draw_button(quit_button, ...)
     end
     opt AI turn
        Renderer -> Game : check_and_trigger_ai_turn()
     end
   else game.state == "BUY"
     Renderer -> Renderer : draw_property_card(...)
     Renderer -> Renderer : draw_buy_options(...)
   else game.state == "AUCTION"
     Renderer -> Renderer : draw_auction(...)
     Renderer -> Game : logic.check_auction_end()
     opt auction ended
        Renderer -> Game : handle_auction_end()
     end
   else game.state == "DEVELOPMENT"
     Renderer -> Renderer : draw_development_ui(...)
   end

   opt game.dice_animation or recent roll
     Renderer -> Renderer : draw_dice(...)
   end

   opt game.show_card
     Renderer -> Renderer : draw_card_alert(...)
   end

   Renderer -> Board : camera.handle_camera_controls(...)
   Renderer -> Board : update_board_positions()

   Renderer -> Game : check_game_over()
   opt game over
     Renderer -> Game : handle_game_over(...)
   end

   opt game.show_popup
     Renderer -> Renderer : draw_popup_message()
   end

   Renderer -> pygame.display : flip()
   Renderer --> Loop
   deactivate Renderer
   @enduml

**Drawing Time Remaining with Warning**

Shows the specific logic executed within the `draw_time_remaining` method, particularly when the game timer is low, triggering visual warnings.

.. uml::
   :caption: Sequence Diagram: Drawing Time Warning

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "renderer:GameRenderer" as Renderer
   participant "game:Game" as Game
   participant "pygame.time" as Time
   participant "math" as Math

   Renderer -> Renderer : draw_time_remaining()
   activate Renderer
   Renderer -> Game : game_mode, time_limit
   opt game_mode == "abridged" and time_limit exists
     Renderer -> Time : get_ticks()
     Renderer -> Game : start_time, total_pause_time, game_paused, pause_start_time
     Renderer -> Renderer : calculate remaining time
     opt remaining <= 30
       Renderer -> Math : sin(...) # for flashing
       Renderer -> Renderer : calculate warning intensity, border width, color
       Renderer -> Renderer : draw warning border/overlay
     end
     opt time_limit_reached
       Renderer -> Renderer : draw "Finishing Lap" banner
     end
     opt remaining <= time_warning_start
        Renderer -> Math : sin(...) # for flashing
        Renderer -> Renderer : draw faint warning overlay
        opt remaining is 60, 30, or 10
            Renderer -> Game : add_message(...)
        end
     end
     Renderer -> Renderer : draw Time Panel (lap, time, progress bar)
   end
   Renderer --> Renderer : return
   deactivate Renderer
   @enduml

**Drawing Auction UI**

Details the steps for rendering the auction interface when the game is in the "AUCTION" state.

.. uml::
   :caption: Sequence Diagram: Drawing Auction UI

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "renderer:GameRenderer" as Renderer
   participant "game:Game" as Game

   Renderer -> Renderer : draw_auction(auction_data)
   activate Renderer
   Renderer -> Game : show_card
   opt card is showing
       Renderer --> Renderer : return (don't draw auction)
   end
   Renderer -> Renderer : Validate auction_data keys
   opt missing keys or invalid property
       Renderer -> Game : state = "ROLL"
       Renderer --> Renderer : return
   end

   Renderer -> Renderer : Draw overlay background
   Renderer -> Renderer : Draw auction panel base (with shadow)
   Renderer -> Renderer : Draw header (Current Bidder, Time Remaining)
   Renderer -> Renderer : Draw Title ("AUCTION", Property Name)
   Renderer -> Renderer : Draw Info (Current Bid, Minimum Bid)
   opt highest_bidder exists
       Renderer -> Renderer : Draw Highest Bidder info
   end

   Renderer -> Renderer : Get current bidder data
   opt bidder is human and can bid
       Renderer -> Renderer : Draw bid input field (auction_input)
       Renderer -> Renderer : Draw "Bid" button (using draw_button)
       Renderer -> Renderer : Draw "Pass" button (using draw_button)
   end

   opt passed_players exist
       Renderer -> Renderer : Draw list of passed players
   end

   Renderer --> Renderer : return
   deactivate Renderer
   @enduml

**Drawing Jail Options**

Shows the process for displaying the available actions to a player currently in jail.

.. uml::
   :caption: Sequence Diagram: Drawing Jail Options

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "renderer:GameRenderer" as Renderer
   participant "player:dict" as PlayerData

   Renderer -> Renderer : draw_jail_options(player_data)
   activate Renderer
   opt player_data("in_jail") == False
       Renderer --> Renderer : return
   end

   Renderer -> Renderer : Draw overlay background
   Renderer -> Renderer : Draw jail options panel base (with shadow)
   Renderer -> Renderer : Draw Title ("Jail Options")

   Renderer -> PlayerData : get("jail_card")
   opt has jail card
       Renderer -> Renderer : draw_button("Use Get Out of Jail Free Card", ...)
   end
   Renderer -> PlayerData : get("money")
   opt money >= 50
       Renderer -> Renderer : draw_button("Pay £50 Fine", ...)
   end
   Renderer -> Renderer : draw_button("Roll for Doubles", ...)

   Renderer -> PlayerData : get("jail_turns")
   Renderer -> Renderer : Draw Turns in Jail text

   Renderer --> Renderer : return
   deactivate Renderer
   @enduml

**Drawing Notification/Popup**

Illustrates how temporary messages (notifications or popups) are displayed over the main game view.

.. uml::
   :caption: Sequence Diagram: Drawing Notification/Popup

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "renderer:GameRenderer" as Renderer
   participant "game:Game" as Game
   participant "pygame.time" as Time

   alt Notification
       Renderer -> Game : notification, notification_time
       opt notification exists
           Renderer -> Time : get_ticks()
           opt time < notification_time + DURATION
               Renderer -> Renderer : Draw notification background (top center)
               Renderer -> Renderer : Draw notification text
           else
               Renderer -> Game : notification = None
           end
       end
   else Popup
       Renderer -> Game : show_popup, popup_title, popup_message
       opt show_popup == True
           Renderer -> Renderer : Draw overlay background
           Renderer -> Renderer : Draw popup panel background
           opt popup_title exists
               Renderer -> Renderer : Draw popup title
           end
           opt popup_message exists
               Renderer -> Renderer : wrap_text(popup_message, ...)
               loop for each line
                   Renderer -> Renderer : Draw message line
               end
           end
           Renderer -> Renderer : Draw "OK" button
       end
   end
   @enduml

Key Classes Overview
--------------------

*   **GameRenderer**: The central class orchestrating the drawing process. It holds references to the game state (`Game`, `GameActions`), the display surface (`screen`), and various fonts (`Font_Manager`). It contains numerous `draw_` methods, each responsible for rendering a specific visual component (e.g., `draw_dice`, `draw_player_info_panel` implicitly, `draw_auction`, `draw_property_card`). The main `draw()` method acts as the primary entry point, called each frame, which then delegates rendering tasks to the appropriate sub-methods based on the current `game.state` and other conditions.

API Documentation
-----------------

.. automodule:: src.GameRenderer
   :members:
   :undoc-members:
   :show-inheritance: