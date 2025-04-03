Sound Manager Module
====================

.. automodule:: src.Sound_Manager
   :members:
   :undoc-members:
   :show-inheritance:

This module provides a centralized `SoundManager` class for loading, playing, and managing sound effects and background music in the game. It handles volume control, settings persistence (via `settings.json`), and provides a simple interface for playing various game sounds identified by logical names.

The Sound Manager is responsible for:

*   Initializing the Pygame mixer.
*   Loading sound effect files (`.mp3`) into memory, associated with specific names (e.g., "dice_roll", "buy_property").
*   Loading background music files.
*   Playing loaded sound effects on demand.
*   Playing, stopping, pausing, and unpausing background music.
*   Managing separate volume levels for sound effects and music.
*   Loading and saving volume settings to a `settings.json` file.
*   Tracking and reporting any missing sound or music files.

Detailed Design
---------------

 SoundManager Class Diagram

This diagram shows the structure of the `SoundManager` class and its interactions with Pygame mixer and the settings file.

.. uml::

    @startuml
    class SoundManager {
        + sound_volume : float
        + music_volume : float
        - sounds : Dict<str, pygame.mixer.Sound>
        - base_path : str
        - sound_path : str
        - music_path : str
        - settings_path : str
        - missing_files : List<str>

        + __init__()
        + load_settings()
        + save_settings()
        + load_sounds() : bool
        + load_music(music_file: str = "background_music.mp3") : bool
        + play_sound(sound_name: str)
        + play_music(loop: int = -1)
        + stop_music()
        + pause_music()
        + unpause_music()
        + set_sound_volume(volume: float)
        + set_music_volume(volume: float)
        + get_missing_files() : List<str>
    }

    class "pygame.mixer" as PygameMixer {
        + init()
        + Sound(filepath: str) : SoundInstance
        + music : MusicModule
    }

    class "pygame.mixer.Sound" as SoundInstance {
        + set_volume(volume: float)
        + play()
    }

    class "pygame.mixer.music" as MusicModule {
        + load(filepath: str)
        + set_volume(volume: float)
        + play(loop: int)
        + stop()
        + pause()
        + unpause()
    }

    class "json" as JSON {
        + load(file_handle) : dict
        + dump(data: dict, file_handle)
    }

    class "os" as OS {
        + path : OsPath
        + makedirs(path, exist_ok)
    }
    class "os.path" as OsPath {
        + dirname(path) : str
        + abspath(path) : str
        + join(...) : str
        + exists(path) : bool
    }


    SoundManager ..> PygameMixer : uses >
    SoundManager "1" *--> "0..*" SoundInstance : holds in sounds{} >
    SoundManager ..> MusicModule : uses >
    SoundManager ..> JSON : uses for settings >
    SoundManager ..> OS : uses for paths >

    note right of SoundManager : Singleton instance `sound_manager` is created.
    @enduml

 Sequence Diagram: Initialization (`__init__`)

Shows the steps taken when a `SoundManager` instance is created.

.. uml::

    @startuml
    participant "Caller" as Caller
    participant "SoundManager.__init__" as Init
    participant "pygame.mixer" as Mixer
    participant "os" as OS
    participant "load_settings()" as LoadSettings <<method>>

    Caller -> Init : SoundManager()
    activate Init
    Init -> Mixer : init()
    Init -> Init : Set default volumes (sound=0.7, music=0.5)
    Init -> Init : Initialize sounds = {}
    Init -> OS : path.dirname(...)
    OS --> Init : base_path
    Init -> OS : path.join(base_path, "assets", "sound")
    OS --> Init : sound_path
    Init -> OS : path.join(base_path, "assets", "music")
    OS --> Init : music_path
    Init -> OS : makedirs(sound_path, exist_ok=True)
    Init -> OS : makedirs(music_path, exist_ok=True)
    Init -> OS : path.join(base_path, "settings.json")
    OS --> Init : settings_path
    Init -> LoadSettings : load_settings()
    activate LoadSettings
        LoadSettings -> OS : path.exists(settings_path)
        OS --> LoadSettings : exists
        alt exists
            LoadSettings -> open(settings_path, "r") : Get file handle
            open() --> LoadSettings : file_handle
            LoadSettings -> json : load(file_handle)
            json --> LoadSettings : settings_dict
            LoadSettings -> Init : Update self.sound_volume (if exists)
            LoadSettings -> Init : Update self.music_volume (if exists)
            LoadSettings -> file_handle : close()
        end
    LoadSettings --> Init
    deactivate LoadSettings
    Init -> Init : Initialize missing_files = ()
    Init --> Caller : SoundManager instance
    deactivate Init
    @enduml

 Sequence Diagram: Loading Sounds (`load_sounds`)

Illustrates the process of loading all required sound effect files.

.. uml::

    @startuml
    participant "Caller" as Caller
    participant "SoundManager" as SM
    participant "os.path" as OSPath
    participant "pygame.mixer" as Mixer
    participant "SoundInstance" as Sound <<pygame.mixer.Sound>>

    Caller -> SM : load_sounds()
    activate SM
    SM -> SM : missing_files = ()
    SM -> SM : required_sounds = {...} ' Define dictionary
    loop for sound_name, file_name in required_sounds.items()
        SM -> OSPath : join(self.sound_path, file_name)
        OSPath --> SM : file_path
        SM -> OSPath : exists(file_path)
        OSPath --> SM : exists
        alt exists
            SM -> Mixer : Sound(file_path)
            Mixer --> Sound : sound_instance
            activate Sound
            Sound -> Sound : set_volume(self.sound_volume)
            Sound --> SM
            deactivate Sound
            SM -> SM : self.sounds(sound_name) = sound_instance
        else File Not Found
            SM -> SM : missing_files.append(file_name)
            SM -> print() : "Missing sound file: ..."
        end
    end loop
    SM -> SM : Check if missing_files is empty
    SM --> Caller : True (all loaded) or False (some missing)
    deactivate SM
    @enduml

 Sequence Diagram: Loading Music (`load_music`)

Shows how the background music file is loaded.

.. uml::

    @startuml
    participant "Caller" as Caller
    participant "SoundManager" as SM
    participant "os.path" as OSPath
    participant "pygame.mixer.music" as Music

    Caller -> SM : load_music(music_file)
    activate SM
    SM -> OSPath : join(self.music_path, music_file)
    OSPath --> SM : full_music_path
    SM -> OSPath : exists(full_music_path)
    OSPath --> SM : exists
    alt exists
        SM -> Music : load(full_music_path)
        SM -> Music : set_volume(self.music_volume)
        SM --> Caller : True (Success)
    else File Not Found
        SM -> SM : missing_files.append(music_file)
        SM -> print() : "Missing music file: ..."
        SM --> Caller : False (Failure)
    end
    deactivate SM
    @enduml

 Sequence Diagram: Playing a Sound (`play_sound`)

Illustrates how a specific sound effect is played.

.. uml::

    @startuml
    participant "Caller" as Caller
    participant "SoundManager" as SM
    participant "SoundInstance" as Sound <<pygame.mixer.Sound>>

    Caller -> SM : play_sound("some_sound")
    activate SM
    alt "some_sound" in self.sounds
        SM -> Sound : Get self.sounds("some_sound")
        Sound -> Sound : play()
        Sound --> SM
    else Sound Not Loaded
        SM -> print() : "Sound 'some_sound' not loaded"
    end
    SM --> Caller
    deactivate SM
    @enduml

 Sequence Diagram: Setting Volume (`set_sound_volume`)

Shows the process for changing the sound effects volume and saving the setting.

.. uml::

    @startuml
    participant "Caller" as Caller
    participant "SoundManager" as SM
    participant "SoundInstance" as Sound <<pygame.mixer.Sound>>
    participant "save_settings()" as SaveSettings <<method>>

    Caller -> SM : set_sound_volume(new_volume)
    activate SM
    SM -> SM : self.sound_volume = max(0.0, min(1.0, new_volume))
    loop for sound in self.sounds.values()
        SM -> Sound : sound instance
        Sound -> Sound : set_volume(self.sound_volume)
        Sound --> SM
    end loop
    SM -> SaveSettings : save_settings()
    activate SaveSettings
        ' ... JSON saving logic ... see Save Settings diagram ...
    SaveSettings --> SM
    deactivate SaveSettings
    SM --> Caller
    deactivate SM
    @enduml

 Sequence Diagram: Saving Settings (`save_settings`)

Illustrates how volume settings are persisted to the JSON file.

.. uml::

    @startuml
    participant "Caller" as Caller <<e.g., set_sound_volume>>
    participant "SoundManager.save_settings" as SaveSettings
    participant "os.path" as OSPath
    participant "json" as JSON

    Caller -> SaveSettings : save_settings()
    activate SaveSettings
    SaveSettings -> SaveSettings : existing_settings = {}
    SaveSettings -> OSPath : exists(self.settings_path)
    OSPath --> SaveSettings : exists
    alt exists
        SaveSettings -> open(self.settings_path, "r") : Get read handle
        open() --> SaveSettings : read_handle
        SaveSettings -> JSON : load(read_handle)
        JSON --> SaveSettings : loaded_settings
        SaveSettings -> SaveSettings : existing_settings = loaded_settings
        SaveSettings -> read_handle : close()
    end
    SaveSettings -> existing_settings : Update "sound_volume" = self.sound_volume
    SaveSettings -> existing_settings : Update "music_volume" = self.music_volume
    SaveSettings -> open(self.settings_path, "w") : Get write handle
    open() --> SaveSettings : write_handle
    SaveSettings -> JSON : dump(existing_settings, write_handle)
    SaveSettings -> write_handle : close()
    SaveSettings --> Caller
    deactivate SaveSettings
    @enduml