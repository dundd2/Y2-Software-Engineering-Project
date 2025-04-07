Sound Manager Module
====================

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

.. automodule:: src.Sound_Manager
   :members:
   :undoc-members:
   :show-inheritance:

Detailed Design
---------------

.. uml::
   :caption: SoundManager Class Diagram

   @startuml
   skinparam class {
     BackgroundColor white
     BorderColor black
     ArrowColor black
   }

   class SoundManager {
       + sound_volume : float
       + music_volume : float
       - sounds : Dict<str, pygame.mixer.Sound>
       - base_path : str
       - sound_path : str
       - music_path : str
       - settings_path : str
       - missing_files : List<str>

       + __init__(): void
       + load_settings(): void
       + save_settings(): void
       + load_sounds(): bool
       + load_music(music_file: str = "background_music.mp3"): bool
       + play_sound(sound_name: str): void
       + play_music(loop: int = -1): void
       + stop_music(): void
       + pause_music(): void
       + unpause_music(): void
       + set_sound_volume(volume: float): void
       + set_music_volume(volume: float): void
       + get_missing_files(): List<str>
   }

   class "pygame.mixer" as PygameMixer {
       + init(): void
       + Sound(filepath: str): SoundInstance
       + music: MusicModule
   }

   class "pygame.mixer.Sound" as SoundInstance {
       + set_volume(volume: float): void
       + play(): void
   }

   class "pygame.mixer.music" as MusicModule {
       + load(filepath: str): void
       + set_volume(volume: float): void
       + play(loop: int): void
       + stop(): void
       + pause(): void
       + unpause(): void
   }

   class "json" as JSON {
       + load(file_handle): dict
       + dump(data: dict, file_handle): void
   }

   class "os" as OS {
       + path: OsPath
       + makedirs(path: str, exist_ok: bool): void
   }

   class "os.path" as OsPath {
       + dirname(path: str): str
       + abspath(path: str): str
       + join(...): str
       + exists(path: str): bool
   }

   SoundManager ..> PygameMixer : uses >
   SoundManager "1" *--> "0..*" SoundInstance : holds in sounds{} >
   SoundManager ..> MusicModule : uses >
   SoundManager ..> JSON : uses for settings >
   SoundManager ..> OS : uses for paths >

   note right of SoundManager : Singleton instance `sound_manager` is created.
   @enduml

.. uml::
   :caption: Sequence Diagram: Initialization

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "Caller" as Caller
   participant "SoundManager.__init__" as Init
   participant "pygame.mixer" as Mixer
   participant "os" as OS
   participant "load_settings()" as LoadSettings

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
           LoadSettings -> OS : open(settings_path, "r")
           OS --> LoadSettings : file_handle
           LoadSettings -> LoadSettings : json.load(file_handle)
           LoadSettings -> Init : Update self.sound_volume
           LoadSettings -> Init : Update self.music_volume
           LoadSettings -> LoadSettings : close file_handle
       end
   LoadSettings --> Init
   deactivate LoadSettings
   Init -> Init : Initialize missing_files = []
   Init --> Caller : SoundManager instance
   deactivate Init
   @enduml

.. uml::
   :caption: Sequence Diagram: Loading Sounds

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "Caller" as Caller
   participant "SoundManager" as SM
   participant "os.path" as OSPath
   participant "pygame.mixer" as Mixer
   participant "Sound" as Sound

   Caller -> SM : load_sounds()
   activate SM
   SM -> SM : missing_files = []
   SM -> SM : required_sounds = {"click": "click.mp3", etc.}
    
   loop for each sound_name, file_name in required_sounds
       SM -> OSPath : join(sound_path, file_name)
       OSPath --> SM : file_path
       SM -> OSPath : exists(file_path)
       OSPath --> SM : exists
        
       alt file exists
           SM -> Mixer : Sound(file_path)
           Mixer --> SM : sound_instance
           SM -> Sound : set_volume(sound_volume)
           SM -> SM : sounds[sound_name] = sound_instance
       else
           SM -> SM : missing_files.append(file_name)
           SM -> SM : print("Missing sound file")
       end
   end
    
   SM -> SM : Check if missing_files is empty
   SM --> Caller : True if all loaded, False otherwise
   deactivate SM
   @enduml

.. uml::
   :caption: Sequence Diagram: Loading Music

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "Caller" as Caller
   participant "SoundManager" as SM
   participant "os.path" as OSPath
   participant "pygame.mixer.music" as Music

   Caller -> SM : load_music(music_file)
   activate SM
   SM -> OSPath : join(music_path, music_file)
   OSPath --> SM : full_music_path
   SM -> OSPath : exists(full_music_path)
   OSPath --> SM : exists
    
   alt file exists
       SM -> Music : load(full_music_path)
       SM -> Music : set_volume(music_volume)
       SM --> Caller : True (Success)
   else
       SM -> SM : missing_files.append(music_file)
       SM -> SM : print("Missing music file")
       SM --> Caller : False (Failure)
   end
   deactivate SM
   @enduml

.. uml::
   :caption: Sequence Diagram: Playing a Sound

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "Caller" as Caller
   participant "SoundManager" as SM
   participant "Sound" as Sound

   Caller -> SM : play_sound("some_sound")
   activate SM
    
   alt "some_sound" in sounds dictionary
       SM -> Sound : Get sounds["some_sound"]
       SM -> Sound : play()
   else
       SM -> SM : print("Sound not loaded")
   end
    
   SM --> Caller
   deactivate SM
   @enduml

.. uml::
   :caption: Sequence Diagram: Setting Volume

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "Caller" as Caller
   participant "SoundManager" as SM
   participant "Sound" as Sound
   participant "save_settings()" as SaveSettings

   Caller -> SM : set_sound_volume(new_volume)
   activate SM
    
   SM -> SM : sound_volume = max(0.0, min(1.0, new_volume))
    
   loop for each sound in sounds.values()
       SM -> Sound : set_volume(sound_volume)
   end
    
   SM -> SaveSettings : save_settings()
   activate SaveSettings
   SaveSettings --> SM
   deactivate SaveSettings
    
   SM --> Caller
   deactivate SM
   @enduml

.. uml::
   :caption: Sequence Diagram: Saving Settings

   @startuml
   skinparam sequence {
     ParticipantBackgroundColor white
     ParticipantBorderColor black
     ArrowColor black
     LifeLineBorderColor gray
     LifeLineBackgroundColor lightgray
   }

   participant "Caller" as Caller
   participant "SoundManager.save_settings" as SaveSettings
   participant "os.path" as OSPath
   participant "json" as JSON

   Caller -> SaveSettings : save_settings()
   activate SaveSettings
    
   SaveSettings -> SaveSettings : existing_settings = {}
   SaveSettings -> OSPath : exists(settings_path)
   OSPath --> SaveSettings : exists
    
   alt file exists
       SaveSettings -> SaveSettings : open(settings_path, "r")
       SaveSettings -> JSON : load(file_handle)
       JSON --> SaveSettings : loaded_settings
       SaveSettings -> SaveSettings : existing_settings = loaded_settings
       SaveSettings -> SaveSettings : close file_handle
   end
    
   SaveSettings -> SaveSettings : existing_settings["sound_volume"] = sound_volume
   SaveSettings -> SaveSettings : existing_settings["music_volume"] = music_volume
   SaveSettings -> SaveSettings : open(settings_path, "w")
   SaveSettings -> JSON : dump(existing_settings, file_handle)
   SaveSettings -> SaveSettings : close file_handle
    
   SaveSettings --> Caller
   deactivate SaveSettings
   @enduml