Property Module
===============

This module defines the `Property` class, representing a single purchasable space on the game board (like streets, stations, utilities). It manages ownership, rent calculation based on development level or group ownership, house/hotel building, and mortgaging.

.. automodule:: src.Property
   :members:
   :undoc-members:
   :show-inheritance:

Diagrams
--------

**Property Class Structure**

.. uml::
   :caption: Structure of the Property class

   @startuml
   class Property {
       + name: str
       + group: str
       + price: int
       + base_rent: int
       + owner: Player <<optional>>
       + houses: int
       + has_hotel: bool
       + house_costs: list<int>
       + is_station: bool
       + is_utility: bool
       + mortgaged: bool
       + __init__(data: dict)
       + calculate_rent(dice_roll, properties)
       + has_monopoly(properties)
       + can_build_house(properties)
       + can_build_hotel(properties)
       + build_house()
       + build_hotel()
       + sell_house()
       + sell_hotel()
       + mortgage()
       + unmortgage()
       + get_mortgage_value()
       + get_unmortgage_cost()
       + get_house_sale_value()
       + get_hotel_sale_value()
       + charge_rent(player, dice_roll)
   }

   Property ..> Player : (references owner)

   @enduml

**Rent Calculation Logic (Activity Diagram)**

.. uml::
   :caption: Flowchart for calculating rent for a property

   @startuml
   start
   if (Property Mortgaged?) then (yes)
     :Return 0 Rent;
     stop
   endif

   if (Is Station?) then (yes)
     :Count Owned Stations;
     :Calculate Rent (25 * 2^(count-1));
     :Return Rent;
     stop
   elseif (Is Utility?) then (yes)
     if (Dice Roll Provided?) then (yes)
       :Count Owned Utilities;
       if (Count > 1?) then (yes)
         :Multiplier = 10;
       else (no)
         :Multiplier = 4;
       endif
       :Calculate Rent (Dice Roll * Multiplier);
       :Return Rent;
     else (no)
       :Return 0 Rent;
     endif
     stop
   else (Street Property)
     if (Has Hotel?) then (yes)
       :Return Hotel Rent (from house_costs);
     elseif (Houses > 0?) then (yes)
       :Return Rent for N Houses (from house_costs);
     elseif (Has Monopoly?) then (yes)
       :Return Base Rent * 2;
     else (no)
       :Return Base Rent;
     endif
     stop
   endif
   @enduml

**Can Build House Logic (`can_build_house`)**
