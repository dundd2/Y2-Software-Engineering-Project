Cards Module
===========

This module contains classes and functions related to the game cards, including the Card and CardDeck classes that manage the Pot Luck and Opportunity Knocks cards in the game.

Key Features
-----------

* **Card Types Management**: Handles two distinct card types - Pot Luck and Opportunity Knocks
* **Card Deck Initialization**: Automatically loads and shuffles card data for each deck
* **Card Drawing**: Provides mechanisms for drawing cards from decks
* **Discard Pile Management**: Tracks drawn cards and reshuffles when necessary
* **Special Card Handling**: Special handling for "Get Out of Jail Free" cards
* **Card Actions**: Each card contains text and an associated action function
* **Deck State Tracking**: Monitors the number of cards in each deck and discard pile

Card Types
---------

The game features two types of cards:

1. **Pot Luck Cards**: Similar to Chance cards in traditional Monopoly, these cards can provide benefits or penalties to players. They include actions like collecting money, paying fines, or moving to specific board locations.

2. **Opportunity Knocks Cards**: Similar to Community Chest cards in traditional Monopoly, these cards also provide various effects that can help or hinder players.

Card Structure
------------

Each card contains:

* **Text**: The message displayed to the player when the card is drawn
* **Action**: A function that implements the card's effect on the game state
* **Card Type**: Identifies whether the card is a Pot Luck or Opportunity Knocks card
* **Special Flags**: Indicators for cards that require special handling (e.g., jail free cards)

Card Effects
-----------

Cards can have various effects on gameplay:

* **Money Transfers**: Adding or removing money from a player
* **Movement**: Moving a player to a specific location on the board
* **Property Interactions**: Charging players based on their property developments
* **Special Actions**: Providing benefits like "Get Out of Jail Free"

Class Documentation
-----------------

.. automodule:: src.cards
   :members:
   :undoc-members:
   :show-inheritance:

CardType Enum
------------

The ``CardType`` enum defines the two types of cards in the game:

* ``POT_LUCK``: Represents Pot Luck cards
* ``OPPORTUNITY_KNOCKS``: Represents Opportunity Knocks cards

Card Class
---------

The ``Card`` class represents an individual card in the game with the following attributes:

* ``text``: The message displayed when the card is drawn
* ``action``: The function that implements the card's effect
* ``card_type``: The type of card (Pot Luck or Opportunity Knocks)
* ``requires_input``: Flag indicating if the card requires player input
* ``is_special``: Flag indicating if the card has special effects

CardDeck Class
------------

The ``CardDeck`` class manages a deck of cards with the following attributes:

* ``card_type``: The type of cards in this deck
* ``cards``: The list of cards currently in the deck
* ``discard_pile``: The list of cards that have been drawn and discarded
* ``last_drawn_card``: Reference to the most recently drawn card

Common Operations
---------------

The Cards module provides several key operations:

* **Drawing Cards**: Use ``draw_card()`` to take the top card from a deck
* **Returning Cards**: Use ``return_card(card, to_bottom)`` to place a card in the discard pile
* **Handling Jail Cards**: Use ``return_jail_card(card_type)`` to return a Get Out of Jail Free card to the deck
* **Peeking at Cards**: Use ``peek_top_card()`` to look at the top card without drawing it
* **Checking Deck Status**: Use ``get_remaining_count()`` and ``get_discard_count()`` to monitor deck state

Card Data
--------

The card data is defined in the ``game_logic.py`` file, with each card containing:

* A text message to display to the player
* An action function that implements the card's effect on the game state

The action functions typically modify player money, bank funds, free parking pot, or player position on the board. 