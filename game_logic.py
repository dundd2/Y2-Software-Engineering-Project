# Base on PropertyTycoonCardData.xlsx from canvas 
# script based on Eric's provided flowchart photo (flowchart.drawio.png)
# will add more comment later to reference for which part of code is based on which part of the flowchart
import random
import pygame
from loadexcel import load_property_data
from ai_player_logic import SimpleAIPlayer

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
    BANK_LIMIT = 50000
    MAX_HOUSES_PER_PROPERTY = 4
    MAX_HOTELS_PER_PROPERTY = 1
    GAME_TOKENS = ["boot", "smartphone", "ship", "hatstand", "cat", "iron"]
    
    def __init__(self):
        self.players = []
        self.bank_money = self.BANK_LIMIT
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
        self.completed_circuits = {}
        self.available_tokens = self.GAME_TOKENS.copy()
        self.pot_luck_cards = pot_luck_cards.copy()
        self.opportunity_knocks_cards = opportunity_knocks_cards.copy()
        random.shuffle(self.pot_luck_cards)
        random.shuffle(self.opportunity_knocks_cards)
        self.ai_player = SimpleAIPlayer()
        self.game = None

    def validate_bank_transaction(self, amount):
        if amount > self.bank_money:
            raise ValueError("Bank does not have sufficient funds")
        return True
        
    def pay_from_bank(self, player, amount):
        if self.validate_bank_transaction(amount):
            self.bank_money -= amount
            player['money'] += amount
            return True
        return False
        
    def pay_to_bank(self, player, amount):
        if player['money'] >= amount:
            player['money'] -= amount
            self.bank_money += amount
            return True
        return False

    def game_start(self):
        self.properties = load_property_data()
        if self.properties is None:
            return False
        return True

    def add_player(self, player):
        if len(self.players) < 5:
            if not self.available_tokens:
                return False, "No tokens available"
            player_name = player.name if hasattr(player, 'name') else player
            player_is_ai = getattr(player, 'is_ai', False) if hasattr(player, 'is_ai') else False
            token = random.choice(self.available_tokens)
            self.available_tokens.remove(token)
            new_player = {
                "name": player_name,
                "money": 1500,
                "position": 1,
                "is_ai": player_is_ai,
                "properties": [],
                "token": token
            }
            self.players.append(new_player)
            self.completed_circuits[player_name] = 0
            return True, f"Added player {player_name} with {token} token"
        return False, "Maximum number of players reached"

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
            self.completed_circuits[current_player['name']] += 1
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

        if space["name"] == "Free Parking":
            if self.free_parking_fund > 0:
                amount = self.free_parking_fund
                player["money"] += amount
                self.free_parking_fund = 0
                message = f"{player['name']} collected £{amount} from Free Parking!"
                self.add_message(message)
            return None, message

        if "price" in space:
            if space["owner"] is None and not player.get('in_jail', False):
                if self.completed_circuits[player['name']] < 1:
                    self.add_message(f"{player['name']} must complete one circuit before buying property")
                    return None, None
                self.add_message(f"Would you like to buy {space['name']} for £{space['price']}?")
                return "can_buy", None
            elif space["owner"] != player["name"]:
                owner = next(p for p in self.players if p["name"] == space["owner"])
                if owner.get('in_jail', False):
                    self.add_message(f"{owner['name']} is in jail and cannot collect rent")
                    return None, None
                
                rent = self.calculate_space_rent(space, player)
                if player["money"] >= rent:
                    player["money"] -= rent
                    owner["money"] += rent
                    message = f"{player['name']} paid £{rent} rent to {owner['name']}"
                    self.add_message(message)
                else:
                    message = f"{player['name']} went bankrupt!"
                    self.add_message(message)
                    self.remove_player(player['name'])
                    return "bankrupt", message

        elif space["name"] in ["Income Tax", "Super Tax"]:
            tax = 200 if space["name"] == "Income Tax" else 100
            if player["money"] >= tax:
                player["money"] -= tax
                self.free_parking_fund += tax
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
        self.doubles_count = 0
        self.add_message(f"{player['name']} goes to jail!")
        return True

    def try_leave_jail(self, player, dice1, dice2):
        if not player.get('in_jail', False):
            return True, None

        if 'jail_turns' not in player:
            player['jail_turns'] = 0

        if self.jail_free_cards.get(player['name'], 0) > 0 and (player.get('is_ai', False) or self.game and self.game.get_jail_choice(player) == "card"):
            self.jail_free_cards[player['name']] -= 1
            player['in_jail'] = False
            player['jail_turns'] = 0
            return True, f"{player['name']} uses Get Out of Jail Free card!"

        if dice1 == dice2:
            player['in_jail'] = False
            player['jail_turns'] = 0
            return True, f"{player['name']} rolled doubles and left jail!"

        if player['money'] >= 50 and (player.get('is_ai', False) or self.game and self.game.get_jail_choice(player) == "pay"):
            player['money'] -= 50
            self.free_parking_fund += 50
            player['in_jail'] = False
            player['jail_turns'] = 0
            return True, f"{player['name']} paid £50 to leave jail"

        player['jail_turns'] += 1

        if player['jail_turns'] >= 3:
            if player['money'] >= 50:
                player['money'] -= 50
                self.free_parking_fund += 50
                player['in_jail'] = False
                player['jail_turns'] = 0
                return True, f"{player['name']} paid £50 to leave jail after 3 turns"
            else:
                self.handle_bankruptcy(player)
                player['in_jail'] = False
                player['jail_turns'] = 0
                return True, f"{player['name']} went bankrupt trying to pay jail fine"

        return False, f"{player['name']} stays in jail (turn {player['jail_turns']}/3)"

    def check_game_over(self):
        if self.game_mode == "full":
            active_players = [p for p in self.players if p['money'] > 0]
            if len(active_players) <= 1:
                return True, active_players[0] if active_players else None
                
        elif self.game_mode == "abridged":
            min_rounds = min(self.rounds_completed.values())
            if min_rounds > 0 and all(rounds == min_rounds for rounds in self.rounds_completed.values()):
                assets = {}
                for player in self.players:
                    total = player['money']
                    for prop in self.properties.values():
                        if prop.get('owner') == player['name']:
                            total += prop['price']
                            if not prop.get('is_mortgaged', False):
                                total += prop.get('houses', 0) * prop.get('house_cost', 0)
                    assets[player['name']] = total
                winner = max(assets.items(), key=lambda x: x[1])[0]
                return True, winner
                
        return False, None

    def handle_jail(self, player):
        player['position'] = 11
        player['in_jail'] = True
        player['jail_turns'] = 0
        self.is_going_to_jail = True
        self.doubles_count = 0
        self.add_message("Go to jail. Do not pass GO, do not collect £200")
        return "Go to jail. Do not pass GO, do not collect £200"

    def calculate_space_rent(self, space, player):
        if space.get('is_mortgaged', False):
            return 0
            
        if "Station" in space["name"]:
            station_count = sum(1 for prop in self.properties.values()
                              if "Station" in prop.get("name", "")
                              and prop.get("owner") == space["owner"])
            return 25 * (2 ** (station_count - 1))
            
        elif space["name"] in ["Tesla Power Co", "Edison Water"]:
            utility_count = sum(1 for prop in self.properties.values()
                              if prop.get("name") in ["Tesla Power Co", "Edison Water"]
                              and prop.get("owner") == space["owner"])
            dice_total = sum(self.last_dice_roll) if self.last_dice_roll else 7
            return dice_total * (10 if utility_count > 1 else 4)
            
        base_rent = space.get("rent", 0)
        if space.get("houses", 0) > 0:
            house_rents = space.get("house_costs", [])
            house_index = min(space["houses"] - 1, len(house_rents) - 1)
            return house_rents[house_index]
            
        color_group = space.get("group")
        if color_group:
            all_owned = all(p.get("owner") == space["owner"] 
                          for p in self.properties.values() 
                          if p.get("group") == color_group)
            if all_owned:
                return base_rent * 2
                
        return base_rent

    def handle_card_draw(self, player, card_type):
        cards = self.pot_luck_cards if card_type == "Pot Luck" else self.opportunity_knocks_cards
        card = cards.pop(0)
        message = card['text']
        self.add_message(message)

        if hasattr(self, 'game') and self.game and not player.get('is_ai', False):
            self.game.show_card_popup(card_type, message)

        result = None
        if message == "Get out of jail free":
            self.jail_free_cards[player['name']] = self.jail_free_cards.get(player['name'], 0) + 1
            result = None
        else:
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

        cards.append(card)
        return result, message

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
            
        if self.completed_circuits.get(player['name'], 0) < 1:
            self.add_message(f"{player['name']} must pass GO before buying property")
            return False
            
        position = str(player["position"])
        property_data = self.properties[position]
        price = property_data["price"]

        if player["money"] >= price:
            if self.validate_bank_transaction(price):
                player["money"] -= price
                self.bank_money += price
                property_data["owner"] = player["name"]
                self.check_property_group_completion(player["name"])
                return True
        return False

    def auction_property(self, position):
        position = str(position)
        if position not in self.properties:
            self.add_message(f"Error: Invalid property position {position}")
            return "auction_completed"
            
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
        print(f"DEBUG: AI Player {player['name']} evaluating bid. Current minimum: {current_minimum}, Money: {player['money']}, Property Price: {property_data['price']}")
        if player['money'] < current_minimum:
            print(f"DEBUG: {player['name']} does not have enough money to bid. Money: {player['money']} < {current_minimum}")
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
        print(f"DEBUG: {player['name']} perceived_value: {perceived_value}")

        max_bid = min(player['money'], perceived_value)
        print(f"DEBUG: {player['name']} max_bid computed as: {max_bid}")

        if max_bid <= current_minimum:
            print(f"DEBUG: {player['name']} max_bid ({max_bid}) <= current_minimum ({current_minimum}); passing.")
            return None

        min_increment = 10
        max_increment = 50 if player['money'] > 1000 else 25

        bid = current_minimum + random.randint(min_increment, max_increment)
        bid = min(bid, max_bid)
        print(f"DEBUG: {player['name']} candidate bid before random pass check: {bid}")

        if bid > perceived_value * 0.8 and random.random() < 0.3:
            print(f"DEBUG: {player['name']} decides to pass despite candidate bid {bid}")
            return None

        print(f"DEBUG: {player['name']} bids {bid}")
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

    def can_build_house(self, property_data, player):
        if property_data.get('is_mortgaged', False):
            return False, "Cannot build on mortgaged property"

        color_group = property_data.get('group')
        if not color_group:
            return False, "Cannot build houses on this type of property"
            
        color_group_properties = [p for p in self.properties.values() 
                                if p.get('group') == color_group]
                                
        for prop in color_group_properties:
            if prop.get('owner') != player['name']:
                return False, f"Must own all {color_group} properties to build"

        current_houses = property_data.get('houses', 0)
        for prop in color_group_properties:
            if prop != property_data:
                other_houses = prop.get('houses', 0)
                if current_houses + 1 > other_houses + 1:
                    return False, "Must build houses evenly across properties"

        if current_houses >= 5:
            return False, "Maximum development reached"

        return True, None

    def can_build_hotel(self, property_data, player):
        if not self.check_property_group_completion(player['name']):
            return False, "You must own all properties in the color group"

        color_group = [p for p in self.properties.values() 
                      if p.get("color") == property_data.get("color") 
                      and p.get("owner") == player['name']]

        current_houses = property_data.get("houses", 0)
        if current_houses != 4:
            return False, "Must have 4 houses before building a hotel"

        for prop in color_group:
            if prop != property_data:
                other_houses = prop.get("houses", 0)
                if other_houses < 4:
                    return False, "All properties in the set must have at least 4 houses before building a hotel"

        return True, None

    def build_house(self, property_data, player):
        can_build, error = self.can_build_house(property_data, player)
        if not can_build:
            self.add_message(error)
            return False
            
        current_houses = property_data.get("houses", 0)
        if current_houses >= self.MAX_HOUSES_PER_PROPERTY:
            self.add_message("Maximum number of houses already built")
            return False

        house_cost = property_data.get("house_cost", 0)
        if player["money"] >= house_cost:
            if self.validate_bank_transaction(house_cost):
                player["money"] -= house_cost
                self.bank_money += house_cost
                property_data["houses"] = current_houses + 1
                self.add_message(f"{player['name']} built a house on {property_data['name']}")
                return True
        
        self.add_message("Not enough money to build a house")
        return False

    def build_hotel(self, property_data, player):
        can_build, error = self.can_build_hotel(property_data, player)
        if not can_build:
            self.add_message(error)
            return False

        hotel_cost = property_data.get("house_cost", 0)
        if player["money"] >= hotel_cost:
            if self.validate_bank_transaction(hotel_cost):
                player["money"] -= hotel_cost
                self.bank_money += hotel_cost
                property_data["houses"] = 5
                self.add_message(f"{player['name']} built a hotel on {property_data['name']}")
                return True
        
        self.add_message("Not enough money to build a hotel")
        return False

    def sell_house(self, property_data, player):
        current_houses = property_data.get("houses", 0)
        if current_houses == 0:
            self.add_message("No houses to sell")
            return False

        color_group = [p for p in self.properties.values() 
                      if p.get("color") == property_data.get("color") 
                      and p.get("owner") == player['name']]

        for prop in color_group:
            if prop != property_data:
                other_houses = prop.get("houses", 0)
                if current_houses - 1 < other_houses - 1:
                    self.add_message("Cannot have more than 1 house difference between properties in a set")
                    return False

        house_cost = property_data.get("house_cost", 0)
        player["money"] += house_cost // 2
        self.bank_money -= house_cost // 2
        property_data["houses"] = current_houses - 1
        self.add_message(f"{player['name']} sold a house from {property_data['name']}")
        return True

    def sell_hotel(self, property_data, player):
        if property_data.get("houses", 0) != 5:
            self.add_message("No hotel to sell")
            return False

        hotel_cost = property_data.get("house_cost", 0) * 5
        player["money"] += hotel_cost // 2
        self.bank_money -= hotel_cost // 2
        property_data["houses"] = 4
        self.add_message(f"{player['name']} sold a hotel from {property_data['name']}")
        return True

    def mortgage_property(self, property_data, player):
        if property_data.get('is_mortgaged', False):
            self.add_message(f"{property_data['name']} is already mortgaged")
            return False
            
        if property_data.get('houses', 0) > 0:
            self.add_message("Cannot mortgage property with houses/hotels")
            return False
            
        mortgage_value = property_data['price'] // 2
        self.pay_from_bank(player, mortgage_value)
        property_data['is_mortgaged'] = True
        self.add_message(f"{player['name']} mortgaged {property_data['name']} for £{mortgage_value}")
        return True
        
    def unmortgage_property(self, property_data, player):
        if not property_data.get('is_mortgaged', False):
            self.add_message(f"{property_data['name']} is not mortgaged")
            return False
            
        unmortgage_cost = (property_data['price'] // 2) * 1.1
        if player['money'] >= unmortgage_cost:
            self.pay_to_bank(player, unmortgage_cost)
            property_data['is_mortgaged'] = False
            self.add_message(f"{player['name']} unmortgaged {property_data['name']} for £{unmortgage_cost}")
            return True
        else:
            self.add_message(f"Not enough money to unmortgage {property_data['name']}")
            return False
            
    def handle_rent_payment(self, landing_player, property_data):
        if property_data.get('is_mortgaged', False):
            self.add_message(f"Property is mortgaged - no rent due")
            return True
            
        owner = next((p for p in self.players if p['name'] == property_data['owner']), None)
        if not owner or owner.get('in_jail', False):
            self.add_message(f"Owner is in jail - no rent collected")
            return True
            
        rent = self.calculate_space_rent(property_data, landing_player)
        if landing_player['money'] >= rent:
            landing_player['money'] -= rent
            owner['money'] += rent
            self.add_message(f"{landing_player['name']} paid £{rent} rent to {owner['name']}")
            return True
        else:
            self.handle_bankruptcy(landing_player)
            return False
            
    def calculate_house_difference(self, color_group_properties):
        house_counts = [p.get('houses', 0) for p in color_group_properties]
        return max(house_counts) - min(house_counts)

    def handle_ai_turn(self, player):
        if not player.get('is_ai', False):
            return None

        if player.get('in_jail', False):
            jail_decision = self.ai_player.get_jail_decision(player, *self.last_dice_roll)
            if jail_decision == 'use_card' and self.jail_free_cards.get(player['name'], 0) > 0:
                self.jail_free_cards[player['name']] -= 1
                player['in_jail'] = False
                player['jail_turns'] = 0
            elif jail_decision == 'pay' and player['money'] >= 50:
                player['money'] -= 50
                self.free_parking_fund += 50
                player['in_jail'] = False
                player['jail_turns'] = 0

        owned_properties = [prop for prop in self.properties.values() if prop.get('owner') == player['name']]
        development_priorities = self.ai_player.get_development_priority(owned_properties)
        
        for property_data, _ in development_priorities:
            if self.ai_player.should_develop_property(property_data, player['money'], owned_properties):
                if property_data.get('houses', 0) == 4:
                    self.build_hotel(property_data, player)
                else:
                    self.build_house(property_data, player)

        if player['money'] < 200:
            for prop in owned_properties:
                if self.ai_player.should_mortgage_property(prop, player['money']):
                    self.mortgage_property(prop, player)
        elif player['money'] > 500:
            mortgaged_properties = [p for p in owned_properties if p.get('is_mortgaged', True)]
            for prop in mortgaged_properties:
                if self.ai_player.should_unmortgage_property(prop, player['money']):
                    self.unmortgage_property(prop, player)

        return None

    def process_ai_property_purchase(self, player, property_data):
        if not player.get('is_ai', False):
            return False

        owned_properties = [prop for prop in self.properties.values() if prop.get('owner') == player['name']]
        if self.ai_player.should_buy_property(property_data, player['money'], owned_properties):
            return self.buy_property(player)
        else:
            return self.auction_property(property_data['position'])

    def get_ai_auction_bid(self, player, property_data, current_bid):
        if not player.get('is_ai', False):
            return None

        owned_properties = [prop for prop in self.properties.values() if prop.get('owner') == player['name']]
        return self.ai_player.make_auction_bid(property_data, current_bid, player['money'], owned_properties)

    def handle_ai_bankruptcy_prevention(self, player, amount_needed):
        if not player.get('is_ai', False):
            return False

        owned_properties = [prop for prop in self.properties.values() if prop.get('owner') == player['name']]
        
        for prop in owned_properties:
            if self.ai_player.should_sell_houses(prop, player['money'], amount_needed):
                if prop.get('houses', 0) == 5:
                    self.sell_hotel(prop, player)
                else:
                    self.sell_house(prop, player)
                if player['money'] >= amount_needed:
                    return True

        for prop in owned_properties:
            if self.ai_player.should_mortgage_property(prop, player['money']):
                self.mortgage_property(prop, player)
                if player['money'] >= amount_needed:
                    return True

        return False

    def handle_buy_decision(self, player, decision):
        position = str(player["position"])
        property_data = self.properties[position]

        if player.get('in_jail', False):
            return "Cannot buy property while in jail"

        if property_data.get('owner') is not None:
            return "Property is already owned"
            
        if property_data.get('is_mortgaged', False):
            return "Property is mortgaged and cannot be purchased"

        if player.get('is_ai', False):
            if self.process_ai_property_purchase(player, property_data):
                return f"{player['name']} bought {property_data['name']}"
            else:
                return f"{property_data['name']} goes to auction"

        if decision == 'buy':
            if self.buy_property(player):
                return f"{player['name']} bought {property_data['name']}"
            else:
                self.auction_property(position)
                return f"Insufficient funds. {property_data['name']} goes to auction"
        elif decision == 'auction':
            self.auction_property(position)
            return f"{property_data['name']} goes to auction"
        else:
            return "Invalid decision. Must be 'buy' or 'auction'"