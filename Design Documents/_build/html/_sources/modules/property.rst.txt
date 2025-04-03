Property Module
===============

The Property module defines and manages all purchasable spaces on the Property Tycoon game board, including streets, stations, and utilities. It handles property ownership, rent calculations, development with houses and hotels, mortgaging, and trading. This module serves as the backbone for the economic aspects of the game.

High-Level Design
-----------------

Use Case Diagram
~~~~~~~~~~~~~~~~

Illustrates the primary interactions involving properties from a player's perspective.

.. uml::
   :caption: Property Module Use Cases

   @startuml
   left to right direction
   actor Player

   rectangle "Property Management" {
     Player -- (Land on Property)
     Player -- (Buy Property)
     Player -- (Pay Rent)
     Player -- (Develop Property)
     Player -- (Mortgage Property)
     Player -- (Unmortgage Property)
     Player -- (Sell Development)

     (Land on Property) --> (Pay Rent) : if owned by another
     (Land on Property) --> (Buy Property) : if unowned
     (Develop Property) ..> (Build House) : include
     (Develop Property) ..> (Build Hotel) : include
     (Sell Development) ..> (Sell House) : include
     (Sell Development) ..> (Sell Hotel) : include
   }
   @enduml

Domain Model
~~~~~~~~~~~~

Shows the core `Property` concept and its relationship with an `Owner` (presumably a Player).

.. uml::
   :caption: Property Domain Model

   @startuml
   class Property {
     name: str
     group: str
     price: int
     base_rent: int
     houses: int
     has_hotel: bool
     is_station: bool
     is_utility: bool
     mortgaged: bool
   }

   class Player {
      name: str
      properties: list<Property>
      pay(amount: int)
      receive(amount: int)
   }

   Property "1" *-- "0..1" Player : owner >
   @enduml


Detailed Design
---------------

Class Diagram
~~~~~~~~~~~~~~

Details the attributes and methods of the `Property` class.

.. uml::
   :caption: Property Class Diagram

   @startuml
   class Property {
     + name: str
     + group: str
     + price: int
     + base_rent: int
     + owner: Player
     + houses: int
     + has_hotel: bool
     + house_costs: list<int>
     + is_station: bool
     + is_utility: bool
     + mortgaged: bool
     --
     + __init__(data: dict)
     + calculate_rent(dice_roll: int = None, properties: list = None): int
     + has_monopoly(properties: list): bool
     + can_build_house(properties: list): bool
     + can_build_hotel(properties: list): bool
     + build_house(): bool
     + build_hotel(): bool
     + sell_house(): bool
     + sell_hotel(): bool
     + mortgage(): bool
     + unmortgage(): bool
     + get_mortgage_value(): int
     + get_unmortgage_cost(): int
     + get_house_sale_value(): int
     + get_hotel_sale_value(): int
     + charge_rent(player: Player, dice_roll: int = None): int
   }

   Property "1" o-- "0..1" Player : owner

   note right of Property::calculate_rent
     Rent calculation depends on type (station, utility, street),
     ownership count (stations, utilities), development level (houses/hotel),
     monopoly status, and potentially dice roll (utilities).
   end note

   note right of Property::can_build_house
     Requires monopoly, not mortgaged,
     no hotel, and even building across the group.
   end note

   note right of Property::can_build_hotel
     Requires monopoly, not mortgaged,
     no hotel yet, and 5 houses built (implicitly, as houses become 0).
     All properties in group must have 5 houses.
   end note

   note right of Property::charge_rent
     Handles the transaction: calculates rent,
     calls player.pay() and owner.receive().
   end note
   @enduml

State Diagram
~~~~~~~~~~~~~

Models the lifecycle and states of a property.

.. uml::
   :caption: Property State Diagram

   @startuml
   (*) --> Unowned : Game Start

   state Owned {
     state Undeveloped
     state Developed {
        state HousesBuilt {
           HousesBuilt : houses > 0
        }
        state HotelBuilt {
           HotelBuilt : has_hotel = True
        }
        HousesBuilt --> HotelBuilt : build_hotel() (houses == 5)
        HotelBuilt --> HousesBuilt : sell_hotel()
        HousesBuilt -> HousesBuilt : build_house() (houses < 5)
        HousesBuilt -> HousesBuilt : sell_house() (houses > 0)
        Undeveloped --> HousesBuilt : build_house() (houses == 0)
        HousesBuilt --> Undeveloped : sell_house() (houses == 1)
     }
     Undeveloped --> Developed : build_house() (can_build_house())
     Developed --> Undeveloped : sell_house()/sell_hotel() (no houses/hotel left)
   }

   state Mortgaged {
     Mortgaged : mortgaged = True
   }

   Unowned --> Owned : buy_property() / win_auction()
   Owned --> Unowned : transfer_ownership() / auction_failed() ' Implicit actions
   Owned.Undeveloped --> Mortgaged : mortgage() (houses == 0, !has_hotel)
   Mortgaged --> Owned.Undeveloped : unmortgage()

   ' Note: Cannot mortgage if Developed
   ' Note: Cannot develop if Mortgaged
   @enduml


