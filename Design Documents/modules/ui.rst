UI Module
=========

This module contains the user interface components of the game, providing a modern, interactive interface for players to navigate menus, configure game settings, and interact with the game.

Key Features
------------

* **Menu System**: Interactive menus for game configuration and navigation
* **Button Management**: Customizable buttons with hover and click effects
* **Player Information Panel**: Dynamic display of player stats and properties
* **Property Cards**: Detailed property information displays
* **Notification System**: Game event messaging and alerts
* **Dialog Boxes**: Confirmation and decision prompts
* **Visual Feedback**: Animations and effects for user interactions
* **Responsive Design**: Adaptive UI that works at different resolutions

UI Class
--------

The UI class manages all interface elements and user interaction:

.. plantuml::

   @startuml
   
   class UI {
     -screen : Surface
     -width : int
     -height : int
     -font_manager : FontManager
     -current_menu : String
     -buttons : Dict
     -menu_elements : Dict
     -active_dialogs : List
     -property_card_data : Dict
     -player_info_panel : PlayerInfoPanel
     -notification_manager : NotificationManager
     -animation_manager : AnimationManager
     
     +__init__(screen, width, height)
     +draw_menu(menu_name)
     +draw_game_ui(game_state, players, current_player)
     +draw_property_card(property_data)
     +draw_player_info(player)
     +draw_auction_ui(current_bid, current_bidder)
     +draw_development_ui(player, available_properties)
     +draw_trade_ui(player1, player2, offerings)
     +create_button(text, x, y, width, height, action)
     +handle_click(x, y)
     +show_dialog(dialog_type, content)
     +close_dialog()
     +add_notification(message, duration)
     +draw_notifications()
     +animate_card_draw(card_type, card_content)
     +animate_dice_roll(dice_values)
     +animate_money_transfer(source, target, amount)
}}}}}}}
   
   @enduml

Menu System
-----------

The UI module implements a comprehensive menu system for game navigation:

.. plantuml::

   @startuml
   
   title UI Menu Architecture
   
   package "Menu System" {
     class "Main Menu" as MainMenu {
       +title
       +background_image
       +buttons
       +logo
}}}}}
     
     class "Player Setup" as PlayerSetup {
       +title
       +player_slots
       +ai_toggles
       +difficulty_selectors
       +token_selectors
       +navigation_buttons
}}}}}}}}}}}}}}}}}}}
     
     class "Game Rules" as GameRules {
       +title
       +rule_toggles
       +rule_sliders
       +presets
       +custom_settings
       +navigation_buttons
}}}}}}}}}}}}}}}}}}}
     
     class "In-Game HUD" as GameHUD {
       +player_info
       +current_player_indicator
       +action_buttons
       +game_messages
       +property_overview
}}}}}}}}}}}}}}}}}}
     
     class "Development Mode" as DevMode {
       +property_grid
       +development_options
       +cost_indicators
       +confirmation_buttons
}
     
     class "End Game" as EndGame {
       +winner_display
       +final_scores
       +statistics
       +replay_button
       +main_menu_button
}}}}}}}}}}}}}}}}}
   }
   
   class UI {
     +current_menu
     +draw_menu()
     +handle_menu_interaction()
}}}}}}
   
   UI --> MainMenu : renders
   UI --> PlayerSetup : renders
   UI --> GameRules : renders
   UI --> GameHUD : renders
   UI --> DevMode : renders
   UI --> EndGame : renders
   
   MainMenu -down-> PlayerSetup : navigates to
   PlayerSetup -down-> GameRules : navigates to
   GameRules -down-> GameHUD : starts game
   GameHUD -down-> DevMode : toggles
   GameHUD -down-> EndGame : game over
   
   @enduml

Button Management
-----------------

The UI includes a sophisticated button system for user interaction:

.. plantuml::

   @startuml
   
   title UI Button System
   
   class Button {
     -text : String
     -rect : Rect
     -action : Function
     -state : String
     -hover_effect : Effect
     -click_effect : Effect
     -colors : Dict
     -font : Font
     
     +draw(screen)
     +update(mouse_pos)
     +handle_click()
     +is_hovered(mouse_pos)
     +set_state(state)
     +play_hover_sound()
     +play_click_sound()
}}}}}}}}}}}}}}}}}}}
   
   class UI {
     -buttons : Dict
     +create_button()
     +handle_button_events()
     +disable_button()
     +enable_button()
     +highlight_button()
}}}}}}}}}}}}}}}}}}}
   
   class "Action Types" as ActionTypes {
     +ROLL_DICE
     +BUY_PROPERTY
     +END_TURN
     +AUCTION_BID
     +MORTGAGE
     +UNMORTGAGE
     +BUILD_HOUSE
     +BUILD_HOTEL
     +TRADE
}}}}}}
   
   UI "1" *-- "0..*" Button : contains
   Button --> ActionTypes : triggers
   
   @enduml

Player Information Panel
------------------------

The UI includes a dedicated panel for displaying player information:

.. plantuml::

   @startuml
   
   title Player Information Panel
   
   class PlayerInfoPanel {
     -position : Tuple
     -dimensions : Tuple
     -current_player : Player
     -property_list_view : PropertyListView
     -stats_view : PlayerStatsView
     
     +draw(screen, player)
     +update_property_list(properties)
     +show_detailed_stats()
     +toggle_visibility()
     +highlight_current_player()
}}}}}}}
   
   class PropertyListView {
     -properties : List
     -scroll_position : int
     -visible_items : int
     
     +draw(screen, properties)
     +scroll_up()
     +scroll_down()
     +select_property(index)
     +highlight_property(property_data)
}}}}}}}}}}}}}}
   
   class PlayerStatsView {
     -player : Player
     -statistics : Dict
     
     +draw(screen, player)
     +update_stats(player)
     +show_net_worth()
     +show_cash_flow()
}}}}}}}}}}}}}}}}}
   
   class UI {
     -player_info_panel : PlayerInfoPanel
     +draw_player_info()
     +update_player_panel()
}}
   
   UI "1" *-- "1" PlayerInfoPanel
   PlayerInfoPanel "1" *-- "1" PropertyListView
   PlayerInfoPanel "1" *-- "1" PlayerStatsView
   
   @enduml

Notification System
-------------------

The UI implements a notification system for game events:

.. plantuml::

   @startuml
   
   title Notification System
   
   class NotificationManager {
     -notifications : List
     -max_notifications : int
     -animation_speed : float
     
     +add_notification(message, duration, type)
     +update_notifications()
     +draw_notifications(screen)
     +clear_notifications()
     +play_notification_sound(type)
}}}}}}}}}}
   
   class Notification {
     -message : String
     -creation_time : float
     -duration : float
     -opacity : float
     -position : Tuple
     -type : String
     
     +update()
     +draw(screen)
     +is_expired()
     +animate_in()
     +animate_out()
}}}}}}}}}}}}}}
   
   enum NotificationType {
     INFO
     WARNING
     SUCCESS
     ERROR
     GAME_EVENT
}}}}}}}}}}
   
   class UI {
     -notification_manager : NotificationManager
     +add_notification()
     +draw_notifications()
}
   
   UI "1" *-- "1" NotificationManager
   NotificationManager "1" *-- "0..*" Notification
   Notification --> NotificationType
   
   @enduml

Property Cards
--------------

The UI displays detailed property information through property cards:

.. plantuml::

   @startuml
   
   title Property Card System
   
   class PropertyCard {
     -property_data : Dict
     -position : Tuple
     -dimensions : Tuple
     -is_visible : Boolean
     -animation_state : float
     
     +draw(screen, property_data)
     +show()
     +hide()
     +animate_in()
     +animate_out()
     +draw_rent_table()
     +draw_development_info()
     +draw_ownership_info()
     +toggle_detailed_view()
}}}
   
   class PropertyCardRenderer {
     +render_standard_property(screen, card, property_data)
     +render_station(screen, card, property_data)
     +render_utility(screen, card, property_data)
     +draw_color_band(screen, card, color)
     +draw_rent_values(screen, card, rent_values)
     +draw_mortgage_info(screen, card, mortgage_value)
}}}}}}}}}
   
   class UI {
     -property_card : PropertyCard
     -property_card_renderer : PropertyCardRenderer
     +show_property_card(property_data)
     +hide_property_card()
}
   
   UI "1" *-- "1" PropertyCard
   UI "1" *-- "1" PropertyCardRenderer
   PropertyCard ..> PropertyCardRenderer : uses
   
   @enduml

Dialog System
-------------

The UI implements a dialog system for user decisions:

.. plantuml::

   @startuml
   
   title Dialog System
   
   class DialogManager {
     -active_dialogs : List
     -dialog_stack : List
     -overlay_opacity : float
     
     +create_dialog(type, content, callbacks)
     +show_dialog(dialog)
     +close_dialog()
     +update_dialogs()
     +draw_dialogs(screen)
     +handle_dialog_event(event)
}}}}}}}
   
   class Dialog {
     -dialog_type : String
     -content : Dict
     -position : Tuple
     -dimensions : Tuple
     -buttons : List
     -result : Any
     -is_closable : Boolean
     
     +draw(screen)
     +handle_click(position)
     +handle_key(key)
     +close(result)
     +animate_in()
     +animate_out()
}}}}}}}}}}}}}}
   
   enum DialogType {
     CONFIRMATION
     PROPERTY_PURCHASE
     AUCTION_BID
     TRADE_OFFER
     BANKRUPTCY
     JAIL_OPTIONS
     GAME_OVER
}}}}}}}}}
   
   class UI {
     -dialog_manager : DialogManager
     +show_dialog()
     +close_dialog()
     +handle_dialog_result()
}}}
   
   UI "1" *-- "1" DialogManager
   DialogManager "1" *-- "0..*" Dialog
   Dialog --> DialogType
   
   @enduml

Animation System
----------------

The UI includes an animation system for visual feedback:

.. plantuml::

   @startuml
   
   title UI Animation System
   
   class AnimationManager {
     -active_animations : List
     -animation_speed : float
     -global_time : float
     
     +create_animation(type, parameters)
     +update_animations(delta_time)
     +draw_animations(screen)
     +clear_animations()
     +is_animating()
}}}}}}}}}}}}}}}
   
   class Animation {
     -animation_type : String
     -start_time : float
     -duration : float
     -progress : float
     -parameters : Dict
     -is_completed : Boolean
     
     +update(current_time)
     +draw(screen)
     +calculate_progress()
     +is_complete()
     +get_interpolated_value()
}}}}}
   
   enum AnimationType {
     FADE_IN
     FADE_OUT
     SLIDE_IN
     SLIDE_OUT
     PULSE
     SHAKE
     CARD_FLIP
     DICE_ROLL
     MONEY_TRANSFER
}}}}}}}}}}}}}}
   
   class UI {
     -animation_manager : AnimationManager
     +create_animation()
     +update_animations()
     +wait_for_animations()
}}
   
   UI "1" *-- "1" AnimationManager
   AnimationManager "1" *-- "0..*" Animation
   Animation --> AnimationType
   
   @enduml

Responsive Design
-----------------

The UI adapts to different screen resolutions and aspect ratios:

.. plantuml::

   @startuml
   
   title UI Responsive Design
   
   class ResponsiveLayout {
     -base_resolution : Tuple
     -current_resolution : Tuple
     -scale_factor : float
     -horizontal_alignment : String
     -vertical_alignment : String
     
     +calculate_position(base_x, base_y)
     +calculate_dimensions(base_width, base_height)
     +calculate_font_size(base_size)
     +calculate_scale_factor()
     +adapt_ui_elements(elements)
     +get_layout_mode()
}}}}}}}}}}}}}}}}}}
   
   enum LayoutMode {
     DESKTOP_WIDE
     DESKTOP_STANDARD
     TABLET_LANDSCAPE
     TABLET_PORTRAIT
     MOBILE
}}}}}}
   
   class UI {
     -responsive_layout : ResponsiveLayout
     +resize(new_width, new_height)
     +reposition_elements()
     +adapt_to_resolution()
}}
   
   UI "1" *-- "1" ResponsiveLayout
   ResponsiveLayout --> LayoutMode
   
   @enduml

Integration with Game Module
----------------------------

The UI module integrates closely with the Game module:

.. plantuml::

   @startuml
   
   title UI Integration with Game
   
   class UI {
     +draw_menu()
     +draw_game_ui()
     +handle_click()
     +show_dialog()
}}}}}}}}}}}}}}
   
   class Game {
     -ui : UI
     -state : String
     +render()
     +handle_events()
     +handle_action()
}}}}}}}}}}}}}}}}
   
   class GameRenderer {
     -ui : UI
     +render_game_state()
     +render_players()
     +render_board()
}}}}}}}}}}}}}}}
   
   class GameEventHandler {
     -ui : UI
     +process_events()
     +handle_mouse_click()
     +handle_key_press()
}}}}}}}}}}}}}}}}}}}
   
   Game *-- UI
   GameRenderer --> UI : uses
   GameEventHandler --> UI : uses
   
   note right of UI
     UI receives game state
     and renders appropriate
     interface elements
   end note
   
   note left of Game
     Game uses UI to display
     information and gather
     user input
   end note
   
   @enduml

Class Documentation
-----------------

.. automodule:: src.UI
   :members:
   :undoc-members:
   :show-inheritance:
