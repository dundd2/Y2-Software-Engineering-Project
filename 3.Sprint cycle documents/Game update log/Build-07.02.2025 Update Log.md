# Property Tycoon - Build-07.02.2025 Update Log

## Property Tycoon - Build-06.03.2025 Update Log

## Changes

- Added initial game structure with Player, Game, Property, Board, and UI classes
- Special thanks to Owen for his fantastic work!

After receiving Owen's work, which included the basic CMD Python code file:

1. Duncan Transformed it into a Pygame game with a basic user interface
2. Fixed some minor bugs
3. Separated the different classes into their own .py files
   - The main.py file can now access other Python files since they are all in the same folder

## Current Features

We've already developed this pretty cool basic game.

The current game flow is:

1. **Start Page**
2. **Rolling**
3. **Moving**
4. **Property Interaction**
   - If the player lands on an unowned property, they get the option to buy it (Y/N keys).
   - If the player lands on an owned property, they pay rent to the owner.
5. **Turn End**: The turn passes to the next player.
6. **Jail**:
   - If player is in jail, increase jail turns
   - If turns are more than 3, player is released from jail
7. **Game End**: The game ends when a player runs out of money.

**Note:** Currently, the dice are not visible in the interface.

## Known Issues / Future Enhancements

- No Win Condition
- Limited Jail Functionality
- No Property Management
- Basic UI: The user interface is functional but very simple
- No AI Players
- No Double Roll
- No Cards
