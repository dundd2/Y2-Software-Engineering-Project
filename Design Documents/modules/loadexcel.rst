Load Excel Module
=================

This module contains functions for loading data from Excel files, which serve as the source of property, card, and other game data for the Property Tycoon game.

Key Features
------------

* **Data Extraction**: Reading property and card data from Excel spreadsheets
* **Data Transformation**: Converting raw Excel data into usable game objects
* **Property Loading**: Creating Property objects with correct attributes
* **Card Loading**: Creating cards with proper text and effects
* **Error Handling**: Robust error management for file access and data parsing
* **Data Validation**: Verification of loaded data integrity
* **Dynamic Updates**: Support for reloading data during development

LoadExcel Functions
-------------------

The module provides several key functions for loading game data:

.. plantuml::

   @startuml
   
   title LoadExcel Module Structure
   
   package "LoadExcel Module" {
     class LoadExcel {
       +load_property_data(file_path)
       +load_card_data(file_path)
       +parse_property_row(row_data)
       +parse_card_row(row_data)
       +validate_property_data(property_data)
       +validate_card_data(card_data)
       +handle_file_error(error, file_path)
       +handle_parse_error(error, row_data)
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
   }
   
   @enduml

Property Data Loading
---------------------

The module loads property data with a specialized process:

.. plantuml::

   @startuml
   
   title Property Data Loading Process
   
   start
   
   :Open Excel File;
   
   :Select Properties Worksheet;
   
   :Iterate Through Property Rows;
   
   repeat
     :Read Property Row;
     
     :Extract Property Attributes;
     note right
       - Name
       - Position
       - Price
       - Group
       - Rent values
       - Mortgage value
       - House/hotel costs
     end note
     
     :Validate Property Data;
     
     :Create Property Object;
     
     :Add to Property Collection;
   repeat while (More Properties?) is (Yes)
   
   :Return Complete Property Collection;
   
   stop
   
   @enduml

Card Data Loading
-----------------

The module loads card data with the following process:

.. plantuml::

   @startuml
   
   title Card Data Loading Process
   
   start
   
   :Open Excel File;
   
   :Select Card Worksheets;
   note right
     Two worksheets:
     - Pot Luck
     - Opportunity Knocks
   end note
   
   :Process Pot Luck Cards;
   
   repeat
     :Read Card Row;
     
     :Extract Card Text;
     
     :Parse Card Effect;
     note right
       Identify effect type:
       - Money
       - Movement
       - Special
     end note
     
     :Create Card Object;
     
     :Add to Pot Luck Deck;
   repeat while (More Pot Luck Cards?) is (Yes)
   
   :Process Opportunity Knocks Cards;
   
   repeat
     :Read Card Row;
     
     :Extract Card Text;
     
     :Parse Card Effect;
     
     :Create Card Object;
     
     :Add to Opportunity Knocks Deck;
   repeat while (More Opportunity Knocks Cards?) is (Yes)
   
   :Return Complete Card Decks;
   
   stop
   
   @enduml

Data Structure
--------------

The module processes data in specific formats:

.. plantuml::

   @startuml
   
   title Excel Data Structure
   
   class "Property Excel Data" as PropertyExcel {
     +Name : String
     +Position : Integer
     +Price : Integer
     +Group : String
     +Base Rent : Integer
     +Rent 1 House : Integer
     +Rent 2 Houses : Integer
     +Rent 3 Houses : Integer
     +Rent 4 Houses : Integer
     +Rent Hotel : Integer
     +Mortgage Value : Integer
     +House Cost : Integer
     +Hotel Cost : Integer
}}}}}}}}}}}}}}}}}}}}}
   
   class "Property Object" as Property {
     +name : String
     +position : int
     +price : int
     +group : String
     +base_rent : int
     +rent_1 : int
     +rent_2 : int
     +rent_3 : int
     +rent_4 : int
     +rent_hotel : int
     +mortgage_value : int
     +house_cost : int
     +hotel_cost : int
}}}}}}}}}}}}}}}}}
   
   class "Card Excel Data" as CardExcel {
     +ID : Integer
     +Type : String
     +Text : String
     +Effect : String
}}}}}}}}}}}}}}}}
   
   class "Card Object" as Card {
     +card_id : int
     +type : String
     +text : String
     +effect_type : String
     +effect_value : Any
}}}}}}}}}}}}}}}}}}}
   
   PropertyExcel ..> Property : converted to
   CardExcel ..> Card : converted to
   
   @enduml

Error Handling
--------------

The module implements robust error handling:

.. plantuml::

   @startuml
   
   title Error Handling System
   
   start
   
   :Attempt Data Load;
   
   if (File Access Error?) then (Yes)
     :Log Error;
     :Display User-Friendly Message;
     :Return Default Data;
   elseif (Parse Error?) then (Yes)
     :Log Row and Error Details;
     :Skip Problematic Row;
     :Continue Processing;
   elseif (Validation Error?) then (Yes)
     :Log Validation Issue;
     :Apply Data Correction if Possible;
     :Flag Warning;
   endif
   
   :Return Successfully Loaded Data;
   
   stop
   
   @enduml

Integration with Game Module
----------------------------

The LoadExcel module integrates with other game components:

.. plantuml::

   @startuml
   
   title LoadExcel Integration
   
   class LoadExcel {
     +load_property_data()
     +load_card_data()
}}}}}}}}}}}}}}}}}
   
   class GameLogic {
     -properties : Dict
     -pot_luck_cards : CardDeck
     -opportunity_knocks_cards : CardDeck
     +initialize_game_data()
}}}}}}}}}}}}}}}}}}}}}}}
   
   class Property {
     +name : String
     +price : int
     +group : String
}}}}}}}}}}}}}}}
   
   class Card {
     +type : String
     +text : String
     +effect_type : String
}}}}}}}}}}}}}}}}}}}}}
   
   class Game {
     +setup_game()
}}}}}}}}}}}}}
   
   LoadExcel ..> Property : creates
   LoadExcel ..> Card : creates
   Game --> LoadExcel : uses
   GameLogic --> LoadExcel : uses
   
   @enduml

Class Documentation
-----------------

.. automodule:: src.Loadexcel
   :members:
   :undoc-members:
   :show-inheritance: