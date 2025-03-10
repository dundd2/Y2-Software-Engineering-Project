Game Flow and Structure
=====================

This section provides visual representations of the game's flow and structure using diagrams.

AI Components
-----------

AI Decision Factors
^^^^^^^^^^^^^^^^^

This diagram shows the factors that influence AI decision making:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam componentBackgroundColor lightYellow
   skinparam componentBorderColor black
   skinparam arrowColor black

   package "AI Decision Engine" {
     [Property Evaluation] as PE
     [Risk Assessment] as RA
     [Strategy Selection] as SS
     [Market Analysis] as MA
   }

   package "Input Factors" {
     [Current Cash] as CC
     [Property Portfolio] as PP
     [Player Positions] as PPos
     [Game Phase] as GP
   }

   package "Analysis Metrics" {
     [Return on Investment] as ROI
     [Risk Level] as RL
     [Market Opportunity] as MO
     [Competition Level] as CL
   }

   package "Decision Outputs" {
     [Purchase Decision] as PD
     [Development Plan] as DP
     [Trade Proposals] as TP
     [Asset Management] as AM
   }

   CC --> PE
   PP --> PE
   PPos --> MA
   GP --> SS

   PE --> ROI
   RA --> RL
   MA --> MO
   MA --> CL

   ROI --> PD
   RL --> SS
   MO --> TP
   CL --> DP

   SS --> AM
   @enduml

AI Decision Making
^^^^^^^^^^^^^^^^^

This diagram shows how the AI makes decisions during the game based on the actual code implementation:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black

   start
   :AI Turn Start;
   note right
     - Determine AI difficulty level (easy/hard)
     - Load appropriate AI strategy
     - Analyze current game state
   end note

   partition "Pre-Turn Analysis" {
     :Evaluate Game State;
     note right
       - Check current position on board
       - Analyze cash reserves
       - Review property portfolio
       - Assess opponent positions and assets
     end note
     
     :Calculate Risk Level;
     note right
       - Determine cash safety threshold
       - Evaluate property development opportunities
       - Assess bankruptcy risk
       - Calculate expected returns
     end note
   }

   partition "Property Analysis" {
     if (On Property Space?) then (yes)
       if (Property Owned?) then (yes)
         :Calculate and Pay Rent;
         note right
           - Determine rent amount based on property development
           - Transfer funds to property owner
           - Update cash reserves
         end note
       else (no)
         :Analyze Property Value;
         note right
           - Check property price vs. available cash
           - Calculate property's strategic value
           - Assess property's position on board
           - Evaluate rent potential
         end note
         
         :Check Property Set Completion;
         note right
           - Identify if property completes a set
           - Check how many properties in set are owned
           - Determine monopoly potential
         end note
         
         :Calculate Expected Return;
         note right
           - Estimate future rent income
           - Calculate development potential
           - Assess risk vs. reward ratio
           - Compare to alternative investments
         end note
         
         :Evaluate Current Cash Position;
         note right
           - Check if purchase maintains minimum cash reserve
           - Calculate post-purchase financial position
           - Assess impact on development plans
         end note
         
         if (Worth Buying?) then (yes)
           if (Can Afford?) then (yes)
             :Purchase Property;
             note right
               - Transfer funds to bank
               - Add property to portfolio
               - Update ownership records
               - Recalculate asset value
             end note
           else (no)
             :Consider Mortgage Options;
             note right
               - Identify low-value properties to mortgage
               - Calculate mortgage values
               - Assess impact on strategy
             end note
             
             if (Can Free Up Cash?) then (yes)
               :Mortgage Properties;
               note right
                 - Select properties to mortgage
                 - Receive mortgage value
                 - Update property status
               end note
               
               :Purchase Property;
             endif
           endif
         else (no)
           :Pass on Purchase;
           note right
             - Allow property to go to auction
             - Prepare auction strategy
             - Set maximum bid amount
           end note
         endif
       endif
     endif
   }

   partition "Development Strategy" {
     :Analyze Building Opportunities;
     note right
       - Check for complete property sets
       - Calculate development costs
       - Assess cash position after development
       - Prioritize high-return properties
     end note
     
     if (Should Build?) then (yes)
       :Evaluate Development Options;
       note right
         - Calculate cost of houses/hotels
         - Determine optimal distribution
         - Assess rent increase potential
       end note
       
       if (Profitable Location?) then (yes)
         :Build Houses/Hotels;
         note right
           - Select properties for development
           - Pay development costs
           - Update property status
           - Recalculate asset value
         end note
       endif
     endif
   }

   partition "Financial Management" {
     :Assess Financial Health;
     note right
       - Calculate current assets vs. liabilities
       - Project future cash flow
       - Identify financial risks
     end note
     
     if (In Financial Trouble?) then (yes)
       :Evaluate Assets;
       note right
         - Rank properties by strategic value
         - Identify development to sell
         - Calculate liquidation values
       end note
       
       :Prioritize Properties;
       note right
         - Determine which properties to keep
         - Identify non-essential properties
         - Protect monopoly sets if possible
       end note
       
       if (Need to Sell?) then (yes)
         :Sell Buildings;
         note right
           - Sell houses/hotels for cash
           - Update property development status
           - Recalculate asset value
         end note
         
         if (Still in Trouble?) then (yes)
           :Mortgage Properties;
           note right
             - Mortgage low-value properties
             - Receive mortgage value
             - Update property status
           end note
         endif
       endif
     endif
   }

   partition "Auction Strategy" {
     if (Property in Auction?) then (yes)
       :Evaluate Auction Property;
       note right
         - Calculate maximum bid value
         - Assess strategic importance
         - Determine bid increment strategy
       end note
       
       if (Worth Bidding?) then (yes)
         :Place Strategic Bid;
         note right
           - Bid based on property value
           - Adjust based on opponent behavior
           - Stay within maximum bid limit
         end note
       endif
     endif
   }

   partition "Risk Management" {
     :Calculate Risk Level;
     note right
       - Assess current financial position
       - Evaluate opponent threats
       - Calculate probability of negative events
     end note
     
     if (High Risk?) then (yes)
       :Implement Conservative Strategy;
       note right
         - Reduce development spending
         - Increase cash reserves
         - Avoid non-essential purchases
         - Prepare contingency plans
       end note
       
       :Maintain Cash Reserve;
       note right
         - Set minimum cash threshold
         - Prioritize liquidity
         - Prepare for unexpected expenses
       end note
     else (no)
       :Implement Aggressive Strategy;
       note right
         - Maximize property acquisition
         - Accelerate development
         - Accept higher risk for greater returns
         - Target opponent vulnerabilities
       end note
       
       :Invest in Properties;
       note right
         - Focus on high-value properties
         - Complete monopoly sets
         - Develop to optimal levels
         - Maximize rent potential
       end note
     endif
   }

   :Update AI Knowledge Base;
   note right
     - Record transaction history
     - Update player behavior models
     - Refine strategy based on outcomes
     - Prepare for next turn
   end note
   
   :End AI Turn;
   stop
   @enduml

AI Strategy Types
^^^^^^^^^^^^^^^^^

This diagram shows the different AI strategy types and their characteristics:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam classBackgroundColor lightGray
   skinparam classBorderColor black
   skinparam arrowColor black

   abstract class AIStrategy {
     + evaluate_move()
     + make_decision()
     + calculate_risk()
     # update_knowledge()
   }

   class AggressiveAI {
     - risk_tolerance: high
     - investment_threshold: low
     + prioritize_purchases()
     + evaluate_trades()
     + calculate_development_priority()
   }

   class ConservativeAI {
     - risk_tolerance: low
     - cash_reserve_target: high
     + evaluate_safety_threshold()
     + calculate_minimum_holdings()
     + plan_emergency_sales()
   }

   class BalancedAI {
     - risk_tolerance: medium
     - strategy_adaptation_rate: high
     + balance_portfolio()
     + adjust_strategy()
     + optimize_holdings()
   }

   class OpportunisticAI {
     - market_analysis: detailed
     - opportunity_threshold: dynamic
     + identify_opportunities()
     + calculate_market_trends()
     + time_investments()
   }

   AIStrategy <|-- AggressiveAI
   AIStrategy <|-- ConservativeAI
   AIStrategy <|-- BalancedAI
   AIStrategy <|-- OpportunisticAI

   @enduml

Auction System
-----------

Auction UI System
^^^^^^^^^^^^^^^^^

This diagram illustrates the auction system when a property is not purchased by the landing player:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black
   
   start
   
   :Player Lands on Unowned Property;
   note right
     - Player moves to property space
     - System identifies property is unowned
     - Offer purchase option to player
   end note
   
   :Player Declines Purchase;
   note right
     - Player chooses not to buy at list price
     - System initiates auction process
     - All eligible players notified
   end note
   
   :Initialize Auction;
   note right
     - Set starting bid (typically £0)
     - Determine eligible participants
     - Set auction timer
     - Prepare auction UI
   end note
   
   :Display Auction UI;
   note right
     - Show property information
     - Display current highest bid and bidder
     - Present bid controls for each player
     - Show auction timer
     - Display minimum bid increment
   end note
   
   while (Auction Active?) is (yes)
     :Process Player Bids;
     
     if (Player Type?) then (Human)
       :Handle Human Player Input;
       note right
         - Process bid button clicks
         - Validate bid amount
         - Check player has sufficient funds
         - Update current bid if valid
       end note
     else (AI)
       :Calculate AI Bid Decision;
       note right
         - Evaluate property value to AI
         - Consider AI's financial position
         - Apply AI difficulty strategy
         - Determine maximum bid amount
         - Decide whether to bid or pass
       end note
       
       if (AI Bids?) then (yes)
         :Process AI Bid;
         note right
           - Calculate strategic bid amount
           - Update current bid
           - Notify players of new bid
         end note
       else (no)
         :AI Passes;
       endif
     endif
     
     :Update Auction Display;
     note right
       - Refresh highest bid amount
       - Update highest bidder name
       - Highlight current leader
       - Update timer display
     end note
     
     if (Auction End Condition?) then (Time Expired)
       :End Auction - Time Expired;
       note right
         - Determine auction winner
         - Process property transfer
         - Deduct bid amount from winner
       end note
     else if (All Others Passed)
       :End Auction - Single Bidder Remains;
       note right
         - Award property to last remaining bidder
         - Process property transfer
         - Deduct bid amount from winner
       end note
     else if (Maximum Bid Reached)
       :End Auction - Maximum Bid;
       note right
         - Award property to highest bidder
         - Process property transfer
         - Deduct bid amount from winner
       end note
     endif
   endwhile (no)
   
   :Award Property to Winner;
   note right
     - Transfer property ownership
     - Update property display
     - Show confirmation message
     - Update player assets
   end note
   
   :Close Auction UI;
   
   stop
   
   @enduml

Auction UI Visual Layout
^^^^^^^^^^^^^^^^^

This diagram illustrates the visual layout of the auction UI:

.. uml::

   @startuml
   skinparam backgroundColor white
   
   rectangle "Auction UI" as AuctionUI #LightBlue {
     rectangle "Auction Header" as AuctionHeader #LightYellow {
       rectangle "Property Name" as AuctionPropName
       rectangle "Color Bar" as AuctionColorBar
     }
     
     rectangle "Property Information" as AuctionPropInfo #White {
       rectangle "Property Details" as PropDetails
       rectangle "Rent Values" as RentValues
     }
     
     rectangle "Auction Status" as AuctionStatus #LightGreen {
       rectangle "Current Bid" as CurrentBid
       rectangle "Highest Bidder" as HighestBidder
       rectangle "Timer" as Timer
     }
     
     rectangle "Player Bidding Controls" as BiddingControls #LightCyan {
       rectangle "Bid Amount Input" as BidInput
       rectangle "Increment/Decrement" as BidAdjust
       rectangle "Place Bid Button" as PlaceBid
       rectangle "Pass Button" as Pass
     }
     
     rectangle "Participant List" as ParticipantList #Pink {
       rectangle "Player 1 Status" as P1Status
       rectangle "Player 2 Status" as P2Status
       rectangle "Player 3 Status" as P3Status
       rectangle "Player 4 Status" as P4Status
     }
   }
   
   AuctionHeader -[hidden]d-> AuctionPropInfo
   AuctionPropInfo -[hidden]d-> AuctionStatus
   AuctionStatus -[hidden]d-> BiddingControls
   BiddingControls -[hidden]d-> ParticipantList
   
   note right of AuctionHeader
     Auction header shows:
     - Property name being auctioned
     - Color group indicator
   end note
   
   note right of AuctionPropInfo
     Property information shows:
     - Purchase price
     - Rent values at different development levels
     - Special rules (if applicable)
   end note
   
   note right of AuctionStatus
     Auction status shows:
     - Current highest bid amount
     - Name of highest bidder
     - Countdown timer for bidding
   end note
   
   note right of BiddingControls
     Bidding controls include:
     - Input field for bid amount
     - +/- buttons to adjust bid
     - Place Bid button to submit bid
     - Pass button to exit auction
   end note
   
   note right of ParticipantList
     Participant list shows:
     - All players in the auction
     - Their current status (active/passed)
     - Highlight for current bidder
     - Indication of AI vs. human players
   end note
   
   note bottom of AuctionUI
     <b>UI Behavior:</b>
     - Appears when property goes to auction
     - Updates in real-time as bids are placed
     - Highlights current highest bidder
     - Shows countdown timer for bidding period
     - Provides visual feedback for valid/invalid bids
     - Automatically processes AI bids based on strategy
   end note
   
   @enduml

Board Components
-----------

Board Camera Controls
^^^^^^^^^^^^^^^^^

This diagram illustrates the camera control system for board movement and zoom functionality:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black
   
   start
   
   partition "Camera Initialization" {
     :Initialize Camera Controls;
     note right
       - Set initial zoom_level (default: 1.0)
       - Set min_zoom and max_zoom limits
       - Initialize offset_x and offset_y to 0
       - Set move_speed and zoom_speed
     end note
   }
   
   partition "Input Handling" {
     while (Game Running?) is (yes)
       :Check for Camera Input;
       
       if (Input Type?) then (Keyboard)
         :Process Keyboard Controls;
         note right
           - Arrow keys for panning
           - +/- keys for zooming
         end note
       else if (Mouse)
         :Process Mouse Controls;
         note right
           - Mouse wheel for zooming
           - Middle button drag for panning
           - Right-click drag for panning
         end note
       else (Touch)
         :Process Touch Controls;
         note right
           - Pinch gesture for zooming
           - Drag gesture for panning
         end note
       endif
     endwhile (no)
   }
   
   partition "Camera Movement" {
     :Calculate Movement Delta;
     note right
       - Apply move_speed multiplier
       - Adjust based on current zoom level
       - Handle boundary constraints
     end note
     
     :Update Camera Position;
     note right
       - Update offset_x and offset_y
       - Apply smoothing for fluid movement
       - Ensure board remains visible
     end note
   }
   
   partition "Zoom Functionality" {
     :Calculate New Zoom Level;
     note right
       - Apply zoom_speed multiplier
       - Clamp between min_zoom and max_zoom
       - Zoom centered on cursor position
     end note
     
     :Apply Zoom Transformation;
     note right
       - Scale board and elements
       - Adjust positions based on zoom center
       - Update visual representation
     end note
   }
   
   partition "Coordinate Transformation" {
     :Transform Board to Screen Coordinates;
     note right
       Function: board_to_screen(x, y)
       - Apply offset translation
       - Apply zoom scaling
       - Convert to screen space
     end note
     
     :Transform Screen to Board Coordinates;
     note right
       Function: screen_to_board(x, y)
       - Reverse zoom scaling
       - Reverse offset translation
       - Convert to board space
     end note
   }
   
   stop
   
   @enduml

Board Flow
^^^^^^^^^^^^^^^^^

This diagram illustrates the board management and player movement:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black

   start
   :Initialize Board;
   note right
     - Create board layout
     - Set up spaces
     - Initialize player positions
   end note

   while (Game Active?) is (yes)
     :Update Board State;
     
     if (Player Moving?) then (yes)
       :Calculate Path;
       :Animate Movement;
       while (Animation in Progress?) is (yes)
         :Update Position;
         :Draw Animation Frame;
       endwhile (no)
       :Update Final Position;
     endif

     if (Property Change?) then (yes)
       :Update Property Ownership;
       :Refresh Display;
     endif

     :Draw Board;
     note right
       - Draw properties
       - Draw players
       - Show messages
       - Update UI
     end note

     if (Special Space?) then (yes)
       :Handle Special Action;
       note right
         - Chance
         - Community Chest
         - Tax
         - Go to Jail
       end note
     endif

   endwhile (no)

   stop
   @enduml

Board Interaction System
^^^^^^^^^^^^^^^^^

This diagram shows how user interactions with the board are processed:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black
   
   start
   
   :Detect User Input;
   note right
     - Mouse click/touch
     - Keyboard input
     - Controller input
   end note
   
   if (Input Type?) then (Mouse/Touch)
     :Get Screen Coordinates;
     note right
       - Capture x, y position
       - Detect click type (left, right, etc.)
       - Record timestamp
     end note
     
     :Transform to Board Coordinates;
     note right
       Function: screen_to_board(x, y)
       - Apply inverse camera transformation
       - Account for zoom level
       - Convert to board space
     end note
     
     :Determine Board Element;
     note right
       - Check if click is on a property
       - Check if click is on a player token
       - Check if click is on a UI element
       - Check if click is on the board itself
     end note
     
     if (Element Type?) then (Property)
       :Handle Property Click;
       note right
         - Show property details
         - Offer purchase/development options
         - Display ownership information
       end note
     else if (Player Token)
       :Handle Player Token Click;
       note right
         - Show player information
         - Display player assets
         - Offer player-specific actions
       end note
     else if (UI Element)
       :Handle UI Element Click;
       note right
         - Trigger button actions
         - Update UI state
         - Process control interactions
       end note
     else (Board Space)
       :Handle Board Space Click;
       note right
         - Show space information
         - Trigger space-specific actions
         - Update camera if needed
       end note
     endif
   else (Keyboard/Controller)
     :Process Command Input;
     note right
       - Handle navigation keys
       - Process action buttons
       - Trigger keyboard shortcuts
     end note
     
     :Update Game State;
     note right
       - Apply command effects
       - Update UI elements
       - Trigger appropriate animations
     end note
   endif
   
   :Update Visual Feedback;
   note right
     - Highlight selected elements
     - Show interaction effects
     - Provide user feedback
   end note
   
   stop
   
   @enduml

Camera Controls Class Diagram
^^^^^^^^^^^^^^^^^

This diagram shows the structure of the camera controls system:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam classBackgroundColor lightGray
   skinparam classBorderColor black
   skinparam arrowColor black
   
   class CameraControls {
     + zoom_level: float
     + offset_x: int
     + offset_y: int
     + move_speed: int
     + zoom_speed: float
     + min_zoom: float
     + max_zoom: float
     + is_dragging: bool
     + drag_start_x: int
     + drag_start_y: int
     
     + handle_camera_controls(keys)
     + handle_mouse_wheel(event)
     + start_drag(x, y)
     + update_drag(x, y)
     + end_drag()
     + zoom_in(center_x, center_y)
     + zoom_out(center_x, center_y)
     + move_camera(dx, dy)
     + reset_camera()
     + board_to_screen(x, y)
     + screen_to_board(x, y)
   }
   
   class Board {
     + camera: CameraControls
     + board_image: Surface
     + board_rects: List[Rect]
     + spaces: List[Space]
     
     + draw(screen)
     + update_board_positions()
     + property_clicked(pos)
     + update_offset(dx, dy)
   }
   
   class Game {
     + board: Board
     + screen: Surface
     
     + handle_mouse_wheel(event)
     + handle_mouse_motion(pos, buttons)
     + handle_mouse_down(pos, button)
     + handle_mouse_up(pos, button)
     + handle_key_down(key)
   }
   
   Game *-- Board
   Board *-- CameraControls
   
   note right of CameraControls
     The CameraControls class manages:
     - Zoom functionality
     - Panning/movement
     - Coordinate transformations
     - Input handling for camera
   end note
   
   note right of Board
     The Board class:
     - Contains a CameraControls instance
     - Applies camera transformations when drawing
     - Handles board-specific interactions
   end note
   
   note right of Game
     The Game class:
     - Routes input events to camera controls
     - Manages high-level game state
     - Coordinates between UI and board
   end note
   
   @enduml

Card Components
-----------

Card Handling Flow
^^^^^^^^^^^^^^^^^

This diagram shows the card drawing and action processing based on the actual code implementation:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black

   start
   :Player Lands on Card Space;
   note right
     - Check space type (Pot Luck or Opportunity Knocks)
     - Trigger card drawing sequence
     - Pause game flow for card action
   end note

   if (Space Type?) then (Pot Luck)
     :Draw Pot Luck Card;
     note right
       - Select random card from Pot Luck deck
       - Remove card from deck temporarily
       - Load card data and action type
     end note
   else (Opportunity Knocks)
     :Draw Opportunity Knocks Card;
     note right
       - Select random card from Opportunity Knocks deck
       - Remove card from deck temporarily
       - Load card data and action type
     end note
   endif

   :Display Card;
   note right
     - Show card popup with text and graphics
     - Animate card appearance
     - Wait for player acknowledgment
     - Highlight card action
   end note

   :Process Card Action;
   note right
     - Determine action type from card data
     - Execute corresponding action function
     - Update game state accordingly
   end note

   if (Action Type?) then (Move Player)
     :Calculate New Position;
     note right
       - Get target position from card
       - Calculate movement path
       - Handle special movement rules
     end note
     
     if (Pass GO?) then (yes)
       :Add £200;
       note right
         - Credit player account
         - Display passing GO message
         - Update money display
       end note
     endif
     
     :Move Player;
     note right
       - Animate player movement
       - Update player position
       - Handle landing on new space
     end note
     
     :Process Destination Space;
     note right
       - Check space type at new position
       - Execute space-specific actions
       - Handle property/tax/special spaces
     end note
   else if (Money Transaction?) then
     if (Receive Money?) then (yes)
       :Add to Player Balance;
       note right
         - Credit specified amount
         - Display transaction message
         - Update money display
         - Check for game effects
       end note
     else if (Pay Bank?) then
       :Deduct from Player Balance;
       note right
         - Debit specified amount
         - Transfer to bank
         - Display transaction message
         - Check for bankruptcy
       end note
     else if (Pay All Players?) then
       :Process Multiple Payments;
       note right
         - Calculate total payment amount
         - Deduct from current player
         - Distribute to other players
       end note
     else if (Collect from All Players?) then
       :Process Multiple Collections;
       note right
         - Calculate total collection amount
         - Collect from each player
         - Add to current player
         - Check others for bankruptcy
       end note
     endif
   else if (Get Out of Jail?) then
     :Add Jail Card to Player;
     note right
       - Increment player's jail_cards count
       - Mark card as held (remove from deck)
       - Display confirmation message
       - Update player status
     end note
   else if (Go To Jail?) then
     :Send Player to Jail;
     note right
       - Move player token to jail position
       - Set player.in_jail = True
       - Reset jail_turns counter
       - End current turn
     end note
   else if (Property Related?) then
     :Handle Property Action;
     note right
       - Identify affected properties
       - Calculate costs/effects
       - Apply changes to properties
     end note
     
     if (Action Subtype?) then (Repairs)
       :Calculate Repair Costs;
       note right
         - Count houses and hotels
         - Multiply by specified amounts
         - Calculate total repair bill
       end note
       
       :Charge Repair Costs;
       note right
         - Deduct total from player
         - Add to free parking pot
         - Check for bankruptcy
       end note
     else if (Property Effect) then
       :Apply Property Effect;
       note right
         - Modify property attributes
         - Update rent calculations
         - Apply temporary effects
       end note
     endif
   else if (Special Action?) then
     :Execute Special Action;
     note right
       - Process unique card effects
       - Apply game rule modifications
       - Handle special case logic
     end note
   endif

   :Return Card to Deck;
   note right
     - Return card to bottom of deck
     - Shuffle deck if specified
     - Reset card state
   end note
   
   :Update Game State;
   note right
     - Refresh player displays
     - Update board state
     - Check for game-ending conditions
     - Continue game flow
   end note

   stop
   @enduml

Card System Flow
^^^^^^^^^^^^^^^^^

This diagram illustrates the card system flow when a player lands on a card space:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black
   
   start
   
   :Player Lands on Card Space;
   note right
     Card space types:
     - Chance space
     - Community Chest space
   end note
   
   if (Card Type?) then (Chance)
     :Draw from Chance Deck;
     note right
       - Get top card from Chance deck
       - Remove card from deck
       - Prepare to execute card effect
     end note
   else (Community Chest)
     :Draw from Community Chest Deck;
     note right
       - Get top card from Community Chest deck
       - Remove card from deck
       - Prepare to execute card effect
     end note
   endif
   
   :Display Card UI;
   note right
     - Show card text and graphics
     - Animate card appearance
     - Wait for player acknowledgment
   end note
   
   :Determine Card Effect Type;
   
   if (Card Effect?) then (Movement)
     :Process Movement Card;
     note right
       Movement types:
       - Advance to specific space
       - Go back X spaces
       - Go to nearest utility/station
       - Go to jail
     end note
     
     :Update Player Position;
     note right
       - Calculate new position
       - Animate player movement
       - Check if passing GO
     end note
     
     :Trigger Space Effect;
     note right
       - Execute effect of destination space
       - May trigger property purchase
       - May trigger rent payment
     end note
   else if (Financial)
     :Process Financial Card;
     note right
       Financial types:
       - Receive money from bank
       - Pay money to bank
       - Pay money to each player
       - Receive money from each player
       - Pay building repairs
     end note
     
     :Update Player Finances;
     note right
       - Add/deduct appropriate amount
       - Update player balance display
       - Check for bankruptcy condition
     end note
   else if (Get Out of Jail Free)
     :Process Jail Card;
     note right
       - Add card to player inventory
       - Update player UI to show card
       - Card remains with player until used
     end note
   else if (Special Effect)
     :Process Special Effect Card;
     note right
       Special effects:
       - Birthday (collect from players)
       - Chairman (pay to players)
       - Property repairs (pay per house/hotel)
       - Street repairs (pay per house/hotel)
     end note
     
     :Execute Special Logic;
     note right
       - Apply complex card effects
       - May involve multiple players
       - May involve property calculations
     end note
   endif
   
   if (Keep Card?) then (yes)
     :Add Card to Player Inventory;
     note right
       - Only for "Get Out of Jail Free" cards
       - Card is removed from deck until used
     end note
   else (no)
     :Return Card to Bottom of Deck;
     note right
       - Place card at bottom of appropriate deck
       - Maintain deck order for future draws
     end note
   endif
   
   :Continue Player Turn;
   
   stop
   
   @enduml

Card UI Visual Layout
^^^^^^^^^^^^^^^^^

This diagram illustrates the visual layout of the card UI when a player draws a card:

.. uml::

   @startuml
   skinparam backgroundColor white
   
   rectangle "Card UI" as CardUI #LightBlue {
     rectangle "Card Header" as CardHeader #LightYellow {
       rectangle "Card Type" as CardType
     }
     
     rectangle "Card Content" as CardContent #White {
       rectangle "Card Text" as CardText
       rectangle "Card Illustration" as CardIllustration
     }
     
     rectangle "Card Effect" as CardEffect #LightGreen {
       rectangle "Effect Description" as EffectDesc
       rectangle "Financial Impact" as FinancialImpact
     }
     
     rectangle "Action Button" as ActionButton #Pink {
       rectangle "OK Button" as OKButton
     }
   }
   
   CardHeader -[hidden]d-> CardContent
   CardContent -[hidden]d-> CardEffect
   CardEffect -[hidden]d-> ActionButton
   
   note right of CardHeader
     Card header shows:
     - Card type (Chance or Community Chest)
     - Distinctive color/icon for card type
   end note
   
   note right of CardContent
     Card content shows:
     - Main card text describing the effect
     - Thematic illustration or icon
     - Visual styling based on card type
   end note
   
   note right of CardEffect
     Effect description shows:
     - Detailed explanation of card effect
     - Financial impact (if applicable)
     - Movement instructions (if applicable)
   end note
   
   note right of ActionButton
     Action button:
     - OK button to acknowledge card
     - Triggers card effect execution
     - Dismisses card UI when clicked
   end note
   
   note bottom of CardUI
     <b>UI Behavior:</b>
     - Card appears with animation when drawn
     - Card effect is executed when OK is clicked
     - Some cards may require additional input
     - Get Out of Jail Free cards show "Keep" option
     - Card UI blocks other interactions until dismissed
   end note
   
   @enduml

Get Out of Jail Card Usage
^^^^^^^^^^^^^^^^^

This diagram illustrates the process of using a "Get Out of Jail Free" card:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black
   
   start
   
   :Player in Jail Selects "Use Card" Option;
   note right
     - Player must be currently in jail
     - Player must have a "Get Out of Jail Free" card
     - Option appears in jail options menu
   end note
   
   :Check Player Inventory;
   
   if (Has Jail Card?) then (yes)
     :Determine Card Source;
     
     if (Card Source?) then (Chance)
       :Remove Card from Player Inventory;
       note right
         - Decrement player's jail card count
         - Update player UI
       end note
       
       :Return Card to Chance Deck;
       note right
         - Place at bottom of Chance deck
         - Card becomes available again
       end note
     else (Community Chest)
       :Remove Card from Player Inventory;
       note right
         - Decrement player's jail card count
         - Update player UI
       end note
       
       :Return Card to Community Chest Deck;
       note right
         - Place at bottom of Community Chest deck
         - Card becomes available again
       end note
     endif
     
     :Release Player from Jail;
     note right
       - Set player.in_jail = False
       - Reset player.jail_turns = 0
       - Enable normal movement
       - Continue player's turn
     end note
     
     :Display Confirmation Message;
     note right
       - Show animation of jail release
       - Display message confirming card use
       - Update player token position
     end note
   else (no)
     :Display Error Message;
     note right
       - Inform player they don't have a card
       - Return to jail options menu
       - Suggest alternative options
     end note
   endif
   
   :Continue Player Turn;
   
   stop
   
   @enduml

Class Structure
-----------

Class Hierarchy
^^^^^^^^^^^^^^^^^

This diagram shows the main class structure of the game based on the actual code implementation:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam classBackgroundColor lightGray
   skinparam classBorderColor black
   skinparam arrowColor black

   class Game {
     + players: List[Player]
     + board: Board
     + current_player: Player
     + dice: Dice
     + cards: Dict[str, List[Card]]
     + game_mode: str
     + time_limit: int
     + ai_difficulty: str
     + bank_money: int
     + game_over: bool
     + winner_index: int
     + logic: GameLogic
     + auction_data: Dict
     + notification: Dict
     + popup_message: Dict
     + free_parking_pot: int
     + start()
     + draw()
     + play_turn()
     + handle_space(player)
     + handle_buy_decision(wants_to_buy)
     + start_auction(property_data)
     + handle_jail_turn(player)
     + move_player(player, spaces)
     + check_passing_go(player, old_position)
     + handle_ai_turn(ai_player)
     + check_game_over()
     + handle_bankruptcy(player)
     + calculate_player_assets(player)
     + draw_dice(dice1, dice2, is_rolling)
     + draw_property_card(property_data)
     + draw_auction(auction_data)
     + draw_jail_options(player)
     + draw_development_ui(property_data)
     + handle_card_action(card, player)
     + handle_fine_payment(player, amount, reason)
     + add_to_free_parking(amount)
     + collect_free_parking(player)
   }

   class Player {
     + name: str
     + player_number: int
     + is_ai: bool
     + money: int
     + properties: List[Property]
     + position: int
     + in_jail: bool
     + jail_turns: int
     + jail_cards: int
     + bankrupt: bool
     + voluntary_exit: bool
     + final_assets: int
     + color: Tuple[int, int, int]
     + player_image: Surface
     + is_moving: bool
     + move_progress: float
     + move_path: List[int]
     + is_active: bool
     + is_winner: bool
     + move(steps)
     + generate_move_path(steps)
     + is_animation_complete()
     + pay(amount)
     + receive(amount)
     + buy_property(property)
     + add_jail_card(card_type)
     + use_jail_card()
     + handle_jail_turn()
     + can_afford(amount)
     + add_property(property)
     + remove_property(property)
     + get_total_assets()
     + get_mortgageable_properties()
     + get_properties_with_houses()
     + get_properties_with_hotels()
     + can_build_houses()
     + can_build_hotels()
     + handle_bankruptcy(creditor)
     + handle_voluntary_exit()
     + draw_player(screen, x, y)
     + update_animation()
     + load_player_image()
     + create_fallback_token()
   }

   class Board {
     + players: List[Player]
     + spaces: List[Space]
     + properties_data: Dict
     + board_image: Surface
     + background_image: Surface
     + board_rects: List[Rect]
     + camera: CameraControls
     + messages: List[str]
     + message_times: List[int]
     + draw(screen)
     + update_board_positions()
     + draw_player(screen, player, rect, index)
     + get_space(position)
     + update_ownership(properties_data)
     + get_property_group(position)
     + get_property_position(position)
     + board_to_screen(x, y)
     + update_offset(dx, dy)
     + property_clicked(pos)
     + add_message(text)
   }

   class Property {
     + name: str
     + group: str
     + price: int
     + base_rent: int
     + owner: Player
     + houses: int
     + has_hotel: bool
     + house_costs: List[int]
     + is_station: bool
     + is_utility: bool
     + mortgaged: bool
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

   class GameLogic {
     + game: Game
     + ai_difficulty: str
     + ai_player: AIPlayer
     + property_data: Dict
     + card_data: Dict
     + game_start()
     + load_property_data()
     + load_card_data()
     + process_turn(player)
     + handle_property_space(player, property_data)
     + handle_card_space(player, card_type)
     + handle_tax_space(player, amount)
     + handle_jail_space(player)
     + handle_free_parking(player)
     + process_card_action(player, card)
     + check_bankruptcy(player, amount, creditor)
     + calculate_assets(player)
     + determine_winner()
   }

   class CameraControls {
     + zoom_level: float
     + offset_x: int
     + offset_y: int
     + move_speed: int
     + zoom_speed: float
     + min_zoom: float
     + max_zoom: float
     + handle_camera_controls(keys)
   }

   class Space {
     + name: str
     + position: int
     + type: str
     + action(player, game)
   }

   class Card {
     + type: str
     + description: str
     + action: str
     + action_value: int
     + execute(player, game)
   }

   class AIPlayer {
     + difficulty: str
     + evaluate_purchase(property, player, game)
     + decide_development(player, game)
     + handle_auction_bid(property, current_bid, player, game)
     + choose_jail_strategy(player, game)
     + evaluate_mortgage_options(player, amount_needed, game)
     + calculate_property_value(property, player, game)
     + determine_risk_level(player, game)
     + make_decision(options, player, game)
   }

   Game *-- Player
   Game *-- Board
   Game *-- GameLogic
   Game *-- Card
   Board *-- Space
   Board *-- CameraControls
   Board o-- Property
   Player o-- Property
   GameLogic o-- AIPlayer
   @enduml

Data Components
-----------

Data Flow
^^^^^^^^^^^^^^^^^

This diagram shows how data flows through the game based on the actual code implementation:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam componentBackgroundColor lightGreen
   skinparam componentBorderColor black
   skinparam arrowColor black

   database "Data Sources" {
     [Property Data Excel] as PDE
     [Card Data Excel] as CDE
     [Configuration Files] as CF
     [Asset Files] as AF
   }

   package "Data Loading" {
     [Excel Reader] as ER
     [Data Parser] as DP
     [Validator] as V
     [Asset Loader] as AL
   }

   package "Game Initialization" {
     [Game Constructor] as GC
     [Board Setup] as BS
     [Player Creation] as PC
     [Property Setup] as PS
     [Card Deck Setup] as CDS
   }

   package "Game State" {
     [Player States] as PST
     [Board State] as BST
     [Property Ownership] as PO
     [Game Progress] as GP
     [Free Parking Pot] as FPP
     [Auction State] as AS
     [Development State] as DS
     [Jail Status] as JS
   }

   package "Game Logic" {
     [Turn Processing] as TP
     [Property Handling] as PH
     [Card Processing] as CP
     [Movement Logic] as ML
     [Rent Calculation] as RC
     [Bankruptcy Handling] as BH
     [Auction Logic] as AL
     [Development Logic] as DL
     [AI Decision Making] as AIDM
   }

   package "User Interface" {
     [Board Rendering] as BR
     [Player Tokens] as PT
     [Property Cards] as PC
     [Dice Animation] as DA
     [Message Display] as MD
     [Button System] as BS
     [Auction UI] as AUI
     [Development UI] as DUI
     [Card Display] as CD
     [Notification System] as NS
   }

   package "Input Processing" {
     [Mouse Handler] as MH
     [Keyboard Handler] as KH
     [Button Handler] as BH
     [Property Selector] as PS
   }

   package "Output Generation" {
     [Screen Updates] as SU
     [Animation System] as ANS
     [Sound Effects] as SE
     [Message Queue] as MQ
   }

   package "Game Flow Control" {
     [Main Game Loop] as MGL
     [Turn Sequencer] as TS
     [Event Dispatcher] as ED
     [State Manager] as SM
   }

   ' Data loading flow
   PDE --> ER : Property data
   CDE --> ER : Card data
   CF --> DP : Game settings
   AF --> AL : Images, sounds
   
   ER --> DP : Raw data
   DP --> V : Structured data
   V --> GC : Validated data
   AL --> GC : Loaded assets
   
   ' Game initialization flow
   GC --> BS : Board configuration
   GC --> PC : Player settings
   GC --> PS : Property data
   GC --> CDS : Card data
   
   BS --> BST : Initial board
   PC --> PST : Initial players
   PS --> PO : Initial properties
   CDS --> GP : Initial card decks
   
   ' Game state updates
   PST --> TP : Player information
   BST --> ML : Board information
   PO --> PH : Property information
   GP --> CP : Card information
   
   ' Game logic flow
   TP --> ML : Movement requests
   ML --> BST : Position updates
   ML --> PH : Land on property
   PH --> RC : Calculate rent
   RC --> PST : Update money
   PH --> AL : Start auction
   AL --> AS : Update auction state
   PH --> DL : Development requests
   DL --> DS : Update development
   CP --> PST : Apply card effects
   CP --> ML : Move player
   CP --> JS : Jail effects
   
   ' AI decision making
   TP --> AIDM : AI turn
   AIDM --> PH : Property decisions
   AIDM --> AL : Auction decisions
   AIDM --> DL : Development decisions
   
   ' User interface flow
   BST --> BR : Board data
   PST --> PT : Player positions
   PO --> PC : Property data
   GP --> DA : Dice results
   
   ' Input processing
   MH --> PS : Property selection
   MH --> BH : Button clicks
   KH --> TP : Key commands
   BH --> TP : Button actions
   PS --> PH : Selected property
   
   ' Output generation
   BR --> SU : Board visuals
   PT --> SU : Player visuals
   PC --> SU : Property cards
   DA --> SU : Dice visuals
   MD --> SU : Messages
   AUI --> SU : Auction interface
   DUI --> SU : Development interface
   CD --> SU : Card display
   NS --> SU : Notifications
   
   ' Game flow control
   MGL --> TS : Turn management
   TS --> TP : Process turn
   TP --> ED : Generate events
   ED --> SM : Update state
   SM --> PST : Update player state
   SM --> BST : Update board state
   SM --> PO : Update property state
   SM --> GP : Update game progress
   
   ' Bankruptcy handling
   RC --> BH : Check bankruptcy
   BH --> PST : Remove bankrupt player
   BH --> PO : Transfer properties
   BH --> GP : Check game end
   
   ' Final output
   SU --> MGL : Display updates
   ANS --> SU : Animation frames
   SE --> MGL : Play sounds
   MQ --> MD : Display messages
   @enduml

State Machine
^^^^^^^^^^^^^^^^^

This diagram shows the game's state transitions based on the actual code implementation:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam stateBorderColor black
   skinparam stateBackgroundColor lightGray

   [*] --> Initialize

   state Initialize {
     [*] --> LoadData
     LoadData : Load property data from Excel
     LoadData : Load card data from Excel
     LoadData : Initialize game constants
     
     LoadData --> SetupPlayers
     SetupPlayers : Create player objects
     SetupPlayers : Set starting money (£1500)
     SetupPlayers : Initialize player tokens
     SetupPlayers : Set AI difficulty
     
     SetupPlayers --> SetupBoard
     SetupBoard : Create board layout
     SetupBoard : Initialize spaces
     SetupBoard : Load board images
     SetupBoard : Setup camera controls
     SetupBoard --> [*]
   }

   Initialize --> GameLoop

   state GameLoop {
     [*] --> PlayerTurn
     
     state PlayerTurn {
       [*] --> CheckJailStatus
       
       state CheckJailStatus {
         [*] --> InJail : Player in jail
         [*] --> NotInJail : Player not in jail
         
         state InJail {
           [*] --> JailOptions
           JailOptions : Offer jail options
           JailOptions : - Use jail card
           JailOptions : - Pay £50 fine
           JailOptions : - Roll for doubles
           
           JailOptions --> UseJailCard : Has jail card
           UseJailCard : Remove jail card
           UseJailCard : Set in_jail = False
           UseJailCard --> EndJailTurn
           
           JailOptions --> PayFine : Choose to pay
           PayFine : Deduct £50
           PayFine : Set in_jail = False
           PayFine --> EndJailTurn
           
           JailOptions --> RollForDoubles : Choose to roll
           RollForDoubles --> FreeFromJail : Rolled doubles
           FreeFromJail : Set in_jail = False
           FreeFromJail --> MovePlayer
           
           RollForDoubles --> StayInJail : No doubles
           StayInJail : Increment jail_turns
           StayInJail --> ForcedPayment : jail_turns >= 3
           ForcedPayment : Deduct £50
           ForcedPayment : Set in_jail = False
           ForcedPayment --> EndJailTurn
           
           StayInJail --> EndJailTurn : jail_turns < 3
         }
         
         state NotInJail {
           [*] --> CheckPlayerType
           
           state CheckPlayerType {
             [*] --> AITurn : is_ai = True
             [*] --> HumanTurn : is_ai = False
             
             state AITurn {
               [*] --> ExecuteAILogic
               ExecuteAILogic : Determine strategy
               ExecuteAILogic : Make decisions
               ExecuteAILogic --> RollDice
             }
             
             state HumanTurn {
               [*] --> WaitForInput
               WaitForInput : Wait for player action
               WaitForInput --> RollDice : Player rolls
             }
           }
         }
       }
       
       NotInJail --> RollDice
       
       state RollDice {
         [*] --> GenerateDiceValues
         GenerateDiceValues : Generate two random numbers
         GenerateDiceValues : Check for doubles
         
         GenerateDiceValues --> CheckTripleDoubles : Third consecutive doubles
         CheckTripleDoubles --> GoToJail : Triple doubles
         GoToJail : Move to jail position
         GoToJail : Set in_jail = True
         GoToJail --> EndTurn
         
         GenerateDiceValues --> MovePlayer : Not triple doubles
       }
       
       state MovePlayer {
         [*] --> CalculatePath
         CalculatePath : Generate movement path
         CalculatePath : Animate player movement
         
         CalculatePath --> CheckPassingGo
         CheckPassingGo : Check if player passes GO
         CheckPassingGo --> CollectPassingGoMoney : Passes GO
         CollectPassingGoMoney : Add £200 to player
         CollectPassingGoMoney --> HandleSpace
         
         CheckPassingGo --> HandleSpace : Doesn't pass GO
       }
       
       state HandleSpace {
         [*] --> DetermineSpaceType
         DetermineSpaceType : Get space at player position
         
         DetermineSpaceType --> HandlePropertySpace : Property space
         DetermineSpaceType --> HandleCardSpace : Card space
         DetermineSpaceType --> HandleTaxSpace : Tax space
         DetermineSpaceType --> HandleJailSpace : Go to jail space
         DetermineSpaceType --> HandleFreeParkingSpace : Free parking space
         DetermineSpaceType --> HandleGoSpace : GO space
         DetermineSpaceType --> HandleJustVisitingSpace : Just visiting space
         
         state HandlePropertySpace {
           [*] --> CheckOwnership
           CheckOwnership : Get property owner
           
           CheckOwnership --> PropertyOwned : Has owner
           PropertyOwned : Calculate rent
           PropertyOwned : Pay rent to owner
           PropertyOwned : Check for bankruptcy
           PropertyOwned --> CheckGameState
           
           CheckOwnership --> PropertyNotOwned : No owner
           PropertyNotOwned : Check if player can afford
           PropertyNotOwned --> OfferPurchase : Can afford
           OfferPurchase : Display property card
           OfferPurchase : Show buy options
           
           OfferPurchase --> BuyProperty : Decides to buy
           BuyProperty : Pay purchase price
           BuyProperty : Add to player properties
           BuyProperty --> CheckGameState
           
           OfferPurchase --> StartAuction : Decides not to buy
           StartAuction : Allow all players to bid
           StartAuction : Track highest bidder
           StartAuction : Award property to winner
           StartAuction --> CheckGameState
           
           PropertyNotOwned --> CheckGameState : Cannot afford
         }
         
         state HandleCardSpace {
           [*] --> DrawCard
           DrawCard : Get card from deck
           DrawCard : Display card to player
           
           DrawCard --> ExecuteCardAction
           ExecuteCardAction : Process card effect
           ExecuteCardAction : - Move player
           ExecuteCardAction : - Money transactions
           ExecuteCardAction : - Property effects
           ExecuteCardAction : - Jail effects
           ExecuteCardAction --> CheckGameState
         }
         
         state HandleTaxSpace {
           [*] --> PayTax
           PayTax : Deduct tax amount
           PayTax : Add to free parking pot
           PayTax : Check for bankruptcy
           PayTax --> CheckGameState
         }
         
         state HandleJailSpace {
           [*] --> SendToJail
           SendToJail : Move to jail position
           SendToJail : Set in_jail = True
           SendToJail --> EndTurn
         }
         
         state HandleFreeParkingSpace {
           [*] --> CollectFreeParking
           CollectFreeParking : Add pot to player
           CollectFreeParking : Reset free parking pot
           CollectFreeParking --> CheckGameState
         }
         
         HandlePropertySpace --> CheckGameState
         HandleCardSpace --> CheckGameState
         HandleTaxSpace --> CheckGameState
         HandleFreeParkingSpace --> CheckGameState
         HandleGoSpace --> CheckGameState
         HandleJustVisitingSpace --> CheckGameState
       }
       
       state CheckGameState {
         [*] --> CheckBankruptcy
         CheckBankruptcy : Check if player is bankrupt
         
         CheckBankruptcy --> ProcessBankruptcy : Player bankrupt
         ProcessBankruptcy : Transfer assets to creditor
         ProcessBankruptcy : Remove player from game
         ProcessBankruptcy --> EndTurn
         
         CheckBankruptcy --> EndTurn : Player not bankrupt
       }
       
       MovePlayer --> HandleSpace
       HandleSpace --> CheckGameState
       CheckGameState --> EndTurn
       
       state EndTurn {
         [*] --> UpdateGameState
         UpdateGameState : Update player status
         UpdateGameState : Update board display
         UpdateGameState --> [*]
       }
       
       EndJailTurn --> EndTurn
     }
     
     PlayerTurn --> CheckEndGame
     
     state CheckEndGame {
       [*] --> EvaluateEndConditions
       EvaluateEndConditions : Check player count
       EvaluateEndConditions : Check time limit
       EvaluateEndConditions : Check voluntary exits
       
       EvaluateEndConditions --> GameContinues : Game not over
       EvaluateEndConditions --> GameEnds : Game over
     }
     
     CheckEndGame --> PlayerTurn : Game Continues
     CheckEndGame --> GameOver : Game Ends
   }

   GameLoop --> GameOver : Game Ends
   
   state GameOver {
     [*] --> CalculateFinalScores
     CalculateFinalScores : Add up property values
     CalculateFinalScores : Count houses and hotels
     CalculateFinalScores : Add cash on hand
     
     CalculateFinalScores --> DetermineWinner
     DetermineWinner : Find player with highest assets
     DetermineWinner : Highlight winner
     
     DetermineWinner --> DisplayResults
     DisplayResults : Show final standings
     DisplayResults : Display game statistics
     DisplayResults --> [*]
   }
   
   GameOver --> [*]

   @enduml 

Development Components
-----------

Development Notification UI
^^^^^^^^^^^^^^^^^

This diagram shows the development notification UI that appears when a player can develop a property:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam classBackgroundColor lightGray
   skinparam classBorderColor black
   skinparam arrowColor black
   
   class DevelopmentNotification {
     + screen: Surface
     + player_name: str
     + property_name: str
     + font: Font
     + buttons: Dict[str, Rect]
     + visible: bool
     + property_data: Dict
     + current_player: Dict
     
     + draw(mouse_pos)
     + check_button_click(pos)
     + show(property_data, player)
     + hide()
     + handle_development_action(action)
   }
   
   class Game {
     + development_notification: DevelopmentNotification
     + selected_property: Dict
     + current_player: Dict
     
     + draw_development_ui(property_data)
     + handle_development_click(pos, property_data)
     + can_develop_property(property_data, player)
     + process_development_action(action, property_data)
   }
   
   Game *-- DevelopmentNotification
   
   note right of DevelopmentNotification
     The DevelopmentNotification class:
     - Appears when a player can develop a property
     - Shows development options (build house/hotel)
     - Displays costs and benefits
     - Handles user interactions with development UI
   end note
   
   note right of Game
     The Game class:
     - Creates and manages the development notification
     - Determines when to show development options
     - Processes development actions
     - Updates game state based on development choices
   end note
   
   @enduml

Development UI Visual Layout
^^^^^^^^^^^^^^^^^

This diagram illustrates the visual layout of the development UI:

.. uml::

   @startuml
   skinparam backgroundColor white
   
   rectangle "Development UI" as DevUI #LightBlue {
     rectangle "Property Header" as Header #LightYellow {
       rectangle "Property Name" as PropName
       rectangle "Color Bar" as ColorBar
     }
     
     rectangle "Property Information" as PropInfo #White {
       rectangle "Owner" as Owner
       rectangle "Current Rent" as Rent
       rectangle "Development Level" as DevLevel
     }
     
     rectangle "Development Options" as DevOptions #LightGreen {
       rectangle "Build House" as BuildHouse
       rectangle "Build Hotel" as BuildHotel
       rectangle "Mortgage" as Mortgage
       rectangle "Sell Improvements" as SellImprove
     }
     
     rectangle "Cost Information" as CostInfo #LightCyan {
       rectangle "House Cost" as HouseCost
       rectangle "Hotel Cost" as HotelCost
       rectangle "Mortgage Value" as MortgageValue
       rectangle "Selling Value" as SellingValue
     }
     
     rectangle "Action Buttons" as ActionButtons #Pink {
       rectangle "Confirm" as Confirm
       rectangle "Cancel" as Cancel
     }
   }
   
   Header -[hidden]d-> PropInfo
   PropInfo -[hidden]d-> DevOptions
   DevOptions -[hidden]d-> CostInfo
   CostInfo -[hidden]d-> ActionButtons
   
   note right of Header
     Property header shows:
     - Property name
     - Color group indicator
   end note
   
   note right of PropInfo
     Property information shows:
     - Current owner
     - Current rent value
     - Current development level (houses/hotel)
   end note
   
   note right of DevOptions
     Development options:
     - Build house button (if eligible)
     - Build hotel button (if eligible)
     - Mortgage button (if no houses)
     - Sell improvements button (if developed)
   end note
   
   note right of CostInfo
     Cost information shows:
     - House cost: £X
     - Hotel cost: £X
     - Mortgage value: £X
     - Selling value: £X (half of cost)
   end note
   
   note right of ActionButtons
     Action buttons:
     - Confirm selected action
     - Cancel and close UI
   end note
   
   note bottom of DevUI
     <b>UI Behavior:</b>
     - Appears when player clicks on their owned property
     - Options are enabled/disabled based on eligibility
     - Costs are displayed for each action
     - Confirmation required for all actions
     - Provides visual feedback on hover/selection
   end note
   
   @enduml

Property Development UI Flow
^^^^^^^^^^^^^^^^^

This diagram illustrates the flow of the property development UI when a player clicks on an owned property:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black
   
   start
   
   :Player Clicks on Property;
   note right
     - Player selects a property on the board
     - System captures click coordinates
     - Transforms to board coordinates
   end note
   
   :Check Property Status;
   
   if (Property Owned?) then (yes)
     if (Owned by Current Player?) then (yes)
       :Check Development Eligibility;
       note right
         - Verify player has completed at least one lap
         - Check if player owns all properties in color group
         - Verify property is not mortgaged
       end note
       
       if (Can Develop?) then (yes)
         :Show Development UI;
         note right
           - Display property information
           - Show current development level
           - Present development options
           - Display costs and benefits
         end note
         
         :Display Development Options;
         note right
           - Build house option (if eligible)
           - Build hotel option (if eligible)
           - Mortgage option
           - Sell house/hotel option (if developed)
         end note
         
         if (Development Type?) then (Build House)
           :Check House Building Requirements;
           note right
             - Verify player has enough money
             - Check even development rule
             - Ensure houses are available in bank
           end note
           
           if (Can Build House?) then (yes)
             :Process House Building;
             note right
               - Deduct cost from player
               - Add house to property
               - Update rent values
               - Refresh visual display
               - Show confirmation message
             end note
           else (no)
             :Show Error Message;
             note right
               - Display reason for failure
               - Suggest alternative actions
               - Provide guidance on requirements
             end note
           endif
         else if (Build Hotel)
           :Check Hotel Building Requirements;
           note right
             - Verify property has 4 houses
             - Check player has enough money
             - Ensure hotels are available in bank
             - Verify even development across group
           end note
           
           if (Can Build Hotel?) then (yes)
             :Process Hotel Building;
             note right
               - Deduct cost from player
               - Replace 4 houses with hotel
               - Return houses to bank
               - Update rent values
               - Refresh visual display
               - Show confirmation message
             end note
           else (no)
             :Show Error Message;
           endif
         else if (Mortgage)
           :Process Mortgage;
           note right
             - Calculate mortgage value
             - Add funds to player
             - Mark property as mortgaged
             - Update visual display
             - Show confirmation message
           end note
         else if (Sell Improvements)
           :Process Improvement Sale;
           note right
             - Calculate sale value (half of cost)
             - Add funds to player
             - Remove house/hotel from property
             - Update rent values
             - Refresh visual display
             - Show confirmation message
           end note
         endif
       else (no)
         :Show Development Restrictions;
         note right
           - Display reason development is not allowed
           - Show requirements for development
           - Provide guidance on next steps
         end note
       endif
     else (no)
       :Show Property Information;
       note right
         - Display property details
         - Show owner information
         - Display current rent
         - Show development level
       end note
     endif
   else (no)
     :Show Property Information;
     note right
       - Display property details
       - Show purchase price
       - Display potential rent values
       - Offer purchase option if applicable
     end note
   endif
   
   :Close UI on User Action;
   
   stop
   
   @enduml

Game Components
-----------

Game Components
^^^^^^^^^^^^^^^^^

This diagram shows the main class structure of the game based on the actual code implementation:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam classBackgroundColor lightGray
   skinparam classBorderColor black
   skinparam arrowColor black

   class Game {
     + players: List[Player]
     + board: Board
     + current_player: Player
     + dice: Dice
     + cards: Dict[str, List[Card]]
     + game_mode: str
     + time_limit: int
     + ai_difficulty: str
     + bank_money: int
     + game_over: bool
     + winner_index: int
     + logic: GameLogic
     + auction_data: Dict
     + notification: Dict
     + popup_message: Dict
     + free_parking_pot: int
     + start()
     + draw()
     + play_turn()
     + handle_space(player)
     + handle_buy_decision(wants_to_buy)
     + start_auction(property_data)
     + handle_jail_turn(player)
     + move_player(player, spaces)
     + check_passing_go(player, old_position)
     + handle_ai_turn(ai_player)
     + check_game_over()
     + handle_bankruptcy(player)
     + calculate_player_assets(player)
     + draw_dice(dice1, dice2, is_rolling)
     + draw_property_card(property_data)
     + draw_auction(auction_data)
     + draw_jail_options(player)
     + draw_development_ui(property_data)
     + handle_card_action(card, player)
     + handle_fine_payment(player, amount, reason)
     + add_to_free_parking(amount)
     + collect_free_parking(player)
   }

   class Player {
     + name: str
     + player_number: int
     + is_ai: bool
     + money: int
     + properties: List[Property]
     + position: int
     + in_jail: bool
     + jail_turns: int
     + jail_cards: int
     + bankrupt: bool
     + voluntary_exit: bool
     + final_assets: int
     + color: Tuple[int, int, int]
     + player_image: Surface
     + is_moving: bool
     + move_progress: float
     + move_path: List[int]
     + is_active: bool
     + is_winner: bool
     + move(steps)
     + generate_move_path(steps)
     + is_animation_complete()
     + pay(amount)
     + receive(amount)
     + buy_property(property)
     + add_jail_card(card_type)
     + use_jail_card()
     + handle_jail_turn()
     + can_afford(amount)
     + add_property(property)
     + remove_property(property)
     + get_total_assets()
     + get_mortgageable_properties()
     + get_properties_with_houses()
     + get_properties_with_hotels()
     + can_build_houses()
     + can_build_hotels()
     + handle_bankruptcy(creditor)
     + handle_voluntary_exit()
     + draw_player(screen, x, y)
     + update_animation()
     + load_player_image()
     + create_fallback_token()
   }

   class Board {
     + players: List[Player]
     + spaces: List[Space]
     + properties_data: Dict
     + board_image: Surface
     + background_image: Surface
     + board_rects: List[Rect]
     + camera: CameraControls
     + messages: List[str]
     + message_times: List[int]
     + draw(screen)
     + update_board_positions()
     + draw_player(screen, player, rect, index)
     + get_space(position)
     + update_ownership(properties_data)
     + get_property_group(position)
     + get_property_position(position)
     + board_to_screen(x, y)
     + update_offset(dx, dy)
     + property_clicked(pos)
     + add_message(text)
   }

   class Property {
     + name: str
     + group: str
     + price: int
     + base_rent: int
     + owner: Player
     + houses: int
     + has_hotel: bool
     + house_costs: List[int]
     + is_station: bool
     + is_utility: bool
     + mortgaged: bool
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

   class GameLogic {
     + game: Game
     + ai_difficulty: str
     + ai_player: AIPlayer
     + property_data: Dict
     + card_data: Dict
     + game_start()
     + load_property_data()
     + load_card_data()
     + process_turn(player)
     + handle_property_space(player, property_data)
     + handle_card_space(player, card_type)
     + handle_tax_space(player, amount)
     + handle_jail_space(player)
     + handle_free_parking(player)
     + process_card_action(player, card)
     + check_bankruptcy(player, amount, creditor)
     + calculate_assets(player)
     + determine_winner()
   }

   class CameraControls {
     + zoom_level: float
     + offset_x: int
     + offset_y: int
     + move_speed: int
     + zoom_speed: float
     + min_zoom: float
     + max_zoom: float
     + handle_camera_controls(keys)
   }

   class Space {
     + name: str
     + position: int
     + type: str
     + action(player, game)
   }

   class Card {
     + type: str
     + description: str
     + action: str
     + action_value: int
     + execute(player, game)
   }

   class AIPlayer {
     + difficulty: str
     + evaluate_purchase(property, player, game)
     + decide_development(player, game)
     + handle_auction_bid(property, current_bid, player, game)
     + choose_jail_strategy(player, game)
     + evaluate_mortgage_options(player, amount_needed, game)
     + calculate_property_value(property, player, game)
     + determine_risk_level(player, game)
     + make_decision(options, player, game)
   }

   Game *-- Player
   Game *-- Board
   Game *-- GameLogic
   Game *-- Card
   Board *-- Space
   Board *-- CameraControls
   Board o-- Property
   Player o-- Property
   GameLogic o-- AIPlayer
   @enduml

Game Flow
^^^^^^^^^^^^^^^^^

The following flowchart shows the main game loop and turn sequence based on the actual code implementation:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black

   start
   :Initialize Game;
   note right
     - Create players with starting money (£1500)
     - Set up bank with initial money (£50000)
     - Load property data from Excel
     - Initialize board with 40 spaces
     - Set game mode (full/abridged)
     - Set AI difficulty (easy/hard)
   end note
   
   :Setup Board;
   note right
     - Create board layout with property positions
     - Initialize player tokens on board
     - Load board and background images
     - Set up camera controls for zoom/pan
   end note
   
   while (Game Not Over?) is (yes)
     :Get Current Player;
     note right
       - Track active player with visual highlight
       - Update player animation state
     end note
     
     if (Player in Jail?) then (yes)
       :Handle Jail Turn;
       note right
         - Check for jail cards
         - Offer options: pay £50, use card, roll for doubles
         - Track jail turns (max 3)
         - Update jail status
       end note
     else (no)
       if (Is AI Player?) then (yes)
         :Execute AI Logic;
         note right
           - Determine strategy based on difficulty
           - Evaluate property purchases
           - Make decisions on development
           - Handle auctions and trades
         end note
       else (no)
         :Wait for Player Input;
       endif
       
       :Roll Dice;
       note right
         - Generate two random numbers (1-6)
         - Display dice animation
         - Check for doubles
         - Handle triple doubles (go to jail)
       end note
       
       :Move Player;
       note right
         - Calculate path around board
         - Animate movement with smooth transitions
         - Check for passing GO (collect £200)
         - Update player position
       end note
       
       :Handle Space;
       note right
         - Get space type at player position
         - Process space-specific actions
       end note
     endif
     
     if (Land on Property?) then (yes)
       if (Property Owned?) then (yes)
         :Calculate Rent;
         note right
           - Check for monopoly (double rent)
           - Check for houses/hotels
           - Handle utilities (based on dice roll)
           - Handle stations (based on ownership count)
         end note
         
         :Pay Rent;
         note right
           - Transfer money from player to owner
           - Check for bankruptcy
           - Update player balances
         end note
       else (no)
         if (Can Afford?) then (yes)
           :Offer Purchase Option;
           note right
             - Display property card with details
             - Show buy/pass buttons
             - Wait for player decision
           end note
           
           if (Buy Property?) then (yes)
             :Purchase Property;
             note right
               - Transfer money to bank
               - Add property to player's portfolio
               - Update property ownership
               - Update board display
             end note
           else (no)
             :Start Auction;
             note right
               - Allow all players to bid
               - Track highest bidder
               - Handle auction timer
               - Award property to winner
             end note
           endif
         endif
       endif
     else (no)
       if (Special Space?) then (yes)
         if (Card Space?) then (yes)
           :Draw Card;
           note right
             - Get card from appropriate deck
             - Display card to player
             - Wait for acknowledgment
           end note
           
           :Execute Card Action;
           note right
             - Move player if required
             - Process money transactions
             - Handle jail cards
             - Apply special effects
           end note
         else if (Tax Space?) then (yes)
           :Pay Tax;
           note right
             - Deduct tax amount from player
             - Add to Free Parking pot if enabled
             - Check for bankruptcy
           end note
         else if (Go To Jail?) then (yes)
           :Send Player to Jail;
           note right
             - Move player to jail position
             - Set jail status
             - End current turn
           end note
         else if (Free Parking?) then (yes)
           :Collect Free Parking Money;
           note right
             - Add accumulated pot to player
             - Reset free parking pot
           end note
         endif
       endif
     endif
     
     :Check Player Status;
     if (Player Bankrupt?) then (yes)
       :Process Bankruptcy;
       note right
         - Transfer assets to creditor
         - Remove player from game
         - Update player list
       end note
     endif
     
     :Check Game End Conditions;
     note right
       - Check if only one player remains
       - Check time limit for abridged mode
       - Check for voluntary exits
     end note
     
     :End Turn;
     note right
       - Move to next player
       - Update game state
       - Refresh display
     end note
   endwhile (no)
   
   :Calculate Final Scores;
   note right
     - Add up property values
     - Count houses and hotels
     - Add cash on hand
     - Determine total assets
   end note
   
   :Declare Winner;
   note right
     - Highlight winning player
     - Display final standings
     - Show game statistics
   end note
   
   stop
   @enduml

Game Lap System
^^^^^^^^^^^^^^^^^

This diagram illustrates how the lap counter system integrates with game mechanics:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black
   
   start
   :Player Movement;
   
   if (Passes GO?) then (yes)
     :Increment Lap Counter;
     :Add Salary (£200);
     note right
       Tracked in completed_circuits dictionary
       by player name
     end note
   else (no)
     :Continue Movement;
   endif
   
   :Check Lap Status;
   
   if (First Lap Completed?) then (yes)
     :Unlock Development Features;
     note right
       Players can now:
       - Build houses/hotels
       - Participate in auctions
       - Trade properties
     end note
   else (no)
     :Limited Game Features;
     note right
       Restrictions until first lap:
       - No building houses/hotels
       - Limited auction participation
       - Basic property purchases only
     end note
   endif
   
   :Update UI Based on Lap Status;
   note right
     UI elements affected:
     - Development buttons enabled/disabled
     - Property cards show development options
     - Auction UI availability
   end note
   
   stop
   
   @enduml

Game Logic Flow
^^^^^^^^^^^^^^^^^

This diagram shows the core game logic and state management based on the actual code implementation:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black

   start
   :Initialize Game Logic;
   note right
     - Create GameLogic instance
     - Load property data from Excel
     - Load card data from Excel
     - Initialize game constants
     - Set up AI difficulty
     - Create appropriate AI strategy
   end note

   :Setup Game Environment;
   note right
     - Initialize pygame
     - Set up display window
     - Load fonts and UI elements
     - Initialize audio system
     - Set up camera controls
   end note

   :Create Game Objects;
   note right
     - Create player objects
     - Initialize board with spaces
     - Set up property data
     - Create card decks
     - Initialize bank with money
   end note

   while (Game Active?) is (yes)
     :Process Game Loop;
     note right
       - Handle events
       - Update game state
       - Render graphics
       - Manage timing
     end note
     
     :Handle Player Turn;
     
     if (Player Type?) then (AI)
       :Execute AI Logic;
       note right
         - Determine strategy based on difficulty
         - Analyze game state
         - Make property decisions
         - Handle development choices
         - Process auction bids
       end note
       
       :Apply AI Decisions;
       note right
         - Execute chosen actions
         - Update game state
         - Animate AI moves
         - Display AI decisions
       end note
     else (Human)
       :Process Player Input;
       note right
         - Handle keyboard commands
         - Process mouse clicks
         - Respond to UI interactions
         - Validate player actions
       end note
       
       :Execute Player Actions;
       note right
         - Roll dice
         - Move player token
         - Buy properties
         - Develop properties
         - Pay/collect money
       end note
     endif

     :Handle Space Actions;
     note right
       - Determine space type
       - Execute space-specific logic
       - Update player state
       - Process transactions
     end note
     
     if (Space Type?) then (Property)
       :Process Property Logic;
       note right
         - Check ownership status
         - Calculate rent if owned
         - Offer purchase if unowned
         - Handle auctions
         - Update property state
       end note
       
       if (Transaction?) then (yes)
         :Validate Transaction;
         note right
           - Check player funds
           - Verify transaction rules
           - Calculate final amounts
         end note
         
         if (Valid?) then (yes)
           :Process Money Transfer;
           note right
             - Update player balances
             - Transfer property ownership
             - Update UI displays
             - Check for bankruptcy
           end note
           
           :Update Bank Balance;
           note right
             - Adjust bank funds
             - Track transaction history
             - Update game economy
           end note
         else (no)
           :Handle Invalid Transaction;
           note right
             - Display error message
             - Offer alternatives
             - Revert to previous state
           end note
         endif
       endif
     else if (Card Space) then
       :Draw Card;
       note right
         - Select from appropriate deck
         - Display card to player
         - Process card action
       end note
     else if (Tax Space) then
       :Process Tax Payment;
       note right
         - Calculate tax amount
         - Deduct from player
         - Add to free parking pot
         - Check for bankruptcy
       end note
     else if (Jail Space) then
       :Handle Jail Logic;
       note right
         - Process jail entry/exit
         - Manage jail turns
         - Handle jail cards
         - Process jail payments
       end note
     else if (Free Parking) then
       :Award Free Parking Pot;
       note right
         - Transfer pot to player
         - Reset pot amount
         - Display notification
       end note
     else if (GO Space) then
       :Process GO Bonus;
       note right
         - Add salary amount
         - Update player balance
         - Display notification
       end note
     endif

     if (Property Action?) then (yes)
       :Handle Property Transaction;
       note right
         - Process buying/selling
         - Handle mortgaging
         - Manage development
         - Update property status
       end note
       
       if (Development?) then (yes)
         :Process Development;
         note right
           - Check monopoly ownership
           - Verify even development rule
           - Calculate development cost
           - Update property improvements
           - Update rent values
         end note
       else if (Mortgage?) then
         :Process Mortgage;
         note right
           - Calculate mortgage value
           - Add funds to player
           - Mark property as mortgaged
           - Update rent calculations
         end note
       else if (Unmortgage?) then
         :Process Unmortgage;
         note right
           - Calculate unmortgage cost
           - Deduct funds from player
           - Mark property as active
           - Restore rent calculations
         end note
       endif
     endif

     :Check Win Conditions;
     note right
       - Evaluate player statuses
       - Check bankruptcy conditions
       - Verify time limits
       - Assess victory conditions
     end note
     
     if (Game Mode?) then (Full)
       if (One Player Left?) then (yes)
         :End Game;
         note right
           - Declare winner
           - Calculate final scores
           - Display game statistics
           - Show victory screen
         end note
         stop
       endif
     else (Abridged)
       if (Time Limit Reached?) then (yes)
         :Calculate Final Assets;
         note right
           - Add property values
           - Count houses/hotels
           - Add cash on hand
           - Determine total worth
         end note
         
         :Determine Winner;
         note right
           - Compare player assets
           - Identify player with most assets
           - Handle tie conditions
           - Display final standings
         end note
         stop
       endif
     endif

     :Update Game State;
     note right
       - Refresh UI elements
       - Update animations
       - Process queued events
       - Prepare for next turn
     end note
     
     :Next Player Turn;
     note right
       - Move to next active player
       - Skip bankrupt players
       - Reset turn variables
       - Update active player highlight
     end note
   endwhile (no)

   :Game Cleanup;
   note right
     - Save game statistics
     - Release resources
     - Close file handles
     - Shut down systems
   end note
   
   stop
   @enduml

Jail Components
-----------

Jail System Flow
^^^^^^^^^^^^^^^^^

This diagram illustrates the jail system flow and player options when in jail:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black
   
   start
   
   :Player Enters Jail;
   note right
     Entry methods:
     - Landing on "Go To Jail" space
     - Drawing a "Go To Jail" card
     - Rolling three consecutive doubles
   end note
   
   :Set Player Jail Status;
   note right
     - Set player.in_jail = True
     - Set player.jail_turns = 0
     - Move player token to jail space
     - Update player animation state
     - Display jail notification
   end note
   
   while (Player in Jail?) is (yes)
     :Begin Player Turn in Jail;
     note right
       - Increment jail_turns counter
       - Display jail options to player
       - Disable normal movement
     end note
     
     :Present Jail Options;
     note right
       Available options:
       - Pay £50 fine to get out
       - Use "Get Out of Jail Free" card
       - Roll for doubles
     end note
     
     if (Player Choice?) then (Pay Fine)
       :Process Fine Payment;
       note right
         - Deduct £50 from player
         - Add to Free Parking pot (if enabled)
         - Set player.in_jail = False
         - Reset player.jail_turns = 0
       end note
     else if (Use Card)
       if (Has Jail Card?) then (yes)
         :Use Get Out of Jail Free Card;
         note right
           - Remove card from player inventory
           - Return card to appropriate deck
           - Set player.in_jail = False
           - Reset player.jail_turns = 0
         end note
       else (no)
         :Show Error - No Card Available;
         note right
           - Inform player they don't have a card
           - Return to jail options
         end note
       endif
     else if (Roll for Doubles)
       :Roll Dice;
       note right
         - Roll two dice
         - Check if dice values match (doubles)
       end note
       
       if (Rolled Doubles?) then (yes)
         :Release from Jail;
         note right
           - Set player.in_jail = False
           - Reset player.jail_turns = 0
           - Move player according to roll
           - Continue normal turn
         end note
       else (no)
         if (Jail Turns >= 3?) then (yes)
           :Force Payment After Third Turn;
           note right
             - Automatically deduct £50 fine
             - Set player.in_jail = False
             - Reset player.jail_turns = 0
             - End player's turn
           end note
         else (no)
           :Remain in Jail;
           note right
             - Keep player.in_jail = True
             - End player's turn
           end note
         endif
       endif
     endif
     
     if (Released from Jail?) then (yes)
       :Update Player Status;
       note right
         - Update player token position
         - Enable normal movement
         - Continue turn if applicable
       end note
     else (no)
       :End Turn While in Jail;
       note right
         - Player can still collect rent
         - Player can manage properties
         - Player can trade with others
       end note
     endif
   endwhile (no)
   
   :Resume Normal Play;
   
   stop
   
   @enduml

Jail UI Visual Layout
^^^^^^^^^^^^^^^^^

This diagram illustrates the visual layout of the jail UI when a player is in jail:

.. uml::

   @startuml
   skinparam backgroundColor white
   
   rectangle "Jail UI" as JailUI #LightBlue {
     rectangle "Jail Header" as JailHeader #LightYellow {
       rectangle "Jail Status" as JailStatus
       rectangle "Turn Counter" as TurnCounter
     }
     
     rectangle "Jail Information" as JailInfo #White {
       rectangle "Jail Rules" as JailRules
       rectangle "Player Status" as PlayerStatus
     }
     
     rectangle "Jail Options" as JailOptions #LightGreen {
       rectangle "Pay Fine Option" as PayFine
       rectangle "Use Card Option" as UseCard
       rectangle "Roll Doubles Option" as RollDoubles
     }
     
     rectangle "Dice Area" as DiceArea #LightCyan {
       rectangle "Dice Display" as DiceDisplay
       rectangle "Roll Result" as RollResult
     }
     
     rectangle "Action Buttons" as JailActionButtons #Pink {
       rectangle "Confirm Button" as ConfirmButton
       rectangle "Cancel Button" as CancelButton
     }
   }
   
   JailHeader -[hidden]d-> JailInfo
   JailInfo -[hidden]d-> JailOptions
   JailOptions -[hidden]d-> DiceArea
   DiceArea -[hidden]d-> JailActionButtons
   
   note right of JailHeader
     Jail header shows:
     - "IN JAIL" status indicator
     - Turn counter (e.g., "Turn 1 of 3")
     - Visual jail bars or icon
   end note
   
   note right of JailInfo
     Jail information shows:
     - Explanation of jail rules
     - Player's current status
     - Available options explanation
   end note
   
   note right of JailOptions
     Jail options show:
     - Pay £50 fine button
     - Use Get Out of Jail Free card button (if available)
     - Roll for doubles button
     - Each option has visual indicator of availability
   end note
   
   note right of DiceArea
     Dice area shows:
     - Dice animation when rolling
     - Result of dice roll
     - Visual indication if doubles were rolled
     - Success/failure message
   end note
   
   note right of JailActionButtons
     Action buttons:
     - Confirm selected option
     - Cancel and return to options
     - Buttons enabled/disabled based on context
   end note
   
   note bottom of JailUI
     <b>UI Behavior:</b>
     - Appears at start of turn when player is in jail
     - Options are enabled/disabled based on availability
     - Dice animation plays when rolling for doubles
     - Success/failure feedback is provided
     - UI updates to show remaining jail turns
     - Automatically closes when player is released
   end note
   
   @enduml

Player Components
-----------

Player Animation Implementation
^^^^^^^^^^^^^^^^^

This diagram shows the detailed implementation of the player animation system:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black
   
   start
   
   partition "Animation Initialization" {
     :Player Movement Triggered;
     note right
       Triggered by:
       - Dice roll
       - Card effect
       - Special event
     end note
     
     :Calculate Path;
     note right
       - Start position
       - End position
       - Intermediate spaces
       - Special spaces (GO, Jail)
     end note
     
     :Set Animation Parameters;
     note right
       - Animation duration
       - Movement speed
       - Visual effects
       - Sound effects
     end note
   }
   
   partition "Animation Execution" {
     :Start Animation Loop;
     
     while (Animation Complete?) is (no)
       :Calculate Current Position;
       note right
         - Interpolate between spaces
         - Apply easing function
         - Handle special cases
       end note
       
       :Update Visual State;
       note right
         - Update token position
         - Apply visual effects
         - Handle special animations
       end note
       
       :Check for GO Passing;
       
       if (Passing GO?) then (yes)
         :Trigger GO Animation;
         :Update Lap Counter;
         note right
           Increment completed_circuits
           for the player
         end note
         :Add Salary;
       endif
       
       :Render Frame;
       :Wait for Next Frame;
     endwhile (yes)
   }
   
   partition "Animation Completion" {
     :Finalize Position;
     note right
       - Snap to final position
       - Reset animation state
       - Update player data
     end note
     
     :Trigger Space Effect;
     note right
       - Property actions
       - Card draws
       - Special space effects
     end note
     
     :Update UI Elements;
     note right
       - Enable/disable buttons
       - Update property cards
       - Show relevant notifications
     end note
   }
   
   stop
   
   @enduml

Player Animation System
^^^^^^^^^^^^^^^^^

This diagram shows the player animation state machine and movement system:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam stateBorderColor black
   skinparam stateBackgroundColor lightGray
   skinparam arrowColor black
   
   state "Idle" as Idle
   state "Moving" as Moving {
     state "Path Calculation" as PC
     state "Animation Progress" as AP
     state "Position Update" as PU
     
     PC --> AP
     AP --> PU
     PU --> AP : next step
   }
   state "Action Animation" as Action {
     state "Jail" as Jail
     state "Bankrupt" as Bankrupt
     state "Celebration" as Celebration
     state "Property Purchase" as Purchase
   }
   state "Highlight" as Highlight
   
   [*] --> Idle
   Idle --> Moving : move command
   Moving --> Idle : animation complete
   Idle --> Action : special event
   Action --> Idle : animation complete
   Idle --> Highlight : turn active
   Highlight --> Idle : turn complete
   
   note right of Moving
     Movement animation includes:
     - Path calculation based on dice roll
     - Smooth transitions between spaces
     - Special animations for passing GO
     - Lap counter increment
   end note
   
   note right of Action
     Special animations triggered by:
     - Going to jail
     - Bankruptcy
     - Winning auctions
     - Building houses/hotels
   end note
   
   note right of Highlight
     Current player highlighting:
     - Pulsing glow effect
     - Color intensity changes
     - Token elevation
   end note
   
   @enduml

Player Flow
^^^^^^^^^^^^^^^^^

This diagram shows the player lifecycle and actions based on the actual code implementation:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black

   start
   :Initialize Player;
   note right
     - Set name and player_number
     - Set is_ai flag
     - Initialize money to £1500
     - Set position to 1 (GO)
     - Initialize properties list
     - Set jail status to false
     - Set jail_turns to 0
     - Set jail_cards to 0
     - Set bankrupt to false
     - Set color based on player type
     - Load player token image
   end note

   :Setup Player Animation;
   note right
     - Initialize animation parameters
     - Set up token appearance
     - Create fallback token if image not found
     - Set initial animation state
   end note

   while (Player Active?) is (yes)
     if (Is AI Player?) then (yes)
       :Execute AI Strategy;
       note right
         - Determine AI difficulty level
         - Evaluate property purchases
         - Calculate risk level
         - Make strategic decisions
         - Handle auction bidding
         - Manage property development
       end note
     else (no)
       :Wait for Player Input;
       note right
         - Process keyboard commands
         - Handle mouse clicks
         - Respond to UI interactions
         - Display relevant options
       end note
     endif

     if (In Jail?) then (yes)
       :Handle Jail Turn;
       note right
         - Display jail options
         - Track jail turn count
       end note
       
       if (Has Jail Card?) then (yes)
         if (Use Card Decision?) then (yes)
           :Use Jail Card;
           note right
             - Decrement jail_cards count
             - Return card to deck
             - Set in_jail to false
           end note
         endif
       else (no)
         if (Pay Fine Decision?) then (yes)
           :Pay £50 Fine;
           note right
             - Deduct money from player
             - Add to free parking pot if enabled
             - Set in_jail to false
           end note
         else (no)
           :Roll for Doubles;
           note right
             - Generate two dice values
             - Check if values match
           end note
           
           if (Rolled Doubles?) then (yes)
             :Free from Jail;
             note right
               - Set in_jail to false
               - Move according to dice roll
             end note
           else (no)
             :Increment Jail Turns;
             if (Jail Turns >= 3) then (yes)
               :Force Payment;
               note right
                 - Deduct £50 automatically
                 - Set in_jail to false
                 - Check for bankruptcy
               end note
             endif
           endif
         endif
       endif
     else (no)
       :Process Normal Turn;
       note right
         - Roll dice
         - Move player token
         - Handle space action
       end note
       
       :Animate Movement;
       note right
         - Generate movement path
         - Calculate animation frames
         - Update position progressively
         - Check for passing GO
       end note
       
       if (Passing GO?) then (yes)
         :Collect £200;
         note right
           - Add money to player balance
           - Display notification
           - Update money display
         end note
       endif
       
       if (On Property?) then (yes)
         if (Property Owned?) then (yes)
           if (Self-Owned?) then (yes)
             :No Action Required;
           else (no)
             :Calculate Rent;
             note right
               - Check for monopoly (double rent)
               - Check for houses/hotels
               - Apply special rules for utilities/stations
               - Calculate final amount
             end note
             
             :Pay Rent;
             note right
               - Transfer money to property owner
               - Update both players' balances
               - Display transaction notification
             end note
           endif
         else (no)
           if (Can Afford?) then (yes)
             :Display Property Card;
             note right
               - Show property details
               - Display purchase price
               - Show rent information
               - Present buy/pass options
             end note
             
             if (Buy Decision?) then (yes)
               :Buy Property;
               note right
                 - Deduct purchase price
                 - Add property to portfolio
                 - Update property ownership
                 - Update board display
               end note
             else (no)
               :Trigger Auction;
               note right
                 - Start bidding process
                 - Allow all players to participate
                 - Track highest bid
                 - Award to highest bidder
               end note
             endif
           endif
         endif
       else if (On Card Space?) then (yes)
         :Draw Card;
         note right
           - Get card from appropriate deck
           - Display card to player
           - Process card action
         end note
         
         :Execute Card Effect;
         note right
           - Move player if required
           - Process money transactions
           - Handle property effects
           - Apply special actions
         end note
       else if (On Tax Space?) then (yes)
         :Pay Tax;
         note right
           - Deduct tax amount
           - Add to free parking pot
           - Update player balance
         end note
       else if (On Go To Jail?) then (yes)
         :Move to Jail;
         note right
           - Set position to jail (10)
           - Set in_jail to true
           - End current turn
         end note
       else if (On Free Parking?) then (yes)
         :Collect Free Parking Pot;
         note right
           - Add pot amount to player
           - Reset free parking pot
           - Display notification
         end note
       endif
     endif
     
     :Update Player Animation;
     note right
       - Update highlight effects
       - Process bounce animation
       - Handle active player glow
       - Update token position
     end note
     
     :Check Financial Status;
     if (Bankrupt?) then (yes)
       :Process Bankruptcy;
       note right
         - Transfer assets to creditor
         - Remove properties from player
         - Set bankrupt flag to true
         - Remove from active players
       end note
       stop
     endif
     
     if (Voluntary Exit?) then (yes)
       :Handle Voluntary Exit;
       note right
         - Calculate final assets
         - Record exit statistics
         - Remove from active players
       end note
       stop
     endif

   endwhile (no)

   if (Game Over?) then (yes)
     :Calculate Final Assets;
     note right
       - Add up property values
       - Add house/hotel values
       - Add cash on hand
       - Calculate total net worth
     end note
     
     if (Is Winner?) then (yes)
       :Highlight as Winner;
       note right
         - Apply winner visual effects
         - Display congratulations
         - Show winning statistics
       end note
     endif
   endif

   stop
   @enduml

Turn Components
-----------

Turn Sequence
^^^^^^^^^^^^^^^^^

This sequence diagram shows the detailed flow of a player's turn based on the actual code implementation:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam sequenceParticipantBackgroundColor lightGray
   skinparam sequenceParticipantBorderColor black
   skinparam arrowColor black

   participant "Game" as Game
   participant "Player" as Player
   participant "Board" as Board
   participant "GameLogic" as Logic
   participant "Property" as Property
   participant "Space" as Space
   participant "Card" as Card
   participant "AIPlayer" as AI

   == Turn Initialization ==
   
   Game -> Game: play_turn()
   activate Game
   Game -> Player: set_active(true)
   activate Player
   Player --> Game: Update animation state
   
   alt Player is in Jail
       Game -> Game: handle_jail_turn(player)
       activate Game
       
       Game -> Player: Check jail status
       Player --> Game: Return jail_turns and jail_cards
       
       alt Has Jail Card
           Game -> Player: Offer to use jail card
           Player --> Game: Decision to use card
           
           opt Uses Jail Card
               Game -> Player: use_jail_card()
               Player --> Game: Update jail status
           end
       else No Jail Card
           Game -> Player: Offer options (pay fine/roll)
           Player --> Game: Decision
           
           alt Pay Fine
               Game -> Player: pay(50)
               Player --> Game: Update money
               Game -> Player: in_jail = False
           else Roll for Doubles
               Game -> Game: Roll dice
               
               alt Rolled Doubles
                   Game -> Player: in_jail = False
                   Game -> Game: Move player
               else No Doubles
                   Game -> Player: jail_turns += 1
                   
                   alt 3 Turns in Jail
                       Game -> Player: Force payment
                       Game -> Player: pay(50)
                       Game -> Player: in_jail = False
                   end
               end
           end
       end
       
       deactivate Game
   else Normal Turn
       alt Player is AI
           Game -> AI: handle_ai_turn(player)
           activate AI
           
           AI -> Logic: Evaluate game state
           Logic --> AI: Strategy recommendations
           
           AI -> Game: Make decisions
           Game --> AI: Execute actions
           
           deactivate AI
       else Human Player
           Game -> Game: Wait for player input
       end
       
       Game -> Game: Roll dice
       Game -> Game: Display dice animation
       Game -> Game: Check for triples (go to jail)
       
       alt Not Going to Jail
           Game -> Game: move_player(player, dice_total)
           activate Game
           
           Game -> Player: generate_move_path(steps)
           Player --> Game: Return path
           
           Game -> Board: Update player position
           Board --> Game: Animate movement
           
           Game -> Game: check_passing_go(player, old_position)
           opt Passing GO
               Game -> Player: receive(200)
               Game -> Board: add_message("Player collected £200")
           end
           
           Game -> Board: get_space(player.position)
           Board --> Game: Return space
           
           Game -> Game: handle_space(player)
           activate Game
           
           alt Property Space
               Game -> Logic: handle_property_space(player, property)
               activate Logic
               
               Logic -> Property: Get property details
               Property --> Logic: Return property data
               
               alt Property is Owned
                   Logic -> Property: calculate_rent(dice_roll, properties)
                   Property --> Logic: Return rent amount
                   
                   Logic -> Player: pay(rent)
                   Player --> Logic: Update money
                   
                   Logic -> Property: Get owner
                   Property --> Logic: Return owner
                   
                   Logic -> Property.owner: receive(rent)
                   
                   Logic -> Game: Check for bankruptcy
               else Property Not Owned
                   Logic -> Player: can_afford(price)
                   Player --> Logic: Return affordability
                   
                   alt Can Afford
                       Logic -> Game: Offer purchase
                       
                       alt Human Player
                           Game -> Game: draw_property_card(property)
                           Game -> Game: draw_buy_options()
                           Game -> Game: Wait for decision
                       else AI Player
                           Game -> AI: evaluate_purchase(property, player, game)
                           AI --> Game: Return decision
                       end
                       
                       alt Decides to Buy
                           Game -> Player: buy_property(property)
                           Player -> Player: pay(price)
                           Player -> Player: add_property(property)
                           Property -> Property: owner = player
                       else Decides Not to Buy
                           Game -> Game: start_auction(property)
                           
                           loop Until Auction Complete
                               Game -> Game: draw_auction(auction_data)
                               Game -> Game: handle_auction_input()
                               
                               alt AI Bidding
                                   Game -> AI: handle_auction_bid(property, current_bid, player, game)
                                   AI --> Game: Return bid amount
                               end
                           end
                           
                           alt Property Sold
                               Game -> Player: buy_property(property)
                               Player -> Player: pay(winning_bid)
                               Player -> Player: add_property(property)
                               Property -> Property: owner = player
                           end
                       end
                   end
               end
               
               deactivate Logic
           else Card Space
               Game -> Logic: handle_card_space(player, card_type)
               activate Logic
               
               Logic -> Card: Draw card
               Card --> Logic: Return card
               
               Logic -> Game: draw_card_alert(card, player)
               Game -> Game: Display card
               
               Logic -> Card: execute(player, game)
               Card -> Player: Apply card effect
               
               deactivate Logic
           else Tax Space
               Game -> Logic: handle_tax_space(player, amount)
               Logic -> Player: pay(amount)
               Logic -> Game: add_to_free_parking(amount)
           else Go To Jail
               Game -> Logic: handle_jail_space(player)
               Logic -> Player: position = 10
               Logic -> Player: in_jail = true
           else Free Parking
               Game -> Logic: handle_free_parking(player)
               Logic -> Game: collect_free_parking(player)
               Game -> Player: receive(free_parking_pot)
           end
           
           deactivate Game
           deactivate Game
       end
   end
   
   Game -> Game: check_game_over()
   
   alt Game Over
       Game -> Game: Calculate final scores
       Game -> Game: Determine winner
       Game -> Game: handle_game_over(winner)
   else Game Continues
       Game -> Player: set_active(false)
       Game -> Game: Move to next player
   end
   
   deactivate Player
   deactivate Game
   @enduml

UI Components
-----------

UI Component Hierarchy
^^^^^^^^^^^^^^^^^

This diagram shows the comprehensive hierarchy and relationships between all UI components:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam classBackgroundColor lightGray
   skinparam classBorderColor black
   skinparam arrowColor black
   
   ' Base classes
   abstract class BasePage {
     +screen
     +title_font
     +button_font
     +small_font
     +version_font
     +instructions
     +draw_background()
     +draw_title()
     +draw_instructions()
     +draw()
     +handle_click()
     +handle_motion()
     +handle_key()
   }
   
   class ModernButton {
     +rect
     +text
     +font
     +color
     +hover
     +active
     +is_selected
     +image
     +draw()
     +check_hover()
     -_draw_basic_button()
   }
   
   class ModernInput {
     +rect
     +text
     +font
     +active_color
     +inactive_color
     +active
     +cursor_visible
     +cursor_timer
     +draw()
     +handle_key_input()
   }
   
   ' UI Pages
   class MainMenuPage {
     +play_button
     +settings_button
     +how_to_play_button
     +exit_button
     +draw()
     +handle_click()
     +handle_motion()
     +handle_key()
   }
   
   class StartPage {
     +player_inputs
     +player_tokens
     +add_player_button
     +remove_player_button
     +start_button
     +back_button
     +player_list
     +ai_players
     +generate_unique_ai_name()
     +update_player_lists()
     +draw()
     +handle_click()
     +handle_motion()
     +handle_key()
     +get_player_info()
   }
   
   class GameModePage {
     +mode_buttons
     +time_limit_input
     +starting_money_input
     +salary_input
     +ai_difficulty
     +custom_settings
     +back_button
     +start_button
     +draw()
     +handle_click()
     +handle_motion()
     +handle_key()
     +get_game_settings()
   }
   
   class SettingsPage {
     +resolution_buttons
     +sound_buttons
     +back_button
     +save_button
     +confirmation_message
     +confirmation_timer
     +draw()
     +handle_click()
     +handle_motion()
     +handle_key()
     +get_settings()
   }
   
   class HowToPlayPage {
     +back_button
     +rules_text
     +draw()
     +handle_click()
     +handle_motion()
     +handle_key()
   }
   
   class EndGamePage {
     +winner_name
     +final_assets
     +bankrupted_players
     +voluntary_exits
     +tied_winners
     +lap_count
     +play_again_button
     +quit_button
     +confetti
     +draw()
     +handle_click()
     +handle_motion()
     +handle_key()
   }
   
   class AIDifficultyPage {
     +difficulty_buttons
     +back_button
     +confirm_button
     +draw()
     +handle_click()
     +handle_motion()
     +handle_key()
   }
   
   ' Game UI Components
   class DevelopmentNotification {
     +screen
     +player_name
     +font
     +property_name
     +buttons
     +visible
     +draw()
     +check_button_click()
   }
   
   ' Relationships
   BasePage <|-- MainMenuPage
   BasePage <|-- StartPage
   BasePage <|-- GameModePage
   BasePage <|-- SettingsPage
   BasePage <|-- HowToPlayPage
   BasePage <|-- EndGamePage
   BasePage <|-- AIDifficultyPage
   
   MainMenuPage --> ModernButton : uses
   StartPage --> ModernButton : uses
   StartPage --> ModernInput : uses
   GameModePage --> ModernButton : uses
   GameModePage --> ModernInput : uses
   SettingsPage --> ModernButton : uses
   HowToPlayPage --> ModernButton : uses
   EndGamePage --> ModernButton : uses
   AIDifficultyPage --> ModernButton : uses
   
   ' Navigation flow
   MainMenuPage ..> StartPage : navigates to
   MainMenuPage ..> SettingsPage : navigates to
   MainMenuPage ..> HowToPlayPage : navigates to
   
   StartPage ..> GameModePage : navigates to
   StartPage ..> MainMenuPage : navigates to
   
   GameModePage ..> AIDifficultyPage : navigates to
   GameModePage ..> StartPage : navigates to
   
   SettingsPage ..> MainMenuPage : navigates to
   HowToPlayPage ..> MainMenuPage : navigates to
   AIDifficultyPage ..> GameModePage : navigates to
   
   EndGamePage ..> MainMenuPage : navigates to
   
   @enduml

UI Layer Structure
^^^^^^^^^^^^^^^^^

This diagram shows the layered structure of the game UI:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam componentBackgroundColor lightGray
   skinparam componentBorderColor black
   skinparam arrowColor black
   
   package "UI Rendering Layers" {
     [Layer 1: Background] as L1
     [Layer 2: Game Board] as L2
     [Layer 3: Properties] as L3
     [Layer 4: Player Tokens] as L4
     [Layer 5: UI Elements] as L5
     [Layer 6: Notifications] as L6
     [Layer 7: Popups/Modals] as L7
   }
   
   note right of L1
     Background layer contains:
     - Background image or color
     - Decorative elements
     - Ambient animations
   end note
   
   note right of L2
     Game board layer contains:
     - Board image
     - Board spaces
     - Board decorations
     - Grid structure
   end note
   
   note right of L3
     Properties layer contains:
     - Property ownership indicators
     - Houses and hotels
     - Mortgaged indicators
   end note
   
   note right of L4
     Player tokens layer contains:
     - Player pieces
     - Movement animations
     - Highlight effects
     - Turn indicators
   end note
   
   note right of L5
     UI elements layer contains:
     - Buttons and controls
     - Player information panels
     - Game status displays
     - Action menus
   end note
   
   note right of L6
     Notifications layer contains:
     - Message notifications
     - Transaction alerts
     - Turn notifications
     - Event announcements
   end note
   
   note right of L7
     Popups/Modals layer contains:
     - Property cards
     - Card draws
     - Auction interface
     - Development interface
     - Dialog boxes
   end note
   
   L1 <-- L2 : renders on top
   L2 <-- L3 : renders on top
   L3 <-- L4 : renders on top
   L4 <-- L5 : renders on top
   L5 <-- L6 : renders on top
   L6 <-- L7 : renders on top
   
   @enduml

UI Layer Visual Representation
^^^^^^^^^^^^^^^^^

This diagram provides a visual representation of how the UI layers are stacked:

.. uml::

   @startuml
   skinparam backgroundColor white
   
   rectangle "Layer 7: Popups/Modals" as L7 #LightBlue {
     rectangle "Property Card" as PC
     rectangle "Auction Interface" as AI
     rectangle "Dialog Box" as DB
   }
   
   rectangle "Layer 6: Notifications" as L6 #LightGreen {
     rectangle "Message Notification" as MN
     rectangle "Turn Alert" as TA
   }
   
   rectangle "Layer 5: UI Elements" as L5 #LightYellow {
     rectangle "Buttons" as BT
     rectangle "Player Info Panel" as PIP
     rectangle "Game Status" as GS
   }
   
   rectangle "Layer 4: Player Tokens" as L4 #Pink {
     rectangle "Player 1" as P1
     rectangle "Player 2" as P2
     rectangle "Player 3" as P3
   }
   
   rectangle "Layer 3: Properties" as L3 #LightCyan {
     rectangle "Houses" as H
     rectangle "Hotels" as HT
     rectangle "Ownership Indicators" as OI
   }
   
   rectangle "Layer 2: Game Board" as L2 #LightGray {
     rectangle "Board Spaces" as BS
     rectangle "Board Grid" as BG
   }
   
   rectangle "Layer 1: Background" as L1 #White {
     rectangle "Background Image" as BI
     rectangle "Decorative Elements" as DE
   }
   
   L1 -[hidden]d-> L2
   L2 -[hidden]d-> L3
   L3 -[hidden]d-> L4
   L4 -[hidden]d-> L5
   L5 -[hidden]d-> L6
   L6 -[hidden]d-> L7
   
   note right of L7
     Top-most layer
     Handles modal dialogs and popups
   end note
   
   note right of L1
     Bottom-most layer
     Provides visual foundation
   end note
   
   note bottom of L1
     <b>Rendering Order:</b>
     Layers are rendered from bottom to top (Layer 1 → Layer 7)
     Each layer may contain multiple elements
     Elements within a layer have their own rendering order
     Transparency allows lower layers to be visible through upper layers
   end note
   
   @enduml

UI Page Navigation Flow
^^^^^^^^^^^^^^^^^

This diagram shows the navigation flow between different UI pages:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black
   
   start
   :Main Menu;
   
   fork
     :Settings;
     :Configure Resolution;
     :Configure Sound;
     :Configure Difficulty;
     :Save Settings;
     :Return to Main Menu;
   fork again
     :How To Play;
     :View Game Rules;
     :Return to Main Menu;
   fork again
     :Start Game;
     :Player Setup;
     note right
       - Add human players
       - Add AI players
       - Configure player tokens
       - Set player names
     end note
     
     :Game Mode Selection;
     note right
       - Standard mode
       - Abridged mode
       - Custom settings
       - AI difficulty
     end note
     
     :Game Play;
     note right
       Game loop with:
       - Player turns
       - Property management
       - Development (after first lap)
       - Trading
       - Special events
     end note
     
     :End Game;
     note right
       - Display winner
       - Show final assets
       - List bankrupted players
       - Show lap count
       - Offer replay option
     end note
     
     :Return to Main Menu;
   end fork
   
   stop
   
   @enduml 

EndGamePage Flow
^^^^^^^^^^^^^^^^^

This diagram illustrates the EndGamePage structure and how it displays game results including lap counts:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black
   
   start
   :Initialize EndGamePage;
   note right
     Parameters:
     - winner_name
     - final_assets
     - bankrupted_players
     - voluntary_exits
     - tied_winners
     - lap_count
   end note
   
   :Setup UI Elements;
   note right
     - Play Again button
     - Quit button
     - Confetti animation
   end note
   
   :Draw Background;
   
   :Draw Game Over Card;
   note right
     - Trophy graphic
     - Winner announcement
     - Tie handling
   end note
   
   :Display Final Assets;
   note right
     - Sorted by amount
     - Winner highlighted
     - Two-column layout
   end note
   
   if (Bankrupted Players?) then (yes)
     :Display Bankrupted Players;
   endif
   
   if (Voluntary Exits?) then (yes)
     :Display Voluntary Exits;
   endif
   
   if (Lap Count Available?) then (yes)
     :Display Lap Count Section;
     note right
       - Title "Laps Completed"
       - Sorted by number of laps
       - Multi-line if needed
     end note
   endif
   
   :Draw Action Buttons;
   
   :Handle User Input;
   
   if (Play Again Clicked?) then (yes)
     :Return to Main Menu;
   else (no)
     if (Quit Clicked?) then (yes)
       :Exit Game;
     endif
   endif
   
   stop
   
   @enduml

UI System Architecture
^^^^^^^^^^^^^^^^^

The following diagram illustrates the UI system architecture and component relationships:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam packageBackgroundColor lightGray
   skinparam componentBackgroundColor white
   skinparam componentBorderColor black
   skinparam arrowColor black
   
   package "UI Layer Structure" {
     [BasePage] as BP
     [MainMenuPage] as MMP
     [StartPage] as SP
     [GameModePage] as GMP
     [SettingsPage] as STP
     [HowToPlayPage] as HTP
     [EndGamePage] as EGP
     [AIDifficultyPage] as ADP
     
     BP <|-- MMP
     BP <|-- SP
     BP <|-- GMP
     BP <|-- STP
     BP <|-- HTP
     BP <|-- EGP
     BP <|-- ADP
   }
   
   package "UI Components" {
     [ModernButton] as MB
     [ModernInput] as MI
     [DevelopmentNotification] as DN
   }
   
   package "Game UI Elements" {
     [Board UI] as BUI
     [Player Tokens] as PT
     [Property Cards] as PC
     [Dice Animation] as DA
     [Development UI] as DUI
     [Auction UI] as AUI
   }
   
   package "Animation System" {
     [Player Movement] as PM
     [Animation State Machine] as ASM
     [Visual Effects] as VE
     [Transition Effects] as TE
   }
   
   package "Game State Management" {
     [Game Logic] as GL
     [Player State] as PS
     [Board State] as BS
     [Lap Counter] as LC
     [Property Ownership] as PO
   }
   
   ' Relationships
   BP --> MB : uses
   BP --> MI : uses
   
   GL --> LC : tracks
   GL --> PS : updates
   
   PS --> PM : controls
   PS --> PT : updates
   
   LC --> DUI : enables features
   LC --> AUI : enables features
   
   PM --> ASM : state transitions
   ASM --> VE : triggers
   
   ' UI Flow
   MMP --> SP : start game
   SP --> GMP : configure players
   GMP --> GL : initialize game
   STP --> GL : apply settings
   GL --> EGP : game over
   
   @enduml

UI Rendering Process
^^^^^^^^^^^^^^^^^

This diagram illustrates how the UI layers are rendered in each frame:

.. uml::

   @startuml
   skinparam backgroundColor white
   skinparam activityBorderColor black
   skinparam activityBackgroundColor lightGray
   skinparam arrowColor black
   
   start
   
   :Begin Frame Rendering;
   
   :Clear Screen;
   note right
     - Fill with background color
     - Reset drawing surface
   end note
   
   :Render Layer 1 - Background;
   note right
     - Draw background image
     - Apply any background effects
     - Render decorative elements
   end note
   
   :Apply Camera Transformations;
   note right
     - Apply zoom level
     - Apply camera offset
     - Set up coordinate system
   end note
   
   :Render Layer 2 - Game Board;
   note right
     - Draw board image
     - Apply board grid
     - Render board spaces
   end note
   
   :Render Layer 3 - Properties;
   note right
     - Draw property ownership indicators
     - Render houses and hotels
     - Show mortgaged properties
   end note
   
   :Render Layer 4 - Player Tokens;
   note right
     - Draw player pieces at current positions
     - Apply animation effects
     - Highlight active player
   end note
   
   :Reset Camera for UI;
   note right
     - Reset to screen coordinates
     - Disable camera transformations
     - Prepare for fixed UI elements
   end note
   
   :Render Layer 5 - UI Elements;
   note right
     - Draw buttons and controls
     - Render player information panels
     - Show game status displays
     - Draw action menus
   end note
   
   :Render Layer 6 - Notifications;
   note right
     - Display message notifications
     - Show transaction alerts
     - Render turn notifications
     - Draw event announcements
   end note
   
   :Render Layer 7 - Popups/Modals;
   note right
     - Draw property cards
     - Show card draws
     - Render auction interface
     - Display development interface
     - Show dialog boxes
   end note
   
   :Complete Frame Rendering;
   note right
     - Apply any post-processing effects
     - Swap display buffers
     - Present frame to screen
   end note
   
   stop
   
   @enduml