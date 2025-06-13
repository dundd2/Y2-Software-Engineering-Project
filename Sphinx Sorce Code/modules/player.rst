Player Module
=============

This module defines the `Player` class, representing a participant in the game. It stores player-specific data like name, money, position, owned properties, and status (e.g., in jail, bankrupt). It also handles player movement animation, visual representation, and interactions related to property ownership and finances. For AI players, it holds a reference to an AI controller.

The Player module provides:

*   Representation of a player's state (money, properties, position, jail status, etc.).
*   Methods for financial transactions (`pay`, `receive`, `can_afford`).
*   Methods for property management (`buy_property`, `add_property`, `remove_property`, asset calculation).
*   Methods for handling jail status (`add_jail_card`, `use_jail_card`, `handle_jail_turn`).
*   Logic for player movement on the board, including animation (`move`, `start_move`, `update_animation`, `generate_move_path`).
*   Visual drawing logic (`draw_player`, `load_player_image`, `create_fallback_token`).
*   Handling of game-ending states like bankruptcy and voluntary exit (`handle_bankruptcy`, `handle_voluntary_exit`).
*   Integration with AI controllers for AI players.

.. automodule:: src.Player
   :members:
   :undoc-members:
   :show-inheritance:
   
Detailed Design
---------------

Player Class Diagram
~~~~~~~~~~~~~~~~~~

.. uml::
   :caption: Player Class Diagram

   @startuml
   skinparam class {
     BackgroundColor white
     BorderColor black
     ArrowColor black
   }

   class Player {
       + name : str
       + player_number : int
       + is_ai : bool
       + ai_difficulty : str
       + position : int
       + money : int
       + properties : List
       + in_jail : bool
       + jail_turns : int
       + jail_cards : List
       + bankrupt : bool
       + voluntary_exit : bool
       + is_moving : bool
       + player_image : Surface
       - ai_controller : AIPlayer
       
       + __init__(name: str, player_number: int, is_ai: bool, ai_difficulty: str): void
       + load_player_image(): Surface
       + create_fallback_token(): Surface
       + update_animation(): void
       + draw_player(screen: Surface, x: int, y: int): void
       + move(steps: int): void
       + pay(amount: int): bool
       + receive(amount: int): void
       + buy_property(property: Property): bool
       + add_jail_card(card_type: str): void
       + use_jail_card(): str
       + handle_jail_turn(): str
       + add_property(property: Property): void
       + remove_property(property: Property): void
       + get_total_assets(): int
       + handle_bankruptcy(creditor: Player): void
       + handle_voluntary_exit(): void
   }

   class Property {
       + name : str
       + price : int
       + owner : Player
       + mortgaged : bool
       + houses : int
       + has_hotel : bool
       
       + get_mortgage_value(): int
       + get_unmortgage_cost(): int
   }

   class AIPlayer {
       + decide_action(): str
   }
    
   class EasyAIPlayer {
   }
    
   class HardAIPlayer {
   }

   class Font_Manager {
       + get_font(size: int): Font
   }

   Player *-- Property : owns
   Player ..> Font_Manager : uses
   Player ..> Property : interacts with
   Player o-- AIPlayer : controls
    
   EasyAIPlayer --|> AIPlayer
   HardAIPlayer --|> AIPlayer
   @enduml

Player State Diagram
~~~~~~~~~~~~~~~~~~

.. uml::
   :caption: Player State Diagram

   @startuml
   skinparam state {
     BackgroundColor white
     BorderColor black
     ArrowColor black
   }

   [*] --> Active
    
   state Active {
       [*] --> Idle
       Idle --> Moving : move() called
       Moving --> Idle : Animation Complete
       Idle --> InJail : Sent to Jail
       Idle --> Deciding : AI Turn
       Deciding --> Idle : Action Taken
       Idle --> Bankrupt : Cannot Pay
       Idle --> Exited : Chooses to Exit
       Idle --> Winner : Game Ends
   }

   Active --> InJail : Sent to Jail
   InJail --> Active : Pays/Uses Card/Rolls Doubles
   InJail --> Bankrupt : Cannot Pay Fine

   Active --> Bankrupt : handle_bankruptcy()
   Bankrupt --> [*]

   Active --> Exited : handle_voluntary_exit()
   Exited --> [*]

   Active --> Winner : Declared Winner
   Winner --> [*]
   @enduml

Player Initialization
~~~~~~~~~~~~~~~~~~~

.. uml::
   :caption: Sequence Diagram: Player Initialization

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "Caller" as Caller <<e.g., create_game>>
   participant "Player.__init__" as Init
   participant "pygame" as Pygame
   participant "os" as OS
   participant "AIController" as AIC <<Easy/HardAIPlayer>>

   Caller -> Init : Player(name, num, is_ai, difficulty)
   activate Init
   Init -> Init : Set basic attributes (name, num, money, pos, etc.)
   Init -> Pygame : Rect(0, 0, 40, 40)
   Pygame --> Init : rect instance
   Init -> Init : Set color based on is_ai
   alt is_ai
       Init -> Init : Import AI classes
       alt ai_difficulty == "hard"
           Init -> AIC : HardAIPlayer()
           AIC --> Init : ai_controller instance
       else
           Init -> AIC : EasyAIPlayer()
           AIC --> Init : ai_controller instance
       end
   end
   Init -> Init : load_player_image()
   activate Init #darkred
       Init -> OS : path.join(...) ' Construct image path
       OS --> Init : image_path
       Init -> OS : path.exists(image_path)
       OS --> Init : exists
       alt exists
           Init -> Pygame : image.load(image_path)
           Pygame --> Init : image_surface
           Init -> Pygame : transform.scale(image_surface, (40,40))
           Pygame --> Init : scaled_image
           Init -> Init : self.player_image = scaled_image
       else Not Found
           Init -> Init : create_fallback_token()
            activate Init #darkblue
               Init -> Pygame : Surface((40,40), SRCALPHA)
               Pygame --> Init : surface
               Init -> Pygame : draw.circle(...)
               Init -> Font_Manager : get_font(28)
               Font_Manager --> Init : font
               Init -> font : render(...)
               font --> Init : text_surface
               Init -> surface : blit(...)
               Init -> Init : self.player_image = surface
            deactivate Init
       end
   deactivate Init
   Init --> Caller : Player instance
   deactivate Init
   @enduml

Player Movement
~~~~~~~~~~~~~

.. uml::
   :caption: Sequence Diagram: Player Movement

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "GameLogic" as Logic
   participant "Player" as P
   participant "update_animation()" as UpdateAnim <<method>>
   participant "pygame" as Pygame

   Logic -> P : move(steps)
   activate P
   P -> P : generate_move_path(steps)
   P -> P : is_moving = True
   P -> P : move_progress = 0.0
   P -> Pygame : time.get_ticks()
   Pygame --> P : current_time
   P -> P : animation_time = current_time
   deactivate P

   loop Animation Loop (e.g., in run_game)
       Logic -> P : update_animation()
       activate P
       P -> Pygame : time.get_ticks()
       Pygame --> P : current_time
       P -> P : Update move_progress based on speed
       alt move_progress > 1.0
           P -> P : position = move_path(current_path_index)
           P -> P : current_path_index += 1
           alt current_path_index >= len(move_path)
               P -> P : is_moving = False
               P -> P : position = move_target_position
           end
       end
       P --> Logic
       deactivate P
   end
   @enduml

Property Purchase
~~~~~~~~~~~~~~

.. uml::
   :caption: Sequence Diagram: Buying a Property

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "GameLogic" as Logic
   participant "Player" as P
   participant "Property" as Prop

   Logic -> P : buy_property(Prop)
   activate P
   P -> Prop : Get price
   Prop --> P : price
   alt money >= price
       P -> P : money -= price
       P -> P : properties.append(Prop)
       P -> Prop : owner = self
       Prop --> P
       P --> Logic : True (Success)
   else money < price
       P --> Logic : False (Failure)
   end
   deactivate P
   @enduml

Jail Turn Handling
~~~~~~~~~~~~~~~~

.. uml::
   :caption: Sequence Diagram: Jail Turn Handling

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "GameLogic" as Logic
   participant "Player" as P
   participant "random" as Random

   Logic -> P : handle_jail_turn()
   activate P
   opt not self.in_jail
       P --> Logic : False (Not in jail)
       deactivate P
       return
   end

   alt is_ai
       opt jail_cards exist
           P -> Random : random()
           Random --> P : value (0.0 to 1.0)
           alt value < 0.7
               P -> P : use_jail_card()
               activate P #DarkCyan
                   P -> P : card_type = jail_cards.pop()
                   P -> P : in_jail = False
                   P -> P : jail_turns = 0
                   P --> P : card_type
               deactivate P
               P --> Logic : card_type (Used card)
               deactivate P
               return
           end
       end
       opt money >= 50
            P -> Random : random()
            Random --> P : value (0.0 to 1.0)
            alt value < 0.5
               P -> P : pay(50)
               activate P #DarkOrange
                   P -> P : money -= 50
                   P --> P : True
               deactivate P
               P -> P : in_jail = False
               P -> P : jail_turns = 0
               P --> Logic : None (Paid fine)
               deactivate P
               return
            end
       end
   end

   P -> P : jail_turns += 1
   alt jail_turns >= 3
       opt money >= 50
           P -> P : pay(50)
            activate P #DarkOrange
               P -> P : money -= 50
               P --> P : True
            deactivate P
       end
       P -> P : in_jail = False
       P -> P : jail_turns = 0
   end

   P --> Logic : None (Stayed in jail or paid on 3rd turn)
   deactivate P
   @enduml

Asset Calculation
~~~~~~~~~~~~~~~

.. uml::
   :caption: Sequence Diagram: Total Asset Calculation

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "Caller" as Caller
   participant "Player" as P
   participant "Property" as Prop

   Caller -> P : get_total_assets()
   activate P
   P -> P : total = self.money
   loop for prop in self.properties
       P -> Prop : Get mortgaged status
       Prop --> P : is_mortgaged
       alt not is_mortgaged
           P -> Prop : Get price
           Prop --> P : price
           P -> P : total += price
       else is_mortgaged
           P -> Prop : Get price
           Prop --> P : price
           P -> P : total += price / 2
       end

       P -> Prop : Get houses count
       Prop --> P : num_houses
       alt num_houses > 0
           P -> Prop : get_house_sale_value()
           Prop --> P : house_value
           P -> P : total += house_value * num_houses
       end

       P -> Prop : Get hotel status
       Prop --> P : has_hotel
       alt has_hotel
           P -> Prop : get_hotel_sale_value()
           Prop --> P : hotel_value
           P -> P : total += hotel_value
       end
   end loop
   P --> Caller : total
   deactivate P
   @enduml

Player Drawing
~~~~~~~~~~~~

