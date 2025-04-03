AI Player Logic Module
======================

This module defines the logic and strategies for Artificial Intelligence (AI) players within the Property Tycoon game. It provides different AI personalities or difficulty levels, encapsulating the decision-making processes for various game situations like buying properties, bidding in auctions, managing assets, and handling jail time.

The AI Player Logic module provides:

*   **EasyAIPlayer:** A baseline AI implementing straightforward decision rules based on predefined strategy parameters (e.g., bid multipliers, development thresholds).
*   **HardAIPlayer:** A more complex AI that builds upon the Easy AI logic but introduces a 'mood' or 'emotion' system. This mood modifier influences decisions, potentially making the AI more aggressive or conservative depending on recent game events (though the mood update mechanism itself is external to this class in the provided code).
*   Methods for evaluating property value from the AI's perspective.
*   Logic for deciding whether to buy properties, bid in auctions, develop properties, mortgage/unmortgage assets, and handle jail situations.
*   Helper functions for analyzing property groups and ownership.

.. automodule:: src.Ai_Player_Logic
   :members:
   :undoc-members:
   :show-inheritance:

High-Level Design
-----------------

 Use Case Diagram (AI Decision Making)

Illustrates the primary decision points where the Game Logic interacts with the AI Player Logic module.

.. uml::

    @startuml
    actor "Game Logic" as GameLogic

    rectangle "AI Player Logic Module" {
      GameLogic -- (Request Purchase Decision)
      GameLogic -- (Request Auction Bid)
      GameLogic -- (Request Jail Action)
      GameLogic -- (Request Development Decision)
      GameLogic -- (Request Mortgage Decision)
      GameLogic -- (Request Trade Evaluation)

      (Request Purchase Decision) ..> (Evaluate Property Value) : include
      (Request Purchase Decision) ..> (Check Affordability) : include
      (Request Purchase Decision) ..> (Apply Strategy/Mood) : include

      (Request Auction Bid) ..> (Evaluate Property Value) : include
      (Request Auction Bid) ..> (Check Affordability) : include
      (Request Auction Bid) ..> (Apply Strategy/Mood) : include

      (Request Jail Action) ..> (Check Resources) : include
      (Request Jail Action) ..> (Apply Strategy/Mood) : include

      (Request Development Decision) ..> (Check Affordability) : include
      (Request Development Decision) ..> (Check Group Ownership) : include
      (Request Development Decision) ..> (Apply Strategy/Mood) : include

      (Request Mortgage Decision) ..> (Evaluate Financial Need) : include
      (Request Mortgage Decision) ..> (Prioritize Properties) : include
      (Request Mortgage Decision) ..> (Apply Strategy/Mood) : include

      (Request Trade Evaluation) ..> (Evaluate Property Value) : include
      (Request Trade Evaluation) ..> (Apply Strategy/Mood) : include
    }

    note right of "AI Player Logic Module"
      Decisions for HardAIPlayer
      are influenced by an internal
      'mood' state.
    end note
    @enduml

 Domain Model (AI Logic Concepts)

Shows the core concepts involved in the AI's decision-making process.

.. uml::

    @startuml
    class AIPlayerLogic {
       Responsibility: Encapsulates decision algorithms
       + difficulty : String
    }

    class EasyAIPlayerLogic extends AIPlayerLogic {
       + strategy : Map<String, Float>
       note right: Predefined parameters
       + decide_purchase()
       + decide_bid()
       + decide_jail()
       + decide_development()
       + decide_mortgage()
    }

    class HardAIPlayerLogic extends AIPlayerLogic {
       - easy_ai : EasyAIPlayerLogic
       note right: Uses base logic
       + mood_modifier : Float
       + update_mood()
       + decide_purchase()
       note right: Overrides/Wraps EasyAI
       + decide_bid()
       note right: Overrides/Wraps EasyAI 
       + decide_jail()
       note right: Overrides/Wraps EasyAI
       + decide_development()
       note right: Overrides/Wraps EasyAI
    }

    class PropertyData {
       + name : String
       + price : int
       + group : String
       + owner : String
       + houses : int
       + is_mortgaged : bool
       + is_station : bool
       + is_utility : bool
    }

    class PlayerData {
       + name : String
       + money : int
       + properties : List<PropertyData>
       + in_jail : bool
       + jail_free_cards : int
    }

    AIPlayerLogic ..> PropertyData : evaluates
    AIPlayerLogic ..> PlayerData : considers state
    HardAIPlayerLogic o-- EasyAIPlayerLogic : delegates to / modifies
    @enduml


