Load Excel Module
=================

.. automodule:: src.Loadexcel
   :members:
   :undoc-members:
   :show-inheritance:

The Load Excel module is responsible for extracting game data from Excel spreadsheets (`.xlsx`), validating it, and transforming it into Python data structures (primarily dictionaries) that can be used by the Property Tycoon game. This module serves as a bridge between external data files (like board layout and card text) and the game's internal representation.

This module provides functions to:

*   Load detailed property information for each board space from `PropertyTycoonBoardData.xlsx`, including name, position, type (property, station, utility, tax, special), price, rent, house costs, group, and actions.
*   Handle potential variations in file paths and data formatting within the Excel file.
*   Load key-value pairs for game text (e.g., Chance/Pot Luck card descriptions) from the `Game Text` sheet in `PropertyTycoonCardData.xlsx`.

Detailed Design
---------------

 Component Diagram

This diagram shows how the Load Excel module interacts with external Excel files and provides data to other game components.

.. uml::

    @startuml
    package "External Data" {
        artifact "PropertyTycoonBoardData.xlsx" as BoardDataXlsx
        artifact "PropertyTycoonCardData.xlsx" as CardDataXlsx
    }

    package "Game Core" {
        (Load Excel Module) as LoadExcel
        (Board Module) as Board
        (Cards Module) as Cards
        (Game Module) as Game
    }

    package "Libraries" {
        (pandas) as PandasLib
        (os) as OsLib
    }

    LoadExcel ..> BoardDataXlsx : Reads
    LoadExcel ..> CardDataXlsx : Reads
    LoadExcel ..> PandasLib : Uses
    LoadExcel ..> OsLib : Uses

    Board ..> LoadExcel : Calls load_property_data() >
    Cards ..> LoadExcel : Calls load_game_text() > ' Assumed usage
    Game ..> LoadExcel : Potentially calls > ' e.g., during initialization
    @enduml

 Sequence Diagram: `load_property_data`

Details the steps involved in reading the property data Excel file.

.. uml::

    @startuml
    participant "Caller" as Caller <<e.g., Board Init>>
    participant "load_property_data()" as LoadFunc
    participant "os" as OS
    participant "pandas" as pd
    participant "DataFrame" as DF <<pandas.DataFrame>>

    Caller -> LoadFunc : load_property_data(filename)
    activate LoadFunc
    LoadFunc -> OS : path.dirname(__file__)
    OS --> LoadFunc : script_dir
    LoadFunc -> OS : path.abspath(script_dir)
    OS --> LoadFunc : abs_script_dir
    LoadFunc -> OS : path.dirname(abs_script_dir)
    OS --> LoadFunc : current_dir
    LoadFunc -> OS : path.join(current_dir, filename)
    OS --> LoadFunc : file_path
    LoadFunc -> OS : path.exists(file_path)
    OS --> LoadFunc : exists
    alt not exists
        LoadFunc -> OS : path.join(current_dir, "Useful Canvas file", ...)
        OS --> LoadFunc : alt_path
        LoadFunc -> OS : path.exists(alt_path)
        OS --> LoadFunc : alt_exists
        alt alt_exists
            LoadFunc -> LoadFunc : file_path = alt_path
        else File Not Found
            LoadFunc --> Caller : Raise FileNotFoundError
            deactivate LoadFunc
            return
        end
    end
    LoadFunc -> pd : read_excel(file_path, header=3)
    pd --> DF : dataframe
    activate DF
    LoadFunc -> DF : fillna("")
    DF --> LoadFunc : cleaned_df
    deactivate DF
    LoadFunc -> LoadFunc : properties_data = {}
    loop for _, row in cleaned_df.iterrows()
        LoadFunc -> LoadFunc : Get Position, Name, Group, Action, CanBeBought from row
        alt Position is not digit
            continue loop
        end
        LoadFunc -> LoadFunc : position = int(row("Position"))
        LoadFunc -> LoadFunc : property_data = {name, position, group, action, can_be_bought}
        alt Name is Tax
            LoadFunc -> property_data : update(type="tax", amount=...)
        else Name is Special (Jail, Go, etc.)
            LoadFunc -> property_data : update(type="special")
        else Name is Station
            LoadFunc -> property_data : update(type="station", price=200, rent=25, ...)
        else Name is Utility
            LoadFunc -> property_data : update(type="utility", price=150, ...)
        else CanBeBought and Price exists
            LoadFunc -> LoadFunc : Parse Price, Rent, House Costs (£.1 to £.6)
            LoadFunc -> property_data : update(type="property", price, rent, house_costs=(), ...)
        else Default
             LoadFunc -> property_data : update(type="special")
        end
        LoadFunc -> properties_data : properties_data(str(position)) = property_data
    end loop
    LoadFunc --> Caller : properties_data dictionary
    deactivate LoadFunc
    @enduml

 Sequence Diagram: `load_game_text`

Shows the simpler process of reading the card/game text sheet.

.. uml::

    @startuml
    participant "Caller" as Caller <<e.g., Cards Init>>
    participant "load_game_text()" as LoadFunc
    participant "os" as OS
    participant "pandas" as pd
    participant "DataFrame" as DF <<pandas.DataFrame>>

    Caller -> LoadFunc : load_game_text(filename, sheet_name)
    activate LoadFunc
    LoadFunc -> OS : path.dirname(__file__) ' Similar path logic as above
    OS --> LoadFunc : current_dir
    LoadFunc -> OS : path.join(current_dir, filename)
    OS --> LoadFunc : file_path
    LoadFunc -> pd : read_excel(file_path, sheet_name=sheet_name)
    pd --> DF : dataframe
    activate DF
    LoadFunc -> LoadFunc : card_data = {}
    loop for index, row in dataframe.iterrows()
        LoadFunc -> LoadFunc : key = row("Key")
        LoadFunc -> LoadFunc : text = row("Text")
        LoadFunc -> card_data : card_data(key) = text
    end loop
    LoadFunc --> Caller : card_data dictionary
    deactivate DF
    deactivate LoadFunc
    alt Exception (FileNotFound, KeyError, etc.)
        LoadFunc -> print() : Error message
        LoadFunc --> Caller : None
    end
    @enduml


 Data Structure Diagram (Conceptual - Property Data)

Illustrates the structure of the dictionary returned by `load_property_data`. The keys are string representations of the board position numbers.

.. uml::

    object "properties_data (dict)" as PropertiesDict {
      "1": PropertyObject1
      "2": PropertyObject2
      ...
      "40": PropertyObject40
    }

    package "Example Property Objects (dict)" {
        object "PropertyObject1 (GO)" as Prop1 {
            name = "Go"
            position = 1
            group = None
            action = "Collect £200"
            can_be_bought = False
            type = "special"
        }
        object "PropertyObject2 (Old Kent Road)" as Prop2 {
            name = "Old Kent Road"
            position = 2
            group = "Brown"
            action = None
            can_be_bought = True
            type = "property"
            price = 60
            rent = 2
            owner = None
            house_costs = (10, 30, 90, 160, 250) ' Rent with 1-4 houses, then hotel
            houses = 0
            is_mortgaged = False
        }
        object "PropertyObject6 (King's Cross Station)" as Prop6 {
            name = "King's Cross Station"
            position = 6
            group = "Station"
            action = None
            can_be_bought = True
            type = "station"
            price = 200
            rent = 25 ' Base rent
            owner = None
            is_station = True
        }
         object "PropertyObject13 (Tesla Power Co)" as Prop13 {
            name = "Tesla Power Co"
            position = 13
            group = "Utility"
            action = None
            can_be_bought = True
            type = "utility"
            price = 150
            rent = 0 ' Rent depends on dice roll & ownership
            owner = None
            is_utility = True
        }
         object "PropertyObject39 (Super Tax)" as Prop39 {
            name = "Super Tax"
            position = 39
            group = None
            action = "Pay £100"
            can_be_bought = False
            type = "tax"
            amount = 100
        }
    }

    PropertiesDict::"1" --> Prop1
    PropertiesDict::"2" --> Prop2
    PropertiesDict::"6" --> Prop6
    PropertiesDict::"13" --> Prop13
    PropertiesDict::"39" --> Prop39