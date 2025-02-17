# Base on PropertyTycoonCardData.xlsx from canvas 
# script based on Eric's provided flowchart photo (flowchart.drawio.png)
# will add more comment later to reference for which part of code is based on which part of the flowchart
import random
import pygame
from loadexcel import load_property_data

pot_luck_cards = [
    {"text": "You inherit £200", "action": lambda player, bank, free_parking: (player['money'] + 200, bank - 200, free_parking)},
    {"text": "You have won 2nd prize in a beauty contest, collect £50", "action": lambda player, bank, free_parking: (player['money'] + 50, bank - 50, free_parking)},
    {"text": "You are up the creek with no paddle - go back to the Old Creek", "action": lambda player, bank, free_parking: (2, bank, free_parking)},
    {"text": "Student loan refund. Collect £20", "action": lambda player, bank, free_parking: (player['money'] + 20, bank - 20, free_parking)},
    {"text": "Bank error in your favour. Collect £200", "action": lambda player, bank, free_parking: (player['money'] + 200, bank - 200, free_parking)},
    {"text": "Pay bill for text books of £100", "action": lambda player, bank, free_parking: (player['money'] - 100, bank + 100, free_parking)},
    {"text": "Mega late night taxi bill pay £50", "action": lambda player, bank, free_parking: (player['money'] - 50, bank + 50, free_parking)},
    {"text": "Advance to go", "action": lambda player, bank, free_parking: (1, bank, free_parking)},
    {"text": "From sale of Bitcoin you get £50", "action": lambda player, bank, free_parking: (player['money'] + 50, bank - 50, free_parking)},
    {"text": "Bitcoin assets fall - pay off Bitcoin short fall", "action": lambda player, bank, free_parking: (player['money'] - 50, bank + 50, free_parking)},
    {"text": "Pay a £10 fine or take opportunity knocks", "action": lambda player, bank, free_parking: (player['money'] - 10, bank + 10, free_parking + 10)},
    {"text": "Pay insurance fee of £50", "action": lambda player, bank, free_parking: (player['money'] - 50, bank + 50, free_parking + 50)},
    {"text": "Savings bond matures, collect £100", "action": lambda player, bank, free_parking: (player['money'] + 100, bank - 100, free_parking)},
    {"text": "Go to jail. Do not pass GO, do not collect £200", "action": lambda player, bank, free_parking: (11, bank, free_parking)},
    {"text": "Received interest on shares of £25", "action": lambda player, bank, free_parking: (player['money'] + 25, bank - 25, free_parking)},
    {"text": "It's your birthday. Collect £10 from each player", "action": lambda player, bank, free_parking: (player['money'] + 10, bank - 10, free_parking)},
    {"text": "Get out of jail free", "action": lambda player, bank, free_parking: (player['position'], bank, free_parking)},
]

opportunity_knocks_cards = [
    {"text": "Bank pays you divided of £50", "action": lambda player, bank, free_parking: (player['money'] + 50, bank - 50, free_parking)},
    {"text": "You have won a lip sync battle. Collect £100", "action": lambda player, bank, free_parking: (player['money'] + 100, bank - 100, free_parking)},
    {"text": "Advance to Turing Heights", "action": lambda player, bank, free_parking: (40, bank, free_parking)},
    {"text": "Advance to Han Xin Gardens", "action": lambda player, bank, free_parking: (25, bank + (200 if player['position'] > 25 else 0), free_parking)},
    {"text": "Fined £15 for speeding", "action": lambda player, bank, free_parking: (player['money'] - 15, bank + 15, free_parking + 15)},
    {"text": "Pay university fees of £150", "action": lambda player, bank, free_parking: (player['money'] - 150, bank + 150, free_parking)},
    {"text": "Take a trip to Hove station", "action": lambda player, bank, free_parking: (16, bank + (200 if player['position'] > 16 else 0), free_parking)},
    {"text": "Loan matures, collect £150", "action": lambda player, bank, free_parking: (player['money'] + 150, bank - 150, free_parking)},
    {"text": "You are assessed for repairs, £40/house, £115/hotel", "action": lambda player, bank, free_parking, game: (player['money'] - game.calculate_repair_cost(player, 40, 115), bank + game.calculate_repair_cost(player, 40, 115), free_parking)},
    {"text": "Advance to GO", "action": lambda player, bank, free_parking: (1, bank, free_parking)},
    {"text": "You are assessed for repairs, £25/house, £100/hotel", "action": lambda player, bank, free_parking, game: (player['money'] - game.calculate_repair_cost(player, 25, 100), bank + game.calculate_repair_cost(player, 25, 100), free_parking)},
    {"text": "Go back 3 spaces", "action": lambda player, bank, free_parking: (((player['position'] - 1 - 3) % 40) + 1, bank, free_parking)},
    {"text": "Advance to Skywalker Drive", "action": lambda player, bank, free_parking: (12, bank + (200 if player['position'] > 12 else 0), free_parking)},
    {"text": "Go to jail. Do not pass GO, do not collect £200", "action": lambda player, bank, free_parking: (11, bank, free_parking)},
    {"text": "Drunk in charge of a hoverboard. Fine £30", "action": lambda player, bank, free_parking: (player['money'] - 30, bank + 30, free_parking + 30)},
    {"text": "Get out of jail free", "action": lambda player, bank, free_parking: (player['position'], bank, free_parking)},
]

class GameLogic:
    def __init__(self):
        self.players = []
        self.bank_money = 50000
        self.free_parking_fund = 0
        self.current_player_index = 0
        self.properties = load_property_data()
        self.is_going_to_jail = False
        self.last_dice_roll = None
        self.doubles_count = 0
        self.message_queue = []
        self.bankrupted_players = []
        self.voluntary_exits = []
        self.jail_free_cards = {}  

    def game_start(self):
        self.properties = load_property_data()
        if self.properties is None:
            return False
        return True

    def add_player(self, name):
        if len(self.players) < 5:
            self.players.append({
                "name": name,
                "money": 1500,
                "position": 1
            })
            return True
        return False

    def play_turn(self):
        if not self.players:
            return None, None

        current_player = self.players[self.current_player_index]
        self.is_going_to_jail = False

        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        self.last_dice_roll = (dice1, dice2)

        if current_player.get('in_jail', False):
            success, message = self.try_leave_jail(current_player, dice1, dice2)
            if not success:
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
                return dice1, dice2

        if dice1 == dice2:
            self.doubles_count += 1
            if self.doubles_count == 3:
                print(f"{current_player['name']} rolled three doubles and goes to jail!")
                self.handle_jail(current_player)
                self.current_player_index = (self.current_player_index + 1) % len(self.players)
                return dice1, dice2
        else:
            self.doubles_count = 0

        old_pos = current_player['position']
        current_player['position'] = ((current_player['position'] - 1 + dice1 + dice2) % 40) + 1

        if current_player['position'] < old_pos and not self.is_going_to_jail:
            current_player["money"] += 200
            self.bank_money -= 200
            print(f"{current_player['name']} collected £200 for passing GO")

        result, message = self.handle_space(current_player)
        if result == "bankrupt":
            print(f"{current_player['name']} is bankrupt!")
        elif result == "jail":
            self.doubles_count = 0

        if not dice1 == dice2 or self.is_going_to_jail:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            self.doubles_count = 0

        return dice1, dice2

    def add_message(self, message):
        self.message_queue.append(message)

    def handle_space(self, player):
        position = str(player['position'])
        if position not in self.properties:
            return None, None

        space = self.properties[position]
        message = None

        if space["name"] == "Go to Jail":
            message = "Go to Jail. Do not pass GO, do not collect £200"
            self.add_message(message)
            return "jail", message

        if "price" in space:
            if space["owner"] is None and not player.get('in_jail', False):
                self.add_message(f"Would you like to buy {space['name']} for £{space['price']}?")
                return "can_buy", None
            elif space["owner"] != player["name"]:
                rent = self.calculate_space_rent(space, player)
                if player["money"] >= rent:
                    player["money"] -= rent
                    owner = next(p for p in self.players if p["name"] == space["owner"])
                    owner["money"] += rent
                    message = f"{player['name']} paid £{rent} rent to {owner['name']}"
                    self.add_message(message)
                else:
                    message = f"{player['name']} went bankrupt!"
                    self.add_message(message)
                    self.remove_player(player['name'])
                    return "bankrupt", message

        elif space["name"] == "Go":
            player["money"] += 200
            self.bank_money -= 200
            message = f"{player['name']} collected £200 for landing on GO"
            self.add_message(message)

        elif space["name"] in ["Income Tax", "Super Tax"]:
            tax = 200 if space["name"] == "Income Tax" else 100
            if player["money"] >= tax:
                player["money"] -= tax
                self.bank_money += tax
                message = f"{player['name']} paid £{tax} {space['name']}"
                self.add_message(message)
            else:
                message = f"{player['name']} went bankrupt!"
                self.add_message(message)
                self.remove_player(player['name'])
                return "bankrupt", message

        elif space["name"] in ["Pot Luck", "Opportunity Knocks"]:
            self.add_message(f"{player['name']} landed on {space['name']}")
            result, message = self.handle_card_draw(player, space["name"])
            if message:
                self.add_message(message)
            return result, message

        return None, message

    def handle_jail(self, player):
        player['position'] = 11
        player['in_jail'] = True
        player['jail_turns'] = 0
        self.is_going_to_jail = True
        self.doubles_count = 0
        self.add_message("Go to jail. Do not pass GO, do not collect £200")
        return "Go to jail. Do not pass GO, do not collect £200"

    def try_leave_jail(self, player, dice1, dice2):
        if not player.get('in_jail', False):
            return True, None

        player['jail_turns'] = player.get('jail_turns', 0) + 1

        if self.jail_free_cards.get(player['name'], 0) > 0:
            self.jail_free_cards[player['name']] -= 1
            player['in_jail'] = False
            player['jail_turns'] = 0
            message = f"{player['name']} uses Get Out of Jail Free card!"
            self.add_message(message)
            return True, message

        if dice1 == dice2:
            player['in_jail'] = False
            player['jail_turns'] = 0
            self.add_message(f"{player['name']} rolled doubles and left jail!")
            return True, f"{player['name']} rolled doubles and left jail!"

        if player['jail_turns'] >= 3 or player['money'] >= 50:
            message = ""
            if player['jail_turns'] >= 3:
                message = f"{player['name']} must leave jail after 3 turns"
            else:
                player['money'] -= 50
                self.bank_money += 50
                message = f"{player['name']} paid £50 to leave jail"
            player['in_jail'] = False
            player['jail_turns'] = 0
            self.add_message(message)
            return True, message

        message = f"{player['name']} stays in jail"
        self.add_message(message)
        return False, message

    def calculate_space_rent(self, space, player):
        if "Station" in space["name"]:
            station_count = sum(1 for prop in self.properties.values()
                              if "Station" in prop.get("name", "")
                              and prop.get("owner") == space["owner"])
            return 25 * (2 ** (station_count - 1))
        elif space["name"] in ["Tesla Power Co", "Edison Water"]:
            utility_count = sum(1 for prop in self.properties.values()
                              if prop.get("name") in ["Tesla Power Co", "Edison Water"]
                              and prop.get("owner") == space["owner"])
            dice_total = sum(self.last_dice_roll) if hasattr(self, 'last_dice_roll') else 7
            return dice_total * (10 if utility_count > 1 else 4)
        else:
            return space.get("rent", 0)

    def handle_card_draw(self, player, card_type):
        cards = pot_luck_cards if card_type == "Pot Luck" else opportunity_knocks_cards
        card = random.choice(cards)
        message = card['text']
        self.add_message(message)

        if message == "Get out of jail free":
            self.jail_free_cards[player['name']] = self.jail_free_cards.get(player['name'], 0) + 1
            return None, message

        try:
            new_pos, new_bank, new_parking = card["action"](player, self.bank_money, self.free_parking_fund, self)
        except TypeError:
            new_pos, new_bank, new_parking = card["action"](player, self.bank_money, self.free_parking_fund)

        if isinstance(new_pos, int):
            old_pos = player["position"]
            player["position"] = new_pos
            if new_pos < old_pos and new_pos != 11:
                player["money"] += 200
                self.bank_money -= 200
                self.add_message("Collected £200 for passing GO")
        else:
            player["money"] = new_pos
        self.bank_money = new_bank
        self.free_parking_fund = new_parking

        return None, message

    def calculate_repair_cost(self, player, house_cost, hotel_cost):
        total_cost = 0
        for prop in self.properties.values():
            if prop.get("owner") == player["name"]:
                houses = prop.get("houses", 0)
                if houses == 5:
                    total_cost += hotel_cost
                else:
                    total_cost += houses * house_cost
        return total_cost

    def check_property_group_completion(self, player_name):
        groups = {}
        for prop in self.properties.values():
            if prop.get('group') and prop.get('owner') == player_name:
                groups[prop['group']] = groups.get(prop['group'], 0) + 1

        group_totals = {}
        for prop in self.properties.values():
            if prop.get('group'):
                group_totals[prop['group']] = group_totals.get(prop['group'], 0) + 1

        for group, count in groups.items():
            if count == group_totals[group]:
                self.add_message(f"🎊 MONOPOLY! 🎊")
                self.add_message(f"{player_name} completed the {group} set!")
                self.add_message(f"Houses can now be built on these properties!")

    def buy_property(self, player):
        if player.get('in_jail', False):
            self.add_message(f"{player['name']} cannot buy property while in jail")
            return False
            
        position = str(player["position"])
        property_data = self.properties[position]

        if player["money"] >= property_data["price"]:
            player["money"] -= property_data["price"]
            self.bank_money += property_data["price"]
            property_data["owner"] = player["name"]
            self.check_property_group_completion(player["name"])
            return True
        return False

    def auction_property(self, position):
        position = str(position)
        property_data = self.properties[position]
        
        eligible_players = [p for p in self.players 
                          if p['money'] >= property_data["price"] // 2 
                          and not p.get('in_jail', False)]
        
        if not eligible_players:
            property_data['owner'] = None
            return "auction_completed"
        
        starting_bid = property_data["price"] // 2
        
        self.current_auction = {
            "property": property_data,
            "current_bid": 0,
            "minimum_bid": starting_bid,
            "highest_bidder": None,
            "start_time": pygame.time.get_ticks(),
            "duration": 30000,
            "passed_players": set(),
            "completed": False,
            "current_bidder_index": 0,
            "active_players": eligible_players,
            "message": f"Auction started for {property_data['name']} - Starting bid: £{starting_bid}"
        }
        
        return "auction_in_progress"

    def process_auction_bid(self, player, bid_amount):
        if not hasattr(self, 'current_auction') or self.current_auction["completed"]:
            return False, "Auction is not active"
            
        if player['name'] in self.current_auction["passed_players"]:
            return False, "You have already passed on this auction"
            
        if bid_amount < self.current_auction["minimum_bid"]:
            return False, f"Bid must be at least £{self.current_auction['minimum_bid']}"
            
        if bid_amount > player['money']:
            return False, "You don't have enough money"
            
        current_time = pygame.time.get_ticks()
        remaining_time = max(0, self.current_auction["start_time"] + self.current_auction["duration"] - current_time)
        if remaining_time <= 0:
            self.current_auction["passed_players"].add(player['name'])
            return False, f"{player['name']} took too long to bid - automatically passed"
            
        self.current_auction["current_bid"] = bid_amount
        self.current_auction["highest_bidder"] = player
        self.current_auction["minimum_bid"] = bid_amount + 10
        
        self.move_to_next_bidder()
        return True, f"{player['name']} bids £{bid_amount}"

    def process_auction_pass(self, player):
        if not hasattr(self, 'current_auction') or self.current_auction["completed"]:
            return False, "Auction is not active"
            
        self.current_auction["passed_players"].add(player['name'])
        
        self.move_to_next_bidder()
        return True, f"{player['name']} passes on the auction"

    def move_to_next_bidder(self):
        if not hasattr(self, 'current_auction'):
            return
            
        active_players = [p for p in self.current_auction["active_players"] 
                         if p['name'] not in self.current_auction["passed_players"]
                         and p['money'] >= self.current_auction["minimum_bid"]]
                         
        if len(active_players) <= 1 and self.current_auction["highest_bidder"]:
            self.current_auction["completed"] = True
            return
            
        current_index = self.current_auction["current_bidder_index"]
        next_index = (current_index + 1) % len(self.current_auction["active_players"])
        
        self.current_auction["current_bidder_index"] = next_index
        self.current_auction["start_time"] = pygame.time.get_ticks()

    def check_auction_end(self):
        if not hasattr(self, 'current_auction') or self.current_auction["completed"]:
            return None
            
        current_time = pygame.time.get_ticks()
        time_remaining = max(0, (self.current_auction["start_time"] + self.current_auction["duration"] - current_time) // 1000)
        
        active_players = [p for p in self.current_auction["active_players"] 
                         if p['name'] not in self.current_auction["passed_players"]
                         and p['money'] >= self.current_auction["minimum_bid"]]
                         
        all_passed = len(active_players) <= 1
        time_up = time_remaining <= 0
        
        if all_passed or time_up:
            if time_up:
                current_player = self.current_auction["active_players"][self.current_auction["current_bidder_index"]]
                self.current_auction["passed_players"].add(current_player['name'])
            
            self.current_auction["completed"] = True
            property_data = self.current_auction["property"]
            
            if self.current_auction["highest_bidder"]:
                winner = self.current_auction["highest_bidder"]
                bid_amount = self.current_auction["current_bid"]
                
                winner['money'] -= bid_amount
                self.bank_money += bid_amount
                property_data['owner'] = winner['name']
                
                end_reason = "time's up!" if time_up else "all other players passed!"
                return f"{winner['name']} won {property_data['name']} for £{bid_amount} - {end_reason}"
            else:
                property_data['owner'] = None
                return f"No one bid on {property_data['name']} - property returns to bank!"
                
        return None

    def is_game_over(self):
        active_players = [p for p in self.players if p["money"] > 0]
        return len(active_players) <= 1

    def get_winner(self):
        if self.is_game_over():
            active_players = [p for p in self.players if p["money"] > 0]
            if active_players:
                return active_players[0]["name"]
        return None

    def remove_player(self, player_name, voluntary=False):
        player = next((p for p in self.players if p['name'] == player_name), None)
        if player:
            for prop in self.properties.values():
                if prop.get('owner') == player_name:
                    prop['owner'] = None
                    if 'houses' in prop:
                        prop['houses'] = 0
            
            self.players.remove(player)
            if voluntary:
                self.voluntary_exits.append(player_name)
            else:
                self.bankrupted_players.append(player_name)
            
            if len(self.players) > 0:
                self.current_player_index = self.current_player_index % len(self.players)
            
            return True
        return False

    def auction(self, property_data):
        auction_message = f"AUCTION: {property_data['name']} will be auctioned because the current player did not purchase it."
        self.add_message(auction_message)
        import pygame
        pygame.time.delay(3000)
        
        eligible_players = [p for p in self.players if not p.get('in_jail', False) and p['money'] >= (property_data['price'] // 2)]
        if not eligible_players:
            self.add_message(f"No eligible players for auction. {property_data['name']} remains unsold.")
            property_data['owner'] = None
            return
        
        winning_bid_info = self.placeBids(eligible_players, property_data)
        
        if not winning_bid_info:
            self.add_message(f"Square remains unsold")
            property_data['owner'] = None
        else:
            winner, bid = winning_bid_info
            self.add_message(f"{winner['name']} has won the bid, with a total of £{bid}")
            if winner['money'] >= bid:
                winner['money'] -= bid
                self.bank_money += bid
                self.buy_property_after_auction(winner, property_data)
            else:
                self.add_message(f"Error: {winner['name']} does not have enough funds to complete the bid.")

    def placeBids(self, player_list, property_data):
        current_minimum = property_data['price'] // 2
        active_players = player_list[:]
        current_bids = {p['name']: 0 for p in active_players}
        while len(active_players) > 1:
            round_bids = {}
            for player in active_players[:]:
                if player.get('in_jail', False):
                    self.add_message(f"{player['name']} is in jail and cannot bid.")
                    active_players.remove(player)
                    continue
                if player.get('is_ai', False):
                    bid = self.get_ai_bid(player, current_minimum, property_data)
                    if bid is None:
                        self.add_message(f"{player['name']} passes on bidding.")
                        active_players.remove(player)
                        continue
                    else:
                        round_bids[player['name']] = bid
                        self.add_message(f"{player['name']} bids £{bid}")
                else:
                    bid = self.get_human_bid(player, current_minimum, property_data)
                    if bid is None:
                        self.add_message(f"{player['name']} did not bid in time and is considered as passing.")
                        active_players.remove(player)
                        continue
                    else:
                        round_bids[player['name']] = bid
                        self.add_message(f"{player['name']} bids £{bid}")
            
            if not round_bids:
                return None
            
            highest_bid = max(round_bids.values())
            active_players = [p for p in active_players if round_bids.get(p['name'], 0) == highest_bid]
            current_minimum = highest_bid + 10
            if len(active_players) == 1:
                return active_players[0], highest_bid
            self.add_message(f"Multiple players tied with £{highest_bid}. Next round of bidding begins.")
        
        if active_players:
            final_winner = active_players[0]
            final_bid = round_bids.get(final_winner['name'], current_minimum)
            return final_winner, final_bid
        return None
    
    def get_ai_bid(self, player, current_minimum, property_data):
        import random

        if player['money'] < current_minimum:
            return None
            
        base_value = property_data['price']
        value_multiplier = 1.0

        if 'group' in property_data:
            owned_in_group = sum(1 for p in self.properties.values() 
                               if p.get('group') == property_data['group'] 
                               and p.get('owner') == player['name'])
            total_in_group = sum(1 for p in self.properties.values() 
                               if p.get('group') == property_data['group'])
            if owned_in_group > 0:
                value_multiplier += 0.3 * (owned_in_group / total_in_group)

        if "Station" in property_data['name']:
            owned_stations = sum(1 for p in self.properties.values()
                               if "Station" in p.get('name', '')
                               and p.get('owner') == player['name'])
            value_multiplier += 0.25 * owned_stations

        elif property_data['name'] in ["Tesla Power Co", "Edison Water"]:
            owned_utilities = sum(1 for p in self.properties.values()
                                if p.get('name') in ["Tesla Power Co", "Edison Water"]
                                and p.get('owner') == player['name'])
            if owned_utilities > 0:
                value_multiplier += 0.5

        if hasattr(self, 'ai_difficulty') and self.ai_difficulty == 'hard':
            value_multiplier *= 1.2

        perceived_value = base_value * value_multiplier

        max_bid = min(player['money'], perceived_value)
        if max_bid <= current_minimum:
            return None

        min_increment = 10
        max_increment = 50 if player['money'] > 1000 else 25

        bid = current_minimum + random.randint(min_increment, max_increment)
        bid = min(bid, max_bid)

        if bid > perceived_value * 0.8 and random.random() < 0.3:
            return None

        return bid
    
    def get_human_bid(self, player, current_minimum, property_data):
        import time
        self.add_message(f"Player {player['name']}, would you like to bid? (Yes/No) Current minimum bid: £{current_minimum}")
        start_time = time.time()
        while True:
            try:
                response = input(f"{player['name']}, enter 'Yes' or 'No' (30s timeout): ")
            except Exception as e:
                self.add_message(f"Error: {e}")
                return None
            if time.time() - start_time > 30:
                self.add_message(f"Timeout: {player['name']} did not respond in time, skipping bid")
                return None
            if response.strip().lower() == 'no':
                return None
            elif response.strip().lower() == 'yes':
                try:
                    bid_input = input(f"{player['name']}, what is your bid? (Enter amount): ")
                    if time.time() - start_time > 30:
                        self.add_message(f"Timeout: {player['name']} took too long to enter bid amount")
                        return None
                    bid = int(bid_input)
                    if bid < current_minimum:
                        self.add_message(f"Bid must be at least £{current_minimum}")
                        start_time = time.time()
                        continue
                    if bid > player['money']:
                        self.add_message(f"Insufficient funds")
                        return None
                    return bid
                except Exception as e:
                    self.add_message(f"Error processing bid: {e}")
                    return None
            else:
                self.add_message("Please enter 'Yes' or 'No'")
                start_time = time.time()
                continue

    def buy_property_after_auction(self, player, property_data):
        property_data['owner'] = player['name']
        if 'properties' not in player:
            player['properties'] = []
        player['properties'].append(property_data['name'])
        self.add_message(f"{player['name']} now owns {property_data['name']}.")

    def handle_bankruptcy(self, player):
        total_liquidated = 0
        property_list = []
        
        for prop in self.properties.values():
            if prop.get('owner') == player['name']:
                value = prop['price']
                if 'houses' in prop:
                    value += sum(prop.get('house_costs', []))[:prop['houses']]
                property_list.append((prop['name'], value))
                total_liquidated += value

        if property_list:
            self.add_message(f"🏦 Liquidating {player['name']}'s properties:")
            for prop_name, value in property_list:
                self.add_message(f"- {prop_name}: £{value}")
            self.add_message(f"Total liquidated: £{total_liquidated}")

        for prop in self.properties.values():
            if prop.get('owner') == player['name']:
                prop['owner'] = None
                if 'houses' in prop:
                    prop['houses'] = 0

        self.players.remove(player)
        self.bankrupted_players.append(player['name'])
        
        if len(self.players) > 0:
            self.current_player_index = self.current_player_index % len(self.players)

        return True