Sequence Diagrams
~~~~~~~~~~~~~~~~~

**Calculating Rent (Street Property)**

.. uml::
   :caption: Sequence Diagram: Calculate Street Rent

   @startuml
   participant "caller" as Caller
   participant "property:Property" as Prop
   participant "owner:Player" as Owner
   participant "group_prop:Property" as GroupProp

   Caller -> Prop : calculate_rent(properties=owner.properties)
   activate Prop
   Prop -> Prop : check mortgaged
   opt mortgaged
     Prop --> Caller : return 0
   else not mortgaged
     Prop -> Prop : check is_station / is_utility (false)
     Prop -> Prop : check has_hotel
     alt has_hotel
       Prop --> Caller : return house_costs(-1)
     else not has_hotel
       Prop -> Prop : check houses > 0
       alt houses > 0
         Prop --> Caller : return house_costs(houses-1)
       else houses == 0
         Prop -> Prop : has_monopoly(properties)
         activate Prop
         Prop -> Owner : get properties in group
         loop for each property in group
            Prop -> GroupProp : check owner == self.owner
         end
         Prop --> Prop : return monopoly_status
         deactivate Prop
         alt monopoly_status == True
           Prop --> Caller : return base_rent * 2
         else monopoly_status == False
           Prop --> Caller : return base_rent
         end
       end
     end
   end
   deactivate Prop
   @enduml

**Calculating Rent (Station)**

.. uml::
   :caption: Sequence Diagram: Calculate Station Rent

   @startuml
   participant "caller" as Caller
   participant "station:Property" as Station
   participant "owner:Player" as Owner
   participant "other_station:Property" as OtherStation

   Caller -> Station : calculate_rent(properties=owner.properties)
   activate Station
   Station -> Station : check mortgaged (assume false)
   Station -> Station : check is_station (true)
   Station -> Owner : get properties
   activate Owner
   Owner --> Station : list of properties
   deactivate Owner
   Station -> Station : count owned stations
   activate Station
   loop for each property p in properties
     Station -> OtherStation : check is_station and owner == self.owner
     activate OtherStation
     OtherStation --> Station : bool
     deactivate OtherStation
   end
   Station --> Station : station_count
   deactivate Station
   Station -> Station : rent = base_rent * (2**(station_count - 1))
   Station --> Caller : return rent
   deactivate Station
   @enduml

**Building a House**

.. uml::
   :caption: Sequence Diagram - Building a House

   @startuml
   participant "player:Player" as Player
   participant "property:Property" as Prop
   participant "game:Game" as Game ' Assumed controller

   Player -> Game : request_build_house(property)
   activate Game
   Game -> Prop : can_build_house(all_properties)
   activate Prop
   Prop -> Prop : check !is_station, !is_utility, !mortgaged, !has_hotel
   Prop -> Prop : has_monopoly(all_properties)
   activate Prop
   ' ... monopoly check ...
   Prop --> Prop : monopoly_status
   deactivate Prop
   Prop -> Prop : check even build rule
   Prop --> Game : can_build
   deactivate Prop

   opt can_build == true
     Game -> Player : deduct_house_cost(property.house_costs(0))
     Game -> Prop : build_house()
     activate Prop
     Prop -> Prop : houses += 1
     Prop --> Game : return true
     deactivate Prop
   end
   Game --> Player : result
   deactivate Game
   @enduml

**Mortgaging a Property**

.. uml::
   :caption: Sequence Diagram - Mortgaging a Property

   @startuml
   participant "player:Player" as Player
   participant "property:Property" as Prop
   participant "game:Game" as Game ' Assumed controller

   Player -> Game : request_mortgage(property)
   activate Game
   Game -> Prop : mortgage()
   activate Prop
   Prop -> Prop : check !mortgaged and houses == 0 and !has_hotel
   alt condition met
     Prop -> Prop : mortgaged = true
     Prop -> Player : receive(property.get_mortgage_value())
     Prop --> Game : return true
   else condition not met
     Prop --> Game : return false
   end
   deactivate Prop
   Game --> Player : result
   deactivate Game
   @enduml


Key Classes Overview
--------------------

*   **Property**: Represents a single purchasable tile on the board. It stores its attributes (name, group, price, rent values, development costs), current state (owner, houses, hotel, mortgaged), and provides methods for calculating rent based on complex rules, managing development (building/selling houses/hotels), and handling mortgaging. It interacts implicitly with a `Player` class for ownership and transactions.

API Documentation
------------------

.. automodule:: src.Property
   :members:
   :undoc-members:
   :show-inheritance: