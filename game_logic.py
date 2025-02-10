# Base on PropertyTycoonCardData.xlsx from canvas 
# script based on Eric's provided flowchart photo (flowchart.drawio.png)
# will add more comment later to reference for which part of code is based on which part of the flowchart
import random
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
            if space["owner"] is None:
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

    def buy_property(self, player):
        position = str(player["position"])
        property_data = self.properties[position]

        if player["money"] >= property_data["price"]:
            player["money"] -= property_data["price"]
            self.bank_money += property_data["price"]
            property_data["owner"] = player["name"]
            return True
        return False

    def auction_property(self, position):
        position = str(position)
        property_data = self.properties[position]
        auction_price = property_data["price"] // 2
        for player in self.players:
            if player["money"] >= auction_price:
                player["money"] -= auction_price
                self.bank_money += auction_price
                property_data["owner"] = player["name"]
                return True
        return False

    def is_game_over(self):
        active_players = [p for p in self.players if p["money"] > 0]
        return len(active_players) <= 1

    def get_winner(self):
        if self.is_game_over():
            active_players = [p for p in self.players if p["money"] > 0]
            if active_players:
                return active_players[0]["name"]
        return None