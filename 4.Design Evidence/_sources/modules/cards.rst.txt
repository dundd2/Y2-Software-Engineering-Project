Cards Module
============

This module defines the structure and behavior of the Pot Luck and Opportunity Knocks cards used in the game. It includes classes for individual cards and the decks that manage them, including drawing, discarding, and reshuffling.

.. automodule:: src.Cards
   :members:
   :undoc-members:
   :show-inheritance:

High-Level Design
-----------------

Use Case Diagram
~~~~~~~~~~~~~~~~

Shows the basic interaction with the card system from a game perspective.

.. uml::
   :caption: Card System Use Cases

   @startuml
   skinparam usecase {
     BackgroundColor white
     BorderColor black
     ArrowColor black
   }
   skinparam actor {
     BackgroundColor white
     BorderColor black
   }
   skinparam note {
     BackgroundColor white
     BorderColor black
   }

   left to right direction
   actor Player
   
   rectangle "Card System" {
     usecase "Draw Card" as Draw
     usecase "Apply Card Action" as Apply
     usecase "Return Card to Deck" as Return
   }
   
   Player -- Draw
   Draw ..> Apply : includes
   Apply ..> Return : includes
   
   note right of Draw
     Game logic requests a card
     from the appropriate deck.
   end note
   @enduml

Detailed Design
---------------

Class Diagram
~~~~~~~~~~~~~~

Shows the classes involved in the card system and their relationships.

.. uml::
   :caption: Cards Class Structure

   @startuml
   skinparam class {
     BackgroundColor white
     BorderColor black
     ArrowColor black
   }
   skinparam note {
     BackgroundColor white
     BorderColor black
   }

   enum CardType {
     POT_LUCK
     OPPORTUNITY_KNOCKS
   }

   class Card {
     + text: str
     + action: any
     + card_type: CardType
     + requires_input: bool <<get>>
     + is_special: bool <<get>>
     + __init__(text, action, card_type)
   }

   note right of Card: action field contains function or identifier

   class CardDeck {
     - card_type: CardType
     - cards: List<Card>
     - discard_pile: List<Card>
     - last_drawn_card: Card
     + __init__(card_type: CardType)
     + initialize_deck()
     + draw_card(): Card
     + return_card(card: Card, to_bottom: bool = True)
     + return_jail_card(card_type: CardType)
     + peek_top_card(): Card
     + get_remaining_count(): int
     + get_discard_count(): int
   }

   CardDeck o-- "*" Card : contains
   CardDeck ..> CardType : uses
   Card -- CardType : uses
   CardDeck ..> random : uses
   CardDeck ..> Game_Logic::pot_luck_cards : uses
   CardDeck ..> Game_Logic::opportunity_knocks_cards : uses

   note right of CardDeck::initialize_deck
     Reads card data from external
     lists (pot_luck_cards or
     opportunity_knocks_cards)
     and creates Card objects.
   end note
   @enduml

State Diagram (CardDeck)
~~~~~~~~~~~~~~~~~~~~~~~~

Illustrates the different states a `CardDeck` can be in regarding its draw and discard piles.

.. uml::
   :caption: CardDeck State Diagram

   @startuml
   skinparam state {
     BackgroundColor white
     BorderColor black
     ArrowColor black
   }

   [*] --> Ready : initialize_deck()

   state Deck {
     state Ready : Draw pile has cards
     state DrawEmpty : Draw pile empty
     state NoCardsLeft : Both piles empty (Error state or needs re-init)

     Ready --> Ready : draw_card() [cards > 1]
     Ready --> DrawEmpty : draw_card() [cards == 1]
     Ready --> Ready : return_card()

     DrawEmpty --> Ready : draw_card() [discard > 0] / Reshuffle discard into draw
     DrawEmpty --> DrawEmpty : return_card()
     DrawEmpty --> NoCardsLeft : draw_card() [discard == 0] / Cannot draw

     NoCardsLeft --> DrawEmpty : return_card() / Card added to discard
   }
   @enduml

Sequence Diagrams
~~~~~~~~~~~~~~~~~

**Deck Initialization**

Shows the process of creating and shuffling a new deck.

.. uml::
   :caption: Sequence Diagram: Deck Initialization

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "deck:CardDeck" as Deck
   participant "Card" as CardClass <<static>>
   participant "random" as Random <<static>>
   participant "card_data" as Data <<external>>

   activate Deck
   Deck -> Deck : initialize_deck()
   activate Deck
   alt deck.card_type == POT_LUCK
     Deck -> Data : pot_luck_cards
   else deck.card_type == OPPORTUNITY_KNOCKS
     Deck -> Data : opportunity_knocks_cards
   end
   Data --> Deck : card_info_list

   loop for card_info in card_info_list
     Deck -> CardClass : create Card(text, action, type)
     CardClass --> Deck : new_card
     Deck -> Deck : self.cards.append(new_card)
   end

   Deck -> Random : shuffle(self.cards)
   Deck --> Deck : shuffled cards
   deactivate Deck
   deactivate Deck
   @enduml

**Drawing a Card**

Illustrates the logic when a card is drawn, including handling an empty draw pile.

.. uml::
   :caption: Sequence Diagram: Card Drawing Sequence

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "caller:GameLogic" as Caller
   participant "deck:CardDeck" as Deck
   participant "random" as Random <<static>>

   Caller -> Deck : draw_card()
   activate Deck
   alt len(self.cards) == 0
     alt len(self.discard_pile) > 0
       Deck -> Deck : self.cards = self.discard_pile
       Deck -> Deck : self.discard_pile = ()
       Deck -> Random : shuffle(self.cards)
       note right: Discard pile becomes the new draw pile
     else len(self.discard_pile) == 0
       Deck --> Caller : return None
       deactivate Deck
       return No card available
     end
   end
   Deck -> Deck : card = self.cards.pop()
   Deck -> Deck : self.last_drawn_card = card
   Deck --> Caller : return card
   deactivate Deck
   @enduml

**Returning a "Get Out of Jail Free" Card**

Shows the special handling for returning this specific type of card.

.. uml::
   :caption: Sequence Diagram: Returning Jail Free Card

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "GameLogic" as Caller
   participant "CardDeck" as Deck
   participant "Card" as CardClass
   participant "CardData" as Data

   Caller -> Deck : return_jail_card(card_type)
   activate Deck

   Deck -> Deck : Search for jail card
   note right of Deck : Search in draw and discard piles

   alt jail card found
       note right of Deck : Use existing card instance
   else jail card not found
       Deck -> Data : Get jail card data
       Data --> Deck : text, action
       Deck -> CardClass : create(text, action, card_type)
       CardClass --> Deck : jail_card
       note right of Deck : Create new instance
   end

   Deck -> Deck : return_card(jail_card, to_bottom=True)
   activate Deck
   Deck -> Deck : discard_pile.append(jail_card)
   deactivate Deck

   Deck --> Caller : void
   deactivate Deck
   @enduml

Key Classes Overview
--------------------

*   **CardType**: An `Enum` defining the two types of decks: `POT_LUCK` and `OPPORTUNITY_KNOCKS`.
*   **Card**: Represents a single card with its display `text`, associated `action` (which likely corresponds to a function or identifier in the game logic), and `card_type`. It also determines if the card `requires_input` or is `is_special` based on keywords in its text.
*   **CardDeck**: Manages a collection of `Card` objects for a specific `card_type`. It handles initialization (reading from external data and shuffling), drawing cards (including reshuffling the discard pile when the draw pile is empty), returning used cards to the discard pile, and specifically handling the return of "Get Out of Jail Free" cards.