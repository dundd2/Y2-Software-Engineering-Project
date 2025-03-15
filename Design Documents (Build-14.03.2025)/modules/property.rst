Property Module
==============

This module contains the Property class that represents properties in the game, including standard properties, stations, and utilities.

Key Features
-----------

* Property data management
* Rent calculation based on property type and development
* Monopoly detection and management
* House and hotel development
* Mortgage handling
* Property valuation

Property Types
------------

The game includes three types of properties:

* **Standard Properties**: Color-coded properties that can be developed with houses and hotels
* **Stations**: Railway stations with rent based on how many stations a player owns
* **Utilities**: Service companies with rent based on dice roll and ownership count

Property Groups
-------------

Standard properties are organized into color groups:

* Brown (2 properties)
* Blue (3 properties)
* Purple (3 properties)
* Orange (3 properties)
* Red (3 properties)
* Yellow (3 properties)
* Green (3 properties)
* Deep Blue (2 properties)

Owning all properties in a group creates a monopoly, which affects rent and allows development.

Rent Calculation
--------------

Rent varies based on several factors:

* **Standard Properties**:
  * Base rent (no development)
  * Double rent when player owns all properties in the group
  * Increased rent with houses (1-4)
  * Maximum rent with a hotel

* **Stations**:
  * Base rent for one station
  * Rent doubles for each additional station owned

* **Utilities**:
  * Rent is 4 times the dice roll if player owns one utility
  * Rent is 10 times the dice roll if player owns both utilities

Development Rules
---------------

Property development follows these rules:

* Player must own all properties in a group (monopoly)
* Development must be even across the group
* Maximum of 4 houses per property
* 5 houses can be converted to 1 hotel
* Houses must be sold evenly across a group


Class Documentation
-----------------

.. automodule:: src.Property
   :members:
   :undoc-members:
   :show-inheritance:

Property Attributes
-----------------

Each property has the following key attributes:

* ``name``: Property name
* ``group``: Color group or type (station/utility)
* ``price``: Purchase price
* ``base_rent``: Base rent amount
* ``owner``: Current owner (Player object or None)
* ``houses``: Number of houses built (0-4)
* ``has_hotel``: Whether the property has a hotel
* ``house_costs``: List of rent amounts for different development levels
* ``is_station``: Whether the property is a station
* ``is_utility``: Whether the property is a utility
* ``mortgaged``: Whether the property is mortgaged

Common Operations
---------------

The Property class provides several key operations:

* ``calculate_rent(dice_roll, properties)``: Calculate the current rent amount
* ``has_monopoly(properties)``: Check if the property is part of a monopoly
* ``can_build_house(properties)``: Check if a house can be built
* ``can_build_hotel(properties)``: Check if a hotel can be built
* ``build_house()``: Build a house on the property
* ``build_hotel()``: Build a hotel on the property
* ``sell_house()``: Sell a house from the property
* ``sell_hotel()``: Sell a hotel from the property
* ``mortgage()``: Mortgage the property
* ``unmortgage()``: Unmortgage the property
* ``get_mortgage_value()``: Get the mortgage value
* ``get_unmortgage_cost()``: Get the cost to unmortgage 