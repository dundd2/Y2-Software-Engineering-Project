Property Module
===============

This module contains the Property class that represents properties in the game, including standard properties, stations, and utilities.

Key Features
------------

* **Property Types**: Implementation of standard properties, stations, and utilities
* **Ownership Management**: Tracking of property ownership and transfers
* **Rent Calculation**: Dynamic calculation of rent based on property development
* **Development Tracking**: Management of houses and hotels on properties
* **Mortgage Handling**: Implementation of mortgage and unmortgage mechanics
* **Visual Representation**: Display of property information and development status
* **Color Group Management**: Organization of properties into color groups

Property Class
--------------

The Property class is the foundation for all purchasable board spaces:

.. plantuml::

   @startuml
   
   class Property {
     +name : String
     +position : int
     +price : int
     +group : String
     +owner : Player
     +is_mortgaged : Boolean
     +houses : int
     +base_rent : int
     +rent_1 : int
     +rent_2 : int
     +rent_3 : int
     +rent_4 : int
     +rent_hotel : int
     +is_station : Boolean
     +is_utility : Boolean
     +mortgage_value : int
     
     +__init__(name, position, price, group)
     +calculate_rent(dice_roll, player_properties)
     +mortgage()
     +unmortgage()
     +add_house()
     +remove_house()
     +add_hotel()
     +remove_hotel()
     +can_build_house(player_properties)
     +can_build_hotel(player_properties)
     +get_development_level()
     +get_group_properties(player_properties)

   
   @enduml

Property Types
--------------

The module supports different types of properties with unique behavior:

.. plantuml::

   @startuml
   
   title Property Type System
   
   class Property {
     +name : String
     +position : int
     +price : int
     +group : String
     +is_station : Boolean
     +is_utility : Boolean
     +calculate_rent()
}}}}}}}}}}}}}}}}}
   
   class "Standard Property" as Standard {
     +houses : int
     +base_rent : int
     +rent_1 : int
     +rent_2 : int
     +rent_3 : int
     +rent_4 : int
     +rent_hotel : int
     +calculate_rent()
}}}}}}}}}}}}}}}}}
   
   class "Station" as Station {
     +base_rent : int
     +calculate_rent()
}}}}}}}}}}}}}}}}}
   
   class "Utility" as Utility {
     +base_multiplier : int
     +group_multiplier : int
     +calculate_rent(dice_roll)
}}}}}}
   
   Property <|-- Standard
   Property <|-- Station
   Property <|-- Utility
   
   note right of Standard
     Rent increases with houses/hotels
     Group ownership doubles base rent
   end note
   
   note right of Station
     Rent increases with number
     of stations owned
   end note
   
   note right of Utility
     Rent is dice roll * multiplier
     Multiplier increases if both utilities owned
   end note
   
   @enduml

Rent Calculation System
-----------------------

Different property types use distinct rent calculation methods:

.. plantuml::

   @startuml
   
   title Rent Calculation System
   
   start
   
   :Property Rent Request;
   
   if (Is Property Mortgaged?) then (Yes)
     :Return 0;
     stop
   endif
   
   if (Property Type?) then (Standard)
     if (Has Color Group Monopoly?) then (Yes)
       if (Development Level?) then (No Houses)
         :Return Double Base Rent;
       else if (Development Level?) then (1 House)
         :Return rent_1;
       else if (Development Level?) then (2 Houses)
         :Return rent_2;
       else if (Development Level?) then (3 Houses)
         :Return rent_3;
       else if (Development Level?) then (4 Houses)
         :Return rent_4;
       else (Hotel)
         :Return rent_hotel;
       endif
     else (No)
       :Return Base Rent;
     endif
   else if (Property Type?) then (Station)
     :Count Owned Stations;
     :Calculate Rent Based on Count;
     note right
       1 station: base_rent
       2 stations: base_rent * 2
       3 stations: base_rent * 4
       4 stations: base_rent * 8
     end note
   else (Utility)
     :Get Dice Roll;
     if (Owns Both Utilities?) then (Yes)
       :Return dice_roll * group_multiplier;
     else (No)
       :Return dice_roll * base_multiplier;
     endif
   endif
   
   :Return Calculated Rent;
   
   stop
   
   @enduml

Development System
------------------

The Property module includes a sophisticated development system for building houses and hotels:

.. plantuml::

   @startuml
   
   title Property Development System
   
   start
   
   :Development Request;
   
   if (Property Type?) then (Not Standard)
     :Reject - Can't Develop;
     stop
   endif
   
   if (Player Owns Color Group?) then (No)
     :Reject - Need Full Group;
     stop
   endif
   
   if (Property is Mortgaged?) then (Yes)
     :Reject - Can't Develop Mortgaged Property;
     stop
   endif
   
   if (Development Type?) then (House)
     if (Has Hotel?) then (Yes)
       :Reject - Already Has Hotel;
       stop
     endif
     
     if (Houses < 4?) then (Yes)
       if (Even Development Rule Check) then (Pass)
         :Add House;
         :Charge House Cost;
       else (Fail)
         :Reject - Uneven Development;
       endif
     else (No)
       :Reject - Max Houses;
     endif
   else (Hotel)
     if (Houses == 4?) then (Yes)
       :Remove 4 Houses;
       :Add Hotel;
       :Charge Hotel Cost;
     else (No)
       :Reject - Need 4 Houses First;
     endif
   endif
   
   stop
   
   @enduml

Mortgage System
---------------

Properties can be mortgaged to raise emergency funds:

.. plantuml::

   @startuml
   
   title Property Mortgage System
   
   start
   
   :Mortgage/Unmortgage Request;
   
   if (Action Type?) then (Mortgage)
     if (Property is Mortgaged?) then (Yes)
       :Reject - Already Mortgaged;
       stop
     endif
     
     if (Has Development?) then (Yes)
       :Reject - Remove Houses First;
       stop
     endif
     
     :Set is_mortgaged = true;
     :Pay Player Mortgage Value;
   else (Unmortgage)
     if (Property is Mortgaged?) then (No)
       :Reject - Not Mortgaged;
       stop
     endif
     
     :Calculate Unmortgage Cost;
     note right
       Unmortgage cost = 
       mortgage_value * 1.1
     end note
     
     if (Player Can Pay?) then (Yes)
       :Charge Player Unmortgage Cost;
       :Set is_mortgaged = false;
     else (No)
       :Reject - Insufficient Funds;
     endif
   endif
   
   stop
   
   @enduml

Color Group Management
----------------------

Properties are organized into color groups that affect development and rent:

.. plantuml::

   @startuml
   
   title Color Group System
   
   package "Color Groups" {
     class "Brown" as Brown #Brown;white {
       2 properties
}}}}}}}}}}}}
     
     class "Light Blue" as LightBlue #LightBlue {
       3 properties
}}}}}}}}}}}}
     
     class "Pink" as Pink #Pink {
       3 properties
}}}}}}}}}}}}
     
     class "Orange" as Orange #Orange {
       3 properties
}}}}}}}}}}}}
     
     class "Red" as Red #Red {
       3 properties
}}}}}}}}}}}}
     
     class "Yellow" as Yellow #Yellow {
       3 properties
}}}}}}}}}}}}
     
     class "Green" as Green #Green {
       3 properties
}}}}}}}}}}}}
     
     class "Dark Blue" as DarkBlue #Blue;white {
       2 properties
}}}}}}}}}}}}
     
     class "Stations" as Stations #White {
       4 properties
}}}}}}}}}}}}
     
     class "Utilities" as Utilities #Gray {
       2 properties
}}}}}}}}}}}}
   }
   
   class Property {
     +group : String
     +get_group_properties()
     +check_group_ownership()
}}}}
   
   Property --> Brown : belongs to
   Property --> LightBlue : belongs to
   Property --> Pink : belongs to
   Property --> Orange : belongs to
   Property --> Red : belongs to
   Property --> Yellow : belongs to
   Property --> Green : belongs to
   Property --> DarkBlue : belongs to
   Property --> Stations : belongs to
   Property --> Utilities : belongs to
   
   @enduml

Property Interaction with Other Modules
---------------------------------------

The Property class interacts with several other modules in the game:

.. plantuml::

   @startuml
   
   title Property Module Integration
   
   class Property {
     +owner : Player
     +calculate_rent()
     +mortgage()
     +unmortgage()
     +add_house()
     +add_hotel()
}}}}}}}}}}}}
   
   class Player {
     +properties : List
     +money : int
     +add_property()
     +remove_property()
     +pay()
     +receive()
}}}}}}}}}}
   
   class GameLogic {
     +properties : Dict
     +handle_property_landing()
     +process_ai_property_purchase()
     +build_house()
     +build_hotel()
     +mortgage_property()
     +unmortgage_property()
}}
   
   class "Development Manager" as DevManager {
     +handle_development_request()
     +check_development_rules()
     +execute_development()
}}
   
   Property "0..*" -- "0..1" Player : owned by >
   Property "0..*" -- "1" GameLogic : managed by >
   Property -- DevManager : developed by >
   
   @enduml

Class Documentation
-----------------

.. automodule:: src.Property
   :members:
   :undoc-members:
   :show-inheritance:
