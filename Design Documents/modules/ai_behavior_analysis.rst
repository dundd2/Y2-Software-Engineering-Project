AI Behavior Analysis
====================

This document provides a detailed analysis of AI player behavior in different game scenarios, explaining the decision-making processes and strategies employed by both Easy and Hard AI players.

AI Decision Patterns
--------------------

AI players follow different decision-making patterns based on their difficulty level and game situation:

.. plantuml::

   @startuml
   
   title AI Decision Pattern Analysis
   
   start
   
   :Game Context Evaluation;
   note right
     AI analyzes:
     - Current board state
     - Player positions
     - Property ownership distribution
     - Available cash
   end note
   
   :Strategic Goal Selection;
   note right
     Prioritizes:
     1. Survival (avoid bankruptcy)
     2. Complete color groups
     3. Build developments
     4. Block opponents
   end note
   
   if (AI Type?) then (Easy AI)
     :Apply Simple Heuristics;
     :Use Fixed Thresholds;
   else (Hard AI)
     :Apply Complex Heuristics;
     :Use Dynamic Thresholds;
     :Apply Emotional Adjustments;
   endif
   
   :Execute Decision;
   
   stop
   
   @enduml

AI Auction Behavior
-------------------

The AI bidding strategy in auctions differs significantly between Easy and Hard difficulty levels:

.. plantuml::

   @startuml
   
   title AI Auction Bidding Strategy
   
   start
   
   :Property Up for Auction;
   
   :Calculate Base Property Value;
   note right
     Considers:
     - Base price
     - Group completion potential
     - Current ownership synergy
   end note
   
   if (AI Type?) then (Easy AI)
     :Apply Conservative Bid Ceiling;
     note right
       Maximum bid = min(
         property_value * 0.8,
         player_money * 0.7
))))))))))))))))))
     end note
     
     if (Current Bid > Max Bid?) then (Yes)
       :Pass;
     else (No)
       :Place Bid;
       note right
         bid = current_bid + 
         min(50, max(10, headroom * 0.2))
       end note
     endif
   else (Hard AI)
     :Apply Emotional Multiplier;
     note right
       multiplier = 1.0 + (mood_modifier * 1.5)
       affected_bid = base_bid * multiplier
     end note
     
     if (AI is Angry?) then (Yes)
       :May Bid Aggressively;
       note right
         Even if base valuation 
         suggests passing
       end note
     else if (AI is Happy?) then (Yes)
       :May Be Conservative;
       note right
         Might pass even on
         valuable properties
       end note
     endif
     
     if (Current Bid > Adjusted Max?) then (Yes)
       :Pass;
     else (No)
       :Place Emotionally Adjusted Bid;
     endif
   endif
   
   stop
   
   @enduml

AI Development Strategy
-----------------------

Property development decision-making follows a specific process based on available resources and group ownership:

.. plantuml::

   @startuml
   
   title AI Property Development Strategy
   
   start
   
   :Evaluate Financial Position;
   
   if (Money < Development Threshold?) then (Yes)
     :Skip Development;
     stop
   endif
   
   :Identify Complete Color Groups;
   
   partition "Development Prioritization" {
     :Sort Properties by Development ROI;
     note right
       ROI = potential_rent_increase / development_cost
     end note
     
     :Apply Even Development Strategy;
     note right
       Prefer to build houses evenly across 
       properties in a color group
     end note
}}}}}}}}
   
   if (AI Type?) then (Easy AI)
     if (ROI > Fixed Threshold?) then (Yes)
       :Approve Development;
     else (No)
       :Skip Development;
     endif
   else (Hard AI)
     :Apply Emotional Factor;
     note right
       Development threshold adjusted by mood:
       * Angry: Lower threshold (more development)
       * Happy: Higher threshold (less development)
     end note
     
     if (Adjusted ROI > Dynamic Threshold?) then (Yes)
       :Approve Development;
     else (No)
       if (Random < Emotion-based Chance?) then (Yes)
         :Approve Development Anyway;
         note right
           More likely if angry
         end note
       else (No)
         :Skip Development;
       endif
     endif
   endif
   
   stop
   
   @enduml

AI Emergency Cash Management
----------------------------

When facing financial difficulties, AI players employ different strategies to raise funds:

.. plantuml::

   @startuml
   
   title AI Emergency Cash Management
   
   start
   
   :Evaluate Cash Shortage;
   note right
     required_amount - available_cash
   end note
   
   if (Has Sufficient Cash?) then (Yes)
     :No Action Needed;
     stop
   endif
   
   partition "Liquidation Priority" {
     :1. Sell Houses from Non-Strategic Properties;
     :2. Mortgage Non-Group Properties;
     :3. Mortgage Properties in Incomplete Groups;
     :4. Sell Houses from Strategic Properties;
     :5. Mortgage Properties in Complete Groups;
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
   
   if (AI Type?) then (Easy AI)
     :Apply Fixed Liquidation Order;
   else (Hard AI)
     :Evaluate Strategic Value of Each Asset;
     note right
       Considers:
       - Immediate cash gain
       - Long-term revenue loss
       - Strategic position impact
     end note
     
     :Apply Emotional Risk Assessment;
     note right
       * Angry: May keep high-risk properties
       * Happy: More willing to sacrifice properties
     end note
   endif
   
   if (Can Raise Required Amount?) then (Yes)
     :Execute Liquidation Plan;
   else (No)
     :Prepare for Bankruptcy;
   endif
   
   stop
   
   @enduml

AI Jail Strategy
----------------

AI decision-making for jail scenarios depends on several factors including financial situation and game state:

.. plantuml::

   @startuml
   
   title AI Jail Strategy Decision Tree
   
   start
   
   if (Has Get Out of Jail Card?) then (Yes)
     :Use Card;
   else (No)
     partition "Evaluate Game Context" {
       :Assess Financial Position;
       :Check Dangerous Properties Ahead;
       :Evaluate Development Opportunities;
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
     
     if (AI Type?) then (Easy AI)
       if (Money > 250?) then (Yes)
         :Pay Fine;
       else (No)
         :Roll for Doubles;
       endif
     else (Hard AI)
       :Apply Emotional Context;
       
       if (AI is Angry?) then (Yes)
         if (Random < Adjusted Probability?) then (Yes)
           :Pay Fine Impulsively;
           note right
             Even if financially risky
           end note
         endif
       endif
       
       if (Board Analysis?) then (Dangerous Properties Ahead)
         :Roll for Doubles;
         note right
           Try to stay in jail to avoid
           expensive properties
         end note
       else (Safe or Opportunities Ahead)
         if (Money > 200?) then (Yes)
           :Pay Fine;
         else (No)
           :Roll for Doubles;
         endif
       endif
     endif
   endif
   
   stop
   
   @enduml

AI Trade Evaluation System
--------------------------

The AI uses a complex system to evaluate trade offers from other players:

.. plantuml::

   @startuml
   
   title AI Trade Evaluation System
   
   start
   
   :Receive Trade Offer;
   note right
     - Properties offered
     - Properties requested
     - Cash difference
   end note
   
   partition "Value Calculation" {
     :Calculate Value of Offered Properties;
     :Calculate Value of Requested Properties;
     :Add/Subtract Cash Difference;
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
   
   :Apply Strategic Multipliers;
   note right
     * Complete color group: 1.5x
     * Almost complete group: 1.3x
     * Station/utility synergy: 1.2x
   end note
   
   if (AI Type?) then (Easy AI)
     if (Value Difference > 0?) then (Yes)
       if (Random < 0.8) then (Yes)
         :Accept Trade;
       else (No)
         :Reject Trade;
         note right
           Adds unpredictability
         end note
       endif
     else (No)
       :Reject Trade;
     endif
   else (Hard AI)
     :Apply Emotional Assessment;
     note right
       * Angry: May reject profitable trades
       * Happy: May accept marginally unprofitable trades
     end note
     
     if (Adjusted Value Difference > 0?) then (Yes)
       :Accept Trade;
     else (No)
       if (Almost Balanced & Happy?) then (Yes)
         if (Random < Adjusted Probability) then (Yes)
           :Accept Slightly Unfavorable Trade;
         else (No)
           :Reject Trade;
         endif
       else (No)
         :Reject Trade;
       endif
     endif
   endif
   
   stop
   
   @enduml

Hard AI Mood Impact Analysis
----------------------------

This diagram provides a detailed analysis of how the Hard AI's mood impacts various game decisions:

.. plantuml::

   @startuml
   
   title Hard AI Mood Impact on Decision Making
   
   skinparam linetype ortho
   
   rectangle "Mood Range" {
     rectangle "Happy\n(-0.3)" as Happy
     rectangle "Slightly Happy\n(-0.15)" as SlightlyHappy
     rectangle "Neutral\n(0.0)" as Neutral
     rectangle "Slightly Angry\n(+0.15)" as SlightlyAngry
     rectangle "Angry\n(+0.3)" as Angry
     
     Happy -[hidden]right- SlightlyHappy
     SlightlyHappy -[hidden]right- Neutral
     Neutral -[hidden]right- SlightlyAngry
     SlightlyAngry -[hidden]right- Angry
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
   
   rectangle "Decision Adjustments" {
     rectangle "Property Valuation" as PropVal {
       text "Happy: -30% Value\nAngry: +30% Value"
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
     
     rectangle "Auction Bidding" as Auction {
       text "Happy: -30% Bid Ceiling\nAngry: +30% Bid Ceiling"
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
     
     rectangle "Development" as Dev {
       text "Happy: +30% ROI Threshold\nAngry: -30% ROI Threshold"
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
     
     rectangle "Risk Tolerance" as Risk {
       text "Happy: -30% Risk Taking\nAngry: +30% Risk Taking"
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
     
     rectangle "Trade Evaluation" as Trade {
       text "Happy: +15% Trade Acceptance\nAngry: -15% Trade Acceptance"
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
     
     PropVal -[hidden]down- Auction
     Auction -[hidden]down- Dev
     Dev -[hidden]down- Risk
     Risk -[hidden]down- Trade
}}}}}}}}}}}}}}}}}}}}}}}}}
   
   rectangle "Behavioral Outcomes" {
     rectangle "Conservative Play" as Conservative {
       text "- Lower bids\n- Fewer developments\n- More predictable"
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
     
     rectangle "Balanced Play" as Balanced {
       text "- Rational decisions\n- Optimal strategy\n- Predictable"
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
     
     rectangle "Aggressive Play" as Aggressive {
       text "- Higher bids\n- More developments\n- Less predictable"
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
     
     Conservative -[hidden]down- Balanced
     Balanced -[hidden]down- Aggressive
}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}
   
   Happy --> PropVal
   Happy --> Auction
   Happy --> Dev
   Happy --> Risk
   Happy --> Trade
   
   Angry --> PropVal
   Angry --> Auction
   Angry --> Dev
   Angry --> Risk
   Angry --> Trade
   
   Happy --> Conservative
   Neutral --> Balanced
   Angry --> Aggressive
   
   @enduml