Detailed Design
---------------

 AI Player Class Diagram

Details the structure of `EasyAIPlayer` and `HardAIPlayer`, their methods, and relationship.

.. uml::

    @startuml
    interface AIPlayer {
       + get_property_value(property_data, ai_player, board_properties) : float
       + get_auction_bid(current_minimum, property_data, ai_player, board_properties) : int or None
       + handle_jail_strategy(ai_player, jail_free_cards) : str or None
       + handle_property_development(ai_player, board_properties) : Property or None
       + should_buy_property(property_data, player_money, owned_properties) : bool
       + should_mortgage_property(property_data, player_money) : bool
       note right: Simplified representation
       + consider_trade_offer(...) : bool
       note right: Other decision methods...
    }

    class EasyAIPlayer implements AIPlayer {
       + difficulty : str = "easy"
       + strategy : dict
       + __init__(difficulty="easy")
       + get_group_properties(color_group, board_properties) : list
       + check_group_ownership(color_group, board_properties, player_name) : bool
       + can_build_house(property, color_group_properties) : bool
       + get_property_value(property_data, ai_player, board_properties) : float
       + handle_turn(ai_player, current_location, board_properties, is_first_round) : dict
       note right: More complex than interface suggests
       + should_use_get_out_of_jail_card() : bool
       + should_pay_jail_fine(ai_player) : bool
       + should_mortgage_property(ai_player, required_money) : list
       note right: Returns list of props to mortgage
       + handle_ai_turn(ai_player, board_properties) : bool
       note right: Simplified decision logic?
       + get_location_type(position, board_properties) : str
       + get_property_name(position, board_properties) : str or None
       + get_auction_bid(current_minimum, property_data, ai_player, board_properties) : int or None
       + handle_jail_strategy(ai_player, jail_free_cards) : str or None
       + handle_property_development(ai_player, board_properties) : dict or None
       note right: Returns property dict
       + handle_emergency_cash(ai_player, required_amount, board_properties) : list
       + consider_trade_offer(...) : bool
       + should_buy_property(property_data, player_money, owned_properties) : bool
       + make_auction_bid(property_data, current_bid, player_money, owned_properties) : int or None
       note right: Seems redundant with get_auction_bid?
       + should_develop_property(property_data, player_money, owned_properties) : bool
       + should_mortgage_property(property_data, player_money) : bool
       note right: Different signature than above
       + should_unmortgage_property(property_data, player_money) : bool
       + should_sell_houses(property_data, player_money, target_amount) : bool
       + get_development_priority(properties) : list
    }

    class HardAIPlayer implements AIPlayer {
       + difficulty : str = "hard"
       + mood_modifier : float = 0.0
       - easy_ai : EasyAIPlayer
       + __init__()
       + update_mood(is_happy: bool)
       + get_adjusted_probability(base_probability: float) : float
       + get_property_value(property_data, ai_player, board_properties) : float ' Wraps EasyAI
       + get_auction_bid(current_minimum, property_data, ai_player, board_properties) : int or None ' Wraps EasyAI
       + handle_jail_strategy(ai_player, jail_free_cards) : str or None ' Wraps EasyAI
       + should_mortgage_property(ai_player, required_money) : list ' Delegates to EasyAI
       + handle_property_development(ai_player, board_properties) : dict or None ' Wraps EasyAI
       + should_buy_property(property_data, player_money, owned_properties) : bool ' Wraps EasyAI
    }

    note right of EasyAIPlayer::strategy
      Contains parameters like:
      - max_bid_multiplier
      - development_threshold
      - jail_stay_threshold
      - mortgage_threshold
    end note

    note bottom of HardAIPlayer
      HardAIPlayer uses an instance of EasyAIPlayer
      to get baseline decisions, then modifies them
      based on the `mood_modifier`.
    end note

    HardAIPlayer o-- EasyAIPlayer : uses

    note "Dependencies (simplified - actual code uses dicts/lists)" as N1
    AIPlayer ..> Property : uses data
    AIPlayer ..> Player : uses data
    @enduml


 Activity Diagram: Hard AI Auction Bid Decision

Illustrates the flow for `HardAIPlayer.get_auction_bid`, showing the interaction with `EasyAIPlayer` and the mood influence.