.. uml::
   :caption: Sequence Diagram: Player Drawing

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "GameRenderer" as Renderer
   participant "Player" as P
   participant "pygame" as Pygame
   participant "Font_Manager" as FM
   participant "Screen" as ScreenSurface

   Renderer -> P : draw_player(ScreenSurface, x, y)
   activate P
   P -> Pygame : time.get_ticks()
   Pygame --> P : current_time
   P -> P : Calculate animation_offset (e.g., based on time)
   P -> P : rect.x = x
   P -> P : rect.y = y - animation_offset

   alt voluntary_exit
       P -> FM : get_font(12)
       FM --> P : font
       P -> font : render("EXITED", ...)
       font --> P : text_surface
       P -> ScreenSurface : blit(text_surface, ...)
       P -> Pygame : Surface(...) ' Create glow surface
       Pygame --> P : glow_surface
       P -> Pygame : draw.circle(...) ' Draw glow effect
       P -> ScreenSurface : blit(glow_surface, ...)
       P -> P : Get player_image
       alt player_image exists
           P -> player_image : copy()
           player_image --> P : image_copy
           P -> image_copy : set_alpha(128)
           P -> ScreenSurface : blit(image_copy, rect)
       else No player_image
           P -> P : create_fallback_token()
            activate P #DarkGreen
            ' ... fallback creation ...
            deactivate P
           P -> player_image : copy()
           player_image --> P : image_copy
           P -> image_copy : set_alpha(128)
           P -> ScreenSurface : blit(image_copy, rect)
       end
   else bankrupt
       P -> FM : get_font(12)
       FM --> P : font
       P -> font : render("BANKRUPT", ...)
       font --> P : text_surface
       P -> ScreenSurface : blit(text_surface, ...)
       P -> P : Get player_image
       alt player_image exists
           P -> player_image : copy()
           player_image --> P : image_copy
           P -> image_copy : set_alpha(128)
           P -> ScreenSurface : blit(image_copy, rect)
       else No player_image
           P -> P : create_fallback_token()
            activate P #DarkGreen
            ' ... fallback creation ...
            deactivate P
           P -> player_image : copy()
           player_image --> P : image_copy
           P -> image_copy : set_alpha(128)
           P -> ScreenSurface : blit(image_copy, rect)
       end
   else Active Player
       P -> P : Get player_image
       alt player_image exists
           P -> ScreenSurface : blit(player_image, rect)
       else No player_image
           P -> P : create_fallback_token()
            activate P #DarkGreen
            ' ... fallback creation ...
            deactivate P
           P -> ScreenSurface : blit(player_image, rect)
       end
   end
   P --> Renderer
   deactivate P
   @enduml

Bankruptcy Handling
~~~~~~~~~~~~~~~~

.. uml::
   :caption: Sequence Diagram: Handling Bankruptcy

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "GameLogic" as Logic
   participant "BankruptPlayer" as BP <<Player>>
   participant "Creditor" as CP <<Player>>
   participant "Property" as Prop

   Logic -> BP : handle_bankruptcy(Creditor)
   activate BP
   BP -> BP : bankrupt = True

   loop for each prop in properties(:)
       alt Creditor exists
           BP -> BP : remove_property(prop)
           BP -> CP : add_property(prop)
           activate CP
           CP -> Prop : Get mortgage status
           Prop --> CP : is_mortgaged
           alt is_mortgaged
               CP -> Prop : get_unmortgage_cost()
               Prop --> CP : cost
               CP -> Prop : get_mortgage_value()
               Prop --> CP : value
               CP -> CP : unmortgage_fee = cost - value
               alt can_afford(unmortgage_fee)
                   CP -> CP : pay(unmortgage_fee)
                   CP -> Prop : unmortgage()
                   Prop --> CP
               end
           end
           CP --> BP
           deactivate CP
       else No Creditor (Bank)
           BP -> BP : remove_property(prop)
           BP -> Prop : owner = None
           BP -> Prop : mortgaged = False
           BP -> Prop : houses = 0
           BP -> Prop : has_hotel = False
           Prop --> BP
       end
   end loop

   alt Creditor exists and BP.money > 0
       BP -> CP : receive(BP.money)
       activate CP
       CP --> BP
       deactivate CP
   end
   BP -> BP : money = 0
   BP --> Logic
   deactivate BP
   @enduml

AI Player Turn
~~~~~~~~~~~~

.. uml::
   :caption: Sequence Diagram: AI Player Turn (Conceptual)

   @startuml
   participant "GameLogic" as Logic
   participant "AIPlayer" as AIP <<Player>>
   participant "AIController" as AIC <<AIPlayer>>

   Logic -> AIP : It's your turn (trigger AI logic)
   activate AIP
   alt is_ai == True
       AIP -> AIC : decide_action(game_state) ' Example call
       activate AIC
       ' ... AI Controller performs calculations ...
       AIC --> AIP : chosen_action (e.g., "roll", "buy", "build")
       deactivate AIC
       AIP -> Logic : Perform chosen_action
       Logic --> AIP
   end
   deactivate AIP
   @enduml