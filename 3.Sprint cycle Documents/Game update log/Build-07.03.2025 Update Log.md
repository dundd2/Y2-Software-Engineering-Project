# Property Tycoon - Build-07.03.2025 Update Log

## Changes

- Ensure that when two players have the same amount of money at the end of an abridged game, the game correctly declares a tie instead of always making Player 1 the winner.  
- Implement keyboard input for time settings, allowing users to set custom values beyond just 10, 30, and 60 seconds, while keeping 30 seconds as the default. Added command-line output for debugging this feature.  
- Use the correct font for all in-game text.  
- Fixed the end-game functionality and improved the UI to display game laps.  

- Improved Github Folder Structure

**Documentation:**  
Added more flotchart for software documentation.

### To-Do

- Ensure the end-game screen appears when the timer reaches 0.  
- Fix the end-game screen so it correctly displays the amount of money each player has when the time limit expires (currently, it only shows 1500 for all players).  
- Improve the UI for bidding and getting out of jail, as they currently experience lag.  
- Investigate an unknown bug causing game lag. Consider adding a delay for AI player actions to prevent all processes from running simultaneously.  

### Known Bug (from Debugging)  

```python
Traceback (most recent call last):
  File "main.py", line 419, in <module>
  File "asyncio\runners.py", line 195, in run
  File "asyncio\runners.py", line 118, in run
  File "asyncio\base_events.py", line 725, in run_until_complete
  File "main.py", line 360, in main
  File "src\ui.py", line 710, in handle_key
AttributeError: module 'pygame' has no attribute 'K_H'. Did you mean: 'K_h'?
```

### Features to Add

- Implement a pause function for the game.  
- Improve the overall UI.  
- Debug and add unit tests, and create documentation for debugging.