.. uml::

    @startuml
    participant "GameLogic/Actions" as Caller
    participant "HardAIPlayer" as HardAI
    participant "EasyAIPlayer" as EasyAI
    participant "PropertyData" as PropData
    participant "PlayerData" as PlayerData

    Caller -> HardAI : get_auction_bid(min_bid, PropData, PlayerData, board_props)
    activate HardAI
    HardAI -> EasyAI : get_auction_bid(min_bid, PropData, PlayerData, board_props)
    activate EasyAI
    EasyAI -> EasyAI : get_property_value(...)
    activate EasyAI
    EasyAI --> EasyAI : perceived_value
    deactivate EasyAI
    note right: Easy AI bid calculation
    EasyAI --> HardAI : base_bid (int or None)
    deactivate EasyAI
    
    alt base_bid is None
        HardAI -> HardAI : get_adjusted_probability(0.0)
        HardAI --> HardAI : angry_bid_chance
        
        alt random() < angry_bid_chance
            HardAI -> HardAI : get_property_value(...)
            note right: Recalculate for Hard AI mood
            HardAI --> HardAI : perceived_value_hard
            HardAI -> HardAI : Calculate emotion_bid
            HardAI --> HardAI : emotion_bid
            HardAI --> Caller : emotion_bid
        else
            HardAI --> Caller : None (Pass)
        end
    else
        HardAI -> HardAI : Calculate mood_multiplier
        HardAI --> HardAI : mood_multiplier
        HardAI -> HardAI : final_bid = base_bid * mood_multiplier
        HardAI -> HardAI : Calculate max_percentage based on mood
        HardAI --> HardAI : max_percentage
        HardAI -> HardAI : Cap final_bid by PlayerData.money * max_percentage
        HardAI --> HardAI : capped_final_bid
        HardAI --> Caller : capped_final_bid
    end
    
    deactivate HardAI
    @enduml

Sequence Diagram: Hard AI Purchase Decision (`should_buy_property`)

Shows `HardAIPlayer` deciding whether to buy, potentially overriding the `EasyAIPlayer` logic based on mood.

.. uml::

    @startuml
    participant "GameLogic/Actions" as Caller
    participant "HardAIPlayer" as HardAI
    participant "EasyAIPlayer" as EasyAI
    participant "PropertyData" as PropData
    participant "PlayerData" as PlayerData

    Caller -> HardAI : should_buy_property(PropData, PlayerData.money, PlayerData.properties)
    activate HardAI
    HardAI -> EasyAI : should_buy_property(PropData, PlayerData.money, PlayerData.properties)
    activate EasyAI
    EasyAI -> EasyAI : get_property_value(PropData, PlayerData.properties, PlayerData.money)
    activate EasyAI
    ' ... value calculation ...
    EasyAI --> EasyAI : property_value
    deactivate EasyAI
    ' ... compare value and price ...
    EasyAI --> HardAI : base_decision (bool)
    deactivate EasyAI
    alt not base_decision and PlayerData.money >= PropData.price
        HardAI -> HardAI : get_adjusted_probability(0.2)
        HardAI --> HardAI : buy_chance
        HardAI -> HardAI : Calculate max_price_ratio based on mood
        HardAI --> HardAI : max_price_ratio
        HardAI -> HardAI : can_afford = (PlayerData.money * max_price_ratio >= PropData.price)
        HardAI --> HardAI : can_afford_result
        opt can_afford_result and random() < buy_chance
            HardAI --> Caller : True (Emotion Triggered Buy)
            deactivate HardAI
            stop
        end opt
    else base_decision and mood_modifier < 0
        HardAI -> HardAI : Calculate pass_chance (-mood_modifier * 1.5)
        HardAI --> HardAI : pass_chance
        opt random() < pass_chance
            HardAI --> Caller : False (Emotion Triggered Pass)
            deactivate HardAI
            stop
        end opt
    end
    HardAI --> Caller : base_decision
    note right: Return original decision if no override
    deactivate HardAI
    @enduml

Sequence Diagram: Updating AI Mood (`update_mood`)

Shows the simple process of adjusting the `mood_modifier`.

.. uml::

    @startuml
    participant "External Caller (e.g., GameLogic)" as Caller
    participant "HardAIPlayer" as HardAI

    Caller -> HardAI : update_mood(is_happy=True)
    activate HardAI
    alt is_happy is True
        HardAI -> HardAI : mood_modifier = max(-0.3, mood_modifier - 0.05)
    else is_happy is False
        HardAI -> HardAI : mood_modifier = min(0.3, mood_modifier + 0.05)
    end
    HardAI --> Caller : return
    deactivate HardAI
    @enduml
