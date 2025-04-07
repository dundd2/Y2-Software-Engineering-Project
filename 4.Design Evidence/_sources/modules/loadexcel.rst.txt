Load Excel Module
=================

The Load Excel module is responsible for extracting game data from Excel spreadsheets (`.xlsx`), validating it, and transforming it into Python data structures (primarily dictionaries) that can be used by the Property Tycoon game. This module serves as a bridge between external data files (like board layout and card text) and the game's internal representation.

This module provides functions to:

*   Load detailed property information for each board space from `PropertyTycoonBoardData.xlsx`, including name, position, type (property, station, utility, tax, special), price, rent, house costs, group, and actions.
*   Handle potential variations in file paths and data formatting within the Excel file.
*   Load key-value pairs for game text (e.g., Chance/Pot Luck card descriptions) from the `Game Text` sheet in `PropertyTycoonCardData.xlsx`.

.. automodule:: src.Sound_Manager
   :members:
   :undoc-members:
   :show-inheritance:


Detailed Design
---------------

 Component Diagram

This diagram shows how the Load Excel module interacts with external Excel files and provides data to other game components.

.. uml::
   :caption: Component Diagram

   @startuml
   skinparam package {
     BackgroundColor white
     BorderColor black
     ArrowColor black
   }
   skinparam artifact {
     BackgroundColor white
     BorderColor black
   }
   skinparam component {
     BackgroundColor white
     BorderColor black
   }

   package "External Data" {
       artifact "PropertyTycoonBoardData.xlsx" as BoardDataXlsx
       artifact "PropertyTycoonCardData.xlsx" as CardDataXlsx
   }

   package "Game Core" {
       component "Load Excel Module" as LoadExcel
       component "Board Module" as Board
       component "Cards Module" as Cards
       component "Game Module" as Game
   }

   package "Libraries" {
       component "pandas" as PandasLib
       component "os" as OsLib
   }

   LoadExcel ..> BoardDataXlsx : Reads
   LoadExcel ..> CardDataXlsx : Reads
   LoadExcel ..> PandasLib : Uses
   LoadExcel ..> OsLib : Uses

   Board ..> LoadExcel : "Calls load_property_data()"
   Cards ..> LoadExcel : "Calls load_game_text()"
   Game ..> LoadExcel : "May call during init"
   @enduml

 Sequence Diagram: `load_property_data`

Details the steps involved in reading the property data Excel file.

.. uml::
   :caption: Sequence Diagram: load_property_data

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "Caller" as Caller
   participant "load_property_data()" as LoadFunc
   participant "os" as OS
   participant "pandas" as pd
   participant "DataFrame" as DF

   Caller -> LoadFunc : load_property_data(filename)
   activate LoadFunc
    
   LoadFunc -> OS : Get script directory path
   OS --> LoadFunc : directory path
    
   LoadFunc -> OS : Build file path
   OS --> LoadFunc : file_path
    
   LoadFunc -> OS : Check if file exists
   OS --> LoadFunc : exists status
    
   alt File not found
       LoadFunc -> OS : Try alternative path
       OS --> LoadFunc : alt_path
        
       LoadFunc -> OS : Check if alt path exists
       OS --> LoadFunc : alt_exists
        
       alt Alternative found
           LoadFunc -> LoadFunc : Use alternative path
       else No file found
           LoadFunc --> Caller : Raise FileNotFoundError
           deactivate LoadFunc
           stop
       end
   end
    
   LoadFunc -> pd : read_excel(file_path)
   pd --> LoadFunc : dataframe
    
   LoadFunc -> LoadFunc : Clean data (fillna)
    
   LoadFunc -> LoadFunc : Initialize properties_data dictionary
    
   loop for each row in dataframe
       LoadFunc -> LoadFunc : Extract position, name, etc.
        
       alt Valid position
           LoadFunc -> LoadFunc : Create property_data dict
            
           alt Tax space
               LoadFunc -> LoadFunc : Add tax attributes
           else Special space
               LoadFunc -> LoadFunc : Add special attributes
           else Station
               LoadFunc -> LoadFunc : Add station attributes
           else Utility
               LoadFunc -> LoadFunc : Add utility attributes
           else Regular property
               LoadFunc -> LoadFunc : Add property attributes
           end
            
           LoadFunc -> LoadFunc : Add to properties_data
       end
   end
    
   LoadFunc --> Caller : Return properties_data dictionary
   deactivate LoadFunc
   @enduml

 Sequence Diagram: `load_game_text`

Shows the simpler process of reading the card/game text sheet.

.. uml::
   :caption: Sequence Diagram: load_game_text

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "Caller" as Caller
   participant "load_game_text()" as LoadFunc
   participant "os" as OS
   participant "pandas" as pd
   participant "DataFrame" as DF

   Caller -> LoadFunc : load_game_text(filename, sheet_name)
   activate LoadFunc
    
   LoadFunc -> OS : Build file path
   OS --> LoadFunc : file_path
    
   LoadFunc -> pd : read_excel(file_path, sheet_name)
   pd --> LoadFunc : dataframe
    
   LoadFunc -> LoadFunc : Initialize card_data dictionary
    
   loop for each row in dataframe
       LoadFunc -> LoadFunc : Extract key and text
       LoadFunc -> LoadFunc : Add to card_data dictionary
   end
    
   alt Success
       LoadFunc --> Caller : Return card_data dictionary
   else Exception
       LoadFunc -> LoadFunc : Print error message
       LoadFunc --> Caller : Return None
   end
    
   deactivate LoadFunc
   @enduml

 Data Structure Diagram (Conceptual - Property Data)

Illustrates the structure of the dictionary returned by `load_property_data`. The keys are string representations of the board position numbers.

.. uml::
   :caption: Data Structure Diagram (Property Data)

   @startuml
   skinparam object {
     BackgroundColor white
     BorderColor black
     ArrowColor black
   }

   object "properties_data" as PropertiesDict {
     "1" : GO space
     "2" : Old Kent Road
     "6" : Station
     "13" : Utility
     "39" : Tax space
     ... (more positions)
   }

   object "GO space" as Prop1 {
     name = "Go"
     position = 1
     type = "special"
     action = "Collect £200"
     can_be_bought = False
   }

   object "Old Kent Road" as Prop2 {
     name = "Old Kent Road"
     position = 2
     type = "property"
     group = "Brown"
     price = 60
     rent = 2
     house_costs = (10,30,90,160,250)
   }

   object "Station" as Prop6 {
     name = "King's Cross Station"
     position = 6
     type = "station"
     price = 200
     rent = 25
     is_station = True
   }

   object "Utility" as Prop13 {
     name = "Tesla Power Co"
     position = 13
     type = "utility"
     price = 150
     is_utility = True
   }

   object "Tax space" as Prop39 {
     name = "Super Tax"
     position = 39
     type = "tax"
     amount = 100
   }

   PropertiesDict --> Prop1
   PropertiesDict --> Prop2
   PropertiesDict --> Prop6
   PropertiesDict --> Prop13
   PropertiesDict --> Prop39
   @enduml