import random
from Property import Property
from Player import Player

class SimpleAIPlayer:
    def __init__(self, difficulty='normal'):
        self.difficulty = difficulty
        self.strategy = {
            'easy': {
                'max_bid_multiplier': 0.8,
                'development_threshold': 0.7,
                'jail_stay_threshold': 0.3,
                'mortgage_threshold': 0.2
            },
            'normal': {
                'max_bid_multiplier': 1.0,
                'development_threshold': 0.5,
                'jail_stay_threshold': 0.5,
                'mortgage_threshold': 0.3
            },
            'hard': {
                'max_bid_multiplier': 1.2,
                'development_threshold': 0.3,
                'jail_stay_threshold': 0.7,
                'mortgage_threshold': 0.4
            }
        }

    def get_group_properties(self, color_group, board_properties):
        return [prop for prop in board_properties if hasattr(prop, 'group') and prop.group == color_group]

    def check_group_ownership(self, color_group, board_properties, player_name):
        if not color_group:
            return False
            
        group_properties = [p for p in board_properties if hasattr(p, 'group') and p.group == color_group]
        return all(p.owner == player_name for p in group_properties)

    def can_build_house(self, property, color_group_properties):
        if property.houses >= 4:
            return False
            
        min_houses = min(prop.houses for prop in color_group_properties)
        return property.houses <= min_houses

    def get_property_value(self, property_data, ai_player, board_properties):
        base_value = property_data.price
        multiplier = 1.0

        if hasattr(property_data, 'group'):
            owned_in_group = sum(1 for p in board_properties 
                               if hasattr(p, 'group') and p.group == property_data.group 
                               and p.owner == ai_player)
            total_in_group = sum(1 for p in board_properties 
                               if hasattr(p, 'group') and p.group == property_data.group)
            if owned_in_group > 0:
                multiplier += 0.3 * (owned_in_group / total_in_group)

        if property_data.is_station:
            owned_stations = sum(1 for p in board_properties 
                               if p.is_station and p.owner == ai_player)
            multiplier += 0.25 * owned_stations

        elif property_data.is_utility:
            owned_utilities = sum(1 for p in board_properties 
                                if p.is_utility and p.owner == ai_player)
            if owned_utilities > 0:
                multiplier += 0.5

        return base_value * multiplier

    def handle_turn(self, ai_player, current_location, board_properties, is_first_round=False):
        actions = {"bought_property": False, "built_house": False, "paid_rent": False}

        if current_location.name == "GO":
            return actions

        elif isinstance(current_location, Property):
            if current_location.owner and current_location.owner != ai_player:
                rent = current_location.calculate_rent(None, current_location.owner.properties)
                if ai_player.money >= rent:
                    actions["paid_rent"] = True

            elif not current_location.owner:
                if random.random() < 0.7 and ai_player.money >= current_location.price:
                    success = ai_player.buy_property(current_location)
                    actions["bought_property"] = success

                    if success and not is_first_round and hasattr(current_location, 'group'):
                        color_group = current_location.group
                        if self.check_group_ownership(color_group, board_properties, ai_player.name):
                            if random.random() < 0.5:
                                group_properties = self.get_group_properties(color_group, board_properties)
                                if self.can_build_house(current_location, group_properties):
                                    house_cost = current_location.price / 2
                                    if ai_player.money >= house_cost:
                                        current_location.houses += 1
                                        ai_player.pay(house_cost)
                                        actions["built_house"] = True

        elif current_location.name == "JAIL":
            pass

        elif current_location.name == "FREE PARKING":
            pass

        return actions

    def should_use_get_out_of_jail_card(self):
        return True

    def should_pay_jail_fine(self, ai_player):
        return ai_player.money >= 250

    def should_mortgage_property(self, ai_player, required_money):
        if ai_player.money >= required_money:
            return []

        to_mortgage = []
        need_amount = required_money - ai_player.money

        unset_properties = [prop for prop in ai_player.properties 
                          if not self.check_group_ownership(prop.group, ai_player.properties, ai_player.name)]
        
        for prop in sorted(unset_properties, key=lambda x: x.price):
            if need_amount <= 0:
                break
            if not prop.is_mortgaged:
                to_mortgage.append(prop)
                need_amount -= prop.price / 2

        if need_amount > 0:
            set_properties = [prop for prop in ai_player.properties 
                            if self.check_group_ownership(prop.group, ai_player.properties, ai_player.name)]
            
            for prop in sorted(set_properties, key=lambda x: x.price):
                if need_amount <= 0:
                    break
                if not prop.is_mortgaged:
                    to_mortgage.append(prop)
                    need_amount -= prop.price / 2

        return to_mortgage

    def handle_ai_turn(self, ai_player, board_properties):
        current_location_type = self.get_location_type(ai_player.position, board_properties)
        property_name = self.get_property_name(ai_player.position, board_properties)
        
        if current_location_type == "Go":
            return True

        elif current_location_type == "property":
            property_data = next((p for p in board_properties if p.name == property_name), None)
            if not property_data:
                return True

            if property_data.owner and property_data.owner != ai_player:
                return True
            elif not property_data.owner:
                if random.random() < 0.7 and ai_player.money >= property_data.price:
                    return True
                return False

        elif current_location_type == "lucky_area":
            return True

        elif current_location_type == "jail":
            return True

        return True

    def get_location_type(self, position, board_properties):
        property_data = next((p for p in board_properties if p.position == position), None)
        
        if not property_data:
            if position == 1:
                return "Go"
            elif position == 11:
                return "jail"
            elif position == 21:
                return "free_parking"
            elif position in [3, 18, 34]:
                return "lucky_area"
            elif position in [8, 23, 37]:
                return "lucky_area"
            return "other"
        
        return "property"

    def get_property_name(self, position, board_properties):
        property_data = next((p for p in board_properties if p.position == position), None)
        return property_data.name if property_data else None

    def get_auction_bid(self, current_minimum, property_data, ai_player, board_properties):
        if ai_player.money < current_minimum:
            return None

        perceived_value = self.get_property_value(property_data, ai_player, board_properties)
        max_bid = min(ai_player.money, perceived_value * self.auction_max_multiplier)
        
        if max_bid <= current_minimum:
            return None

        bid_headroom = max_bid - current_minimum
        increment = min(50, max(10, int(bid_headroom * 0.2)))
        
        bid = current_minimum + random.randint(10, increment)
        bid = min(bid, max_bid)

        if bid > perceived_value * 0.6 and random.random() < 0.3:
            return None

        return bid

    def handle_jail_strategy(self, ai_player, jail_free_cards):
        if not ai_player.get('in_jail', False):
            return None
            
        if jail_free_cards.get(ai_player['name'], 0) > 0:
            return "use_card"
            
        if ai_player['money'] >= 250:
            total_property_value = sum(prop['price'] for prop in ai_player.properties)
            if total_property_value > 500:
                return "pay_fine"
                
        return "roll_doubles"

    def handle_property_development(self, ai_player, board_properties):
        if ai_player['money'] < 200:
            return None
            
        groups = set()
        for prop in board_properties.values():
            if 'group' in prop:
                groups.add(prop['group'])
            
        for color_group in groups:
            group_properties = [p for p in board_properties.values() 
                              if p.get('group') == color_group 
                              and p.get('owner') == ai_player['name']]
            
            total_in_group = sum(1 for p in board_properties.values() 
                               if p.get('group') == color_group)
                               
            if len(group_properties) == total_in_group:
                for prop in group_properties:
                    current_houses = prop.get('houses', 0)
                    if current_houses < 4:
                        min_houses = min(p.get('houses', 0) for p in group_properties)
                        if current_houses <= min_houses:
                            house_cost = prop['price'] / 2
                            if ai_player['money'] >= house_cost * 1.5:
                                return prop
        return None

    def handle_emergency_cash(self, ai_player, required_amount, board_properties):
        if ai_player['money'] >= required_amount:
            return []
            
        properties_to_mortgage = []
        for prop in board_properties.values():
            if prop.get('owner') == ai_player['name'] and not prop.get('is_mortgaged'):
                if not self.check_group_ownership(prop.get('group'), board_properties, ai_player['name']):
                    properties_to_mortgage.append(prop)
        
        properties_to_mortgage.sort(key=lambda x: x['price'])
        
        potential_cash = 0
        final_properties = []
        
        for prop in properties_to_mortgage:
            potential_cash += prop['price'] / 2
            final_properties.append(prop)
            if potential_cash >= required_amount:
                break
                
        return final_properties if potential_cash >= required_amount else []

    def consider_trade_offer(self, ai_player, offered_properties, requested_properties, 
                           cash_difference, board_properties):
        offered_value = sum(prop['price'] for prop in offered_properties)
        
        for prop in offered_properties:
            if prop.get('group'):
                owned_in_group = sum(1 for p in board_properties 
                                   if p.get('group') == prop.get('group') 
                                   and p.get('owner') == ai_player['name'])
                total_in_group = sum(1 for p in board_properties 
                                   if p.get('group') == prop.get('group'))
                if owned_in_group + 1 == total_in_group:
                    offered_value += prop['price']
        
        requested_value = sum(prop['price'] for prop in requested_properties)
        
        for prop in requested_properties:
            if prop.get('group'):
                if self.check_group_ownership(prop.get('group'), board_properties, ai_player['name']):
                    requested_value *= 1.5
        
        total_value_difference = (offered_value + cash_difference) - requested_value
        
        return total_value_difference > 0 and random.random() < 0.8

    def get_property_value(self, property_data, owned_properties, total_money):
        base_value = property_data['price']
        value_multiplier = 1.0

        if 'group' in property_data:
            owned_in_group = sum(1 for p in owned_properties 
                               if p.get('group') == property_data['group'])
            total_in_group = property_data.get('group_size', 3)
            if owned_in_group > 0:
                value_multiplier += 0.3 * (owned_in_group / total_in_group)

        if "Station" in property_data['name']:
            owned_stations = sum(1 for p in owned_properties 
                               if "Station" in p.get('name', ''))
            value_multiplier += 0.25 * owned_stations

        elif property_data['name'] in ["Tesla Power Co", "Edison Water"]:
            owned_utilities = sum(1 for p in owned_properties 
                                if p.get('name') in ["Tesla Power Co", "Edison Water"])
            if owned_utilities > 0:
                value_multiplier += 0.5

        value_multiplier *= self.strategy[self.difficulty]['max_bid_multiplier']

        return base_value * value_multiplier

    def should_buy_property(self, property_data, player_money, owned_properties):
        if player_money < property_data['price']:
            return False

        property_value = self.get_property_value(property_data, owned_properties, player_money)
        return player_money >= property_data['price'] and property_value >= property_data['price']

    def make_auction_bid(self, property_data, current_bid, player_money, owned_properties):
        if player_money <= current_bid:
            return None

        property_value = self.get_property_value(property_data, owned_properties, player_money)
        max_bid = min(player_money * 0.8, property_value)

        if max_bid <= current_bid:
            return None

        bid_increment = 10 if self.difficulty == 'easy' else (25 if self.difficulty == 'normal' else 50)
        return min(current_bid + bid_increment, max_bid)

    def should_develop_property(self, property_data, player_money, owned_properties):
        if player_money < property_data.get('house_cost', float('inf')):
            return False

        current_houses = property_data.get('houses', 0)
        if current_houses >= 5:
            return False

        development_cost = property_data.get('house_cost', 0)
        potential_rent = property_data.get('house_rents', [0])[current_houses] if current_houses < len(property_data.get('house_rents', [])) else 0
        
        money_threshold = self.strategy[self.difficulty]['development_threshold'] * player_money
        return (development_cost <= money_threshold and 
                potential_rent >= development_cost * 0.2 * (3 if self.difficulty == 'hard' else 2))

    def should_mortgage_property(self, property_data, player_money):
        if property_data.get('is_mortgaged', False) or property_data.get('houses', 0) > 0:
            return False

        mortgage_threshold = self.strategy[self.difficulty]['mortgage_threshold'] * 1500
        return player_money < mortgage_threshold

    def should_unmortgage_property(self, property_data, player_money):
        if not property_data.get('is_mortgaged', False):
            return False

        unmortgage_cost = (property_data['price'] // 2) * 1.1
        return (player_money > unmortgage_cost * 2 and 
                unmortgage_cost < player_money * (0.4 if self.difficulty == 'hard' else 0.3))

    def get_jail_decision(self, player, dice1, dice2):
        if not player.get('is_ai', False):
            has_jail_card = player.get('jail_free_cards', 0) > 0
            can_pay_fine = player['money'] >= 50
            is_doubles = dice1 == dice2
            jail_turns = player.get('jail_turns', 0)

            if jail_turns >= 2:
                if has_jail_card:
                    return 'use_card'
                return 'pay'

            if has_jail_card or can_pay_fine:
                return None
            
            if is_doubles:
                return 'roll'

            return 'stay'
        else:
            jail_turns = player.get('jail_turns', 0)
            is_doubles = dice1 == dice2

            if jail_turns >= 2:
                return 'pay'
            
            if is_doubles:
                return 'roll'
            
            return 'stay'

    def should_sell_houses(self, property_data, player_money, target_amount):
        if property_data.get('houses', 0) == 0:
            return False

        sell_threshold = target_amount * (1.2 if self.difficulty == 'easy' else 
                                        1.1 if self.difficulty == 'normal' else 1.0)
        return player_money < sell_threshold

    def get_development_priority(self, properties):
        priorities = []
        for prop in properties:
            if prop.get('group'):
                rent_to_cost_ratio = max(prop.get('house_rents', [0])) / prop.get('house_cost', float('inf'))
                group_completion = 1.0
                priority_score = rent_to_cost_ratio * group_completion
                priorities.append((prop, priority_score))

        return sorted(priorities, key=lambda x: x[1], reverse=True)
