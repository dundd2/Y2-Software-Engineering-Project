# This is a demo planning python script based on eric's flowchart.drawio.png. 
# a coded version of flowchart.drawio.png. 
# All code from this file should now be copyed to use in different script files of the game. 
# This file is no longer needed, only as a progress of coding.

import random
import pandas as pd
from loadexcel import load_property_data
def game_start():
    """
    Starts the game and initializes players, bank, and loads property data from Excel.
    """
    print("Game Start")

    # Input the number of players (1-5)
    num_players = int(input("Input the number of players (1-5): "))
    players = []
    for i in range(num_players):
        #base on eric's flowchart:  let player choose a chess and input their name
        player_name = input(f"Player {i+1}, choose your chess and input your name: ")
        players.append({"name": player_name, "money": 1500, "position": 0}) # put all players on the "GO" and give each player $1500
    bank_money = 50000 # and set bank has $50,000

    properties_data = load_property_data() # Call the function from excel_loader

    if properties_data is None: # Check if loading failed
        return None, None, None # Indicate error in game start

    print("Game initialized with properties from Excel.")
    return players, bank_money, properties_data

def player_turn(players, bank_money, current_player_index, properties):
    current_player = players[current_player_index]
    print(f"\n{current_player['name']}'s turn.")

    # base on eric's flowchart: let player rolling the dices
    dice1 = random.randint(1, 6)
    dice2 = random.randint(1, 6)
    dice_sum = dice1 + dice2
    print(f"Dice roll: {dice1}, {dice2} (Sum: {dice_sum})")

    # base on eric's flowchart: after calculating the sum of the numbers thrown by the dices, let the player move clockwise
    current_player['position'] = (current_player['position'] + dice_sum) % 40
    print(f"{current_player['name']} moved to position {current_player['position']}")

    # base on eric's flowchart: player stop on the property
    player_stop_on(players, bank_money, current_player, properties)
    return players, bank_money

def player_stop_on(players, bank_money, current_player, properties):
    position = current_player['position']

    # Check space type based on properties data loaded from Excel
    if position in properties:
        space_info = properties[position]
        space_name = space_info['name']
        print(f"Player landed on: {space_name} (Position {position})")

        if "price" in space_info:
            print("Player stop on the property")
            property_actions(players, bank_money, current_player, position, properties)
        elif space_name == "Pot Luck" or space_name == "Opportunity Knocks":
            print("player stop on the lucky area / treasure area")
            lucky_treasure_actions(players, bank_money, current_player, space_name)
        elif space_name == "Go to Jail":
            print("player stop on the \"Go Jail\"")
            go_jail_actions(players, bank_money, current_player)
        elif space_name == "Free Parking":
            print("player stop on the free parking area")
            free_parking_actions(players, bank_money, current_player)
        elif space_name == "Go":
            print("Player stop on \"GO\"")
            # base on eric's flowchart: get $200 from bank
            current_player['money'] += 200
            bank_money -= 200
            print(f"{current_player['name']} gets $200 from bank. Current money: {current_player['money']}")
        elif space_name == "Income Tax" or space_name == "Super Tax":
            print("Player stop on Tax Space")
            tax_actions(players, bank_money, current_player, space_name)
        elif space_name == "Jail/Just visiting":
            print("Player stop on Jail/Just visiting")
        elif "Station" in space_name or "Utilities" in space_name:
             print("Player stop on Station or Utility")
             property_actions(players, bank_money, current_player, position, properties)

        else:
            print(f"No specific action defined for {space_name} yet.")
    else:
        print("Landed on an unknown space position:", position)

def property_actions(players, bank_money, current_player, property_position, properties):
    property = properties[property_position]
    print(f"{current_player['name']} landed on {property['name']}, Price: ${property['price']}")

    # base on eric's flowchart: if property has owner
    if property['owner']:
        print("if other players stop on your property")
        if property['owner'] != current_player['name']:
            # base on eric's flowchart: player need to pay rent to the owner(see property card)
            rent = property['rent']
            print(f"player need to pay rent to the owner(see property card), Rent: ${rent}")
            if current_player['money'] >= rent:
                current_player['money'] -= rent
                owner_player = next((player for player in players if player['name'] == property['owner']), None)
                if owner_player:
                    owner_player['money'] += rent
                print(f"{current_player['name']} paid ${rent} rent to {property['owner']}. Current money: {current_player['money']}")
            else:
                print(f"{current_player['name']} doesn't have enough money to pay rent.")
                # base on eric's flowchart: if player don't have enough money to pay
                # base on eric's flowchart: if players are short of cash, they can sell game assets (real estate, houses, hotels)
                mortgage_sell_assets()
                # base on eric's flowchart: can afford?
                if current_player['money'] >= rent:
                    current_player['money'] -= rent
                    owner_player = next((player for player in players if player['name'] == property['owner']), None)
                    if owner_player:
                        owner_player['money'] += rent
                    print(f"{current_player['name']} paid ${rent} rent to {property['owner']} after selling assets. Current money: ${current_player['money']}")
                else:
                    # base on eric's flowchart: Go bankrupt and exit the game, game pieces are removed
                    go_bankrupt(players, current_player_index)
        else:
            print("Player owns this property.")
    # base on eric's flowchart: if property has no owner
    else:
        # base on eric's flowchart: want to buy?
        want_to_buy = input("want to buy this property? (yes/no): ")
        if want_to_buy.lower() == 'yes':
            # base on eric's flowchart: have this player completed first round of chessboard? # Simplified: Assume yes for now
            # base on eric's flowchart: pay the property, and give the property card to player
            if current_player['money'] >= property['price']:
                current_player['money'] -= property['price']
                bank_money += property['price']
                property['owner'] = current_player['name']
                print(f"{current_player['name']} bought {property['name']} for ${property['price']}. Current money: ${current_player['money']}")
            else:
                print(f"{current_player['name']} does not have enough money to buy {property['name']}.")
                # base on eric's flowchart: not allow to buy this property
                print("not allow to buy this property")
                # base on eric's flowchart: return to the rolling process
        else:
            # base on eric's flowchart: the property will be auctioned
            print("the property will be auctioned")
            auction_property(players, bank_money, property)
 
pot_luck_cards = [
    {"text": "You inherit £200", "action": lambda player, bank, free_parking: (player['money'] + 200, bank - 200, free_parking)},
    {"text": "You have won 2nd prize in a beauty contest, collect £50", "action": lambda player, bank, free_parking: (player['money'] + 50, bank - 50, free_parking)},
    {"text": "You are up the creek with no paddle - go back to the Old Creek", "action": lambda player, bank, free_parking: (player['position'] -3 , bank, free_parking)}, # Assuming "Old Creek" is 3 spaces back, adjust as needed
    {"text": "Student loan refund. Collect £20", "action": lambda player, bank, free_parking: (player['money'] + 20, bank - 20, free_parking)},
    {"text": "Bank error in your favour. Collect £200", "action": lambda player, bank, free_parking: (player['money'] + 200, bank - 200, free_parking)},
    {"text": "Pay bill for text books of £100", "action": lambda player, bank, free_parking: (player['money'] - 100, bank + 100, free_parking)},
    {"text": "Mega late night taxi bill pay £50", "action": lambda player, bank, free_parking: (player['money'] - 50, bank + 50, free_parking)},
    {"text": "Advance to go", "action": lambda player, bank, free_parking: (0, bank, free_parking)},
    {"text": "From sale of Bitcoin you get £50", "action": lambda player, bank, free_parking: (player['money'] + 50, bank - 50, free_parking)},
    {"text": "Bitcoin assets fall - pay off Bitcoin short fall", "action": lambda player, bank, free_parking: (player['money'] - 50, bank + 50, free_parking)},
    {"text": "Pay a £10 fine or take opportunity knocks", "action": lambda player, bank, free_parking: (player['money'] - 10, bank + 10, free_parking + 10)}, # Player pays £10 on free parking
    {"text": "Pay insurance fee of £50", "action": lambda player, bank, free_parking: (player['money'] - 50, bank + 50, free_parking + 50)}, # Player puts £50 on free parking
    {"text": "Savings bond matures, collect £100", "action": lambda player, bank, free_parking: (player['money'] + 100, bank - 100, free_parking)},
    {"text": "Go to jail. Do not pass GO, do not collect £200", "action": lambda player, bank, free_parking: (10, bank, free_parking)}, # Move to jail position 10
    {"text": "Received interest on shares of £25", "action": lambda player, bank, free_parking: (player['money'] + 25, bank - 25, free_parking)},
    {"text": "It's your birthday. Collect £10 from each player", "action": lambda player, bank, free_parking: (player['money'] + sum(10 for p in players if p != player), bank - sum(10 for p in players if p != player) , free_parking)}, # Collect £10 from each other player
    {"text": "Get out of jail free", "action": lambda player, bank, free_parking: (player['money'], bank, free_parking)}, # Action for get out of jail free card (implementation needed)
]

opportunity_knocks_cards = [
    {"text": "Bank pays you divided of £50", "action": lambda player, bank, free_parking: (player['money'] + 50, bank - 50, free_parking)},
    {"text": "You have won a lip sync battle. Collect £100", "action": lambda player, bank, free_parking: (player['money'] + 100, bank - 100, free_parking)},
    {"text": "Advance to Turing Heights", "action": lambda player, bank, free_parking: (39, bank, free_parking)}, # Assuming Turing Heights is position 39, adjust as needed
    {"text": "Advance to Han Xin Gardens. If you pass GO, collect £200", "action": lambda player, bank, free_parking: (24 if player['position'] > 24 else player['money'] + 200, bank -200 if player['position'] > 24 else bank, free_parking)}, # Assuming Han Xin Gardens is position 24, adjust as needed
    {"text": "Fined £15 for speeding", "action": lambda player, bank, free_parking: (player['money'] - 15, bank + 15, free_parking + 15)}, # Player puts £15 on free parking
    {"text": "Pay university fees of £150", "action": lambda player, bank, free_parking: (player['money'] - 150, bank + 150, free_parking)},
    {"text": "Take a trip to Hove station. If you pass GO collect £200", "action": lambda player, bank, free_parking: (15 if player['position'] > 15 else player['money'] + 200, bank -200 if player['position'] > 15 else bank, free_parking)}, # Assuming Hove station is position 15, adjust as needed
    {"text": "Loan matures, collect £150", "action": lambda player, bank, free_parking: (player['money'] + 150, bank - 150, free_parking)},
    {"text": "You are assessed for repairs, £40/house, £115/hotel", "action": lambda player, bank, free_parking: (player['money'] - calculate_repair_cost(player, properties, 40, 115), bank + calculate_repair_cost(player, properties, 40, 115), free_parking)}, #Need a function to calculate repair cost
    {"text": "Advance to GO", "action": lambda player, bank, free_parking: (0, bank, free_parking)},
    {"text": "You are assessed for repairs, £25/house, £100/hotel", "action": lambda player, bank, free_parking: (player['money'] - calculate_repair_cost(player, properties, 25, 100), bank + calculate_repair_cost(player, properties, 25, 100), free_parking)}, #Need a function to calculate repair cost
    {"text": "Go back 3 spaces", "action": lambda player, bank, free_parking: (player['position'] - 3, bank, free_parking)},
    {"text": "Advance to Skywalker Drive. If you pass GO collect £200", "action": lambda player, bank, free_parking: (12 if player['position'] > 12 else player['money'] + 200, bank -200 if player['position'] > 12 else bank, free_parking)}, # Assuming Skywalker Drive is position 12, adjust as needed
    {"text": "Go to jail. Do not pass GO, do not collect £200", "action": lambda player, bank, free_parking: (10, bank, free_parking)}, # Move to jail position 10
    {"text": "Drunk in charge of a hoverboard. Fine £30", "action": lambda player, bank, free_parking: (player['money'] - 30, bank + 30, free_parking + 30)}, # Player puts £20 on free parking, should be £30 according to description, corrected to £30
    {"text": "Get out of jail free", "action": lambda player, bank, free_parking: (player['money'], bank, free_parking)}, # Action for get out of jail free card (implementation needed)
]

def calculate_repair_cost(player, properties, house_cost, hotel_cost):
    total_cost = 0
    for prop_position, prop_info in properties.items():
        if prop_info.get('owner') == player['name']:
            if prop_info.get('houses', 0) > 0 and prop_info.get('houses', 0) < 5: #houses
                total_cost += prop_info.get('houses', 0) * house_cost
            elif prop_info.get('houses', 0) == 5: #hotel is represented as 5 houses
                total_cost += hotel_cost
    return total_cost


def lucky_treasure_actions(players, bank_money, current_player, space_name):
    # base on eric's flowchart: player stop on the lucky area / treasure area
    # base on eric's flowchart: player need to take one card from the top of the lucky / treasure card
    print("player need to take one card from the top of the lucky / treasure card")
    global free_parking_fund
    if space_name == "Pot Luck":
        cards = pot_luck_cards
    elif space_name == "Opportunity Knocks":
        cards = opportunity_knocks_cards
    else:
        print("Unknown card space:", space_name)
        return

    card = random.choice(cards)
    print(f"Lucky card: {card['text']}")
    # base on eric's flowchart: execute the detail on the card what it says
    player_money, bank_money, free_parking_fund = card['action'](current_player, bank_money, free_parking_fund)
    current_player['money'] = player_money
    print(f"{current_player['name']}'s money is now ${current_player['money']}")

def go_jail_actions(players, bank_money, current_player):
    # base on eric's flowchart: player stop on the "Go Jail"
    # base on eric's flowchart: player will move to the Jail
    print("player will move to the Jail")
    current_player['position'] = 10
    print(f"{current_player['name']} is now in Jail.")
    # base on eric's flowchart: waiting and lose 2 round rolling dice times # Simplified jail time

def free_parking_actions(players, bank_money, current_player):
    # base on eric's flowchart: player stop on the free parking area
    # base on eric's flowchart: Receive all currently accumulated funds
    print("Receive all currently accumulated funds")
    global free_parking_fund
    current_player['money'] += free_parking_fund
    print(f"{current_player['name']} received ${free_parking_fund} from Free Parking. Current money: ${current_player['money']}")
    free_parking_fund = 0

def tax_actions(players, bank_money, current_player, space_name):
    # base on eric's flowchart: actions for tax spaces
    if space_name == "Income Tax":
        tax_amount = 200
    elif space_name == "Super Tax":
        tax_amount = 100
    else:
        tax_amount = 0
        print("Unknown tax space:", space_name)
        return

    if current_player['money'] >= tax_amount:
        current_player['money'] -= tax_amount
        bank_money += tax_amount
        print(f"{current_player['name']} paid ${tax_amount} for {space_name}. Current money: ${current_player['money']}")
    else:
        print(f"{current_player['name']} does not have enough money to pay {space_name} tax.")
        mortgage_sell_assets()
        if current_player['money'] >= tax_amount:
            current_player['money'] -= tax_amount
            bank_money += tax_amount
            print(f"{current_player['name']} paid ${tax_amount} for {space_name} after selling assets. Current money: ${current_player['money']}")
        else:
             go_bankrupt(players, current_player_index)

def building_process(players, bank_money, current_player, property):
    # base on eric's flowchart: building process
    # base on eric's flowchart: owner want to build house?
    print("building process")
    want_to_build = input("owner want to build house? (yes/no): ")
    if want_to_build.lower() == 'yes':
        # base on eric's flowchart: owner has a group color of the properties? # Simplified: Assume yes for now
        # base on eric's flowchart: if player has enough money to build
        house_cost = property['price'] // 2
        if current_player['money'] >= house_cost:
            current_player['money'] -= house_cost
            bank_money += house_cost
            property['houses'] = property.get('houses', 0) + 1
            property['rent'] *= 2
            print(f"{current_player['name']} built a house on {property['name']} for ${house_cost}. Current money: {current_player['money']}, Houses: {property['houses']}, Rent: ${property['rent']}")
            # base on eric's flowchart: return to the building process
            building_process(players, bank_money, current_player, property)
        else:
            print(f"{current_player['name']} does not have enough money to build a house.")
    else:
        # base on eric's flowchart: return to the rolling process
        print("no building are built")

def mortgage_sell_assets():
    # base on eric's flowchart: if players are short of cash, they can sell game assets (real estate, houses, hotels)
    print("if players are short of cash, they can sell game assets (real estate, houses, hotels)")
    print("mortgage_sell_assets - Implementation needed to handle selling assets and mortgages")

def go_bankrupt(players, current_player_index):
    # base on eric's flowchart: Go bankrupt and exit the game, game pieces are removed
    print("Go bankrupt and exit the game, game pieces are removed")
    player_name = players[current_player_index]['name']
    print(f"{player_name} went bankrupt and is out of the game.")
    del players[current_player_index]

def auction_property(players, bank_money, property):
    # base on eric's flowchart: auction process
    print("auction process")
    print(f"Auction for {property['name']} starts.")
    # base on eric's flowchart: if other player want this property?
    # base on eric's flowchart: The highest bidder will acquire the property

    auction_price = property['price'] // 2
    want_auction_buy = input(f"Buy {property['name']} at auction price ${auction_price}? (yes/no): ")
    if want_auction_buy.lower() == 'yes':
        current_player = players[current_player_index]
        if current_player['money'] >= auction_price:
            current_player['money'] -= auction_price
            bank_money += auction_price
            property['owner'] = current_player['name']
            print(f"{current_player['name']} bought {property['name']} at auction for ${auction_price}. Current money: ${current_player['money']}")
        else:
            print(f"{current_player['name']} does not have enough money to buy {property['name']} at auction price.")
            # base on eric's flowchart: this property will return to the bank
            print("this property will return to the bank")
            property['owner'] = None
    else:
        # base on eric's flowchart: this property will return to the bank
        print("this property will return to the bank")
        property['owner'] = None

    # base on eric's flowchart: Game Loop
if __name__ == "__main__":
    players, bank_money, properties = game_start()
    if players is None:
        exit()

    current_player_index = 0
    free_parking_fund = 0

    while len(players) > 1: # play continue the game
        players, bank_money = player_turn(players, bank_money, current_player_index, properties)
        if current_player_index >= len(players):
            current_player_index = 0
        else:
            current_player_index = (current_player_index + 1) % len(players)

    # base on eric's flowchart: if player can afford?
    if len(players) == 1:
        print(f"\n{players[0]['name']} wins the game!")
    else:
        print("\nGame over.")