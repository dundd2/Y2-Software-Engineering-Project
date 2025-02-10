class Property:
    def __init__(self, name, price, rent):
        self.name = name
        self.price = price
        self.rent = rent
        self.owner = None
        self.is_station = "Station" in name
        self.is_utility = name in ["Tesla Power Co", "Edison Water"]
        self.houses = 0

## from the note part of PropertyTycoonBoardData.xlsx
    def calculate_rent(self, dice_roll=None, owner_properties=None):
        if self.is_station and owner_properties:
            # how many stations the owner has?
            station_count = sum(1 for prop in owner_properties if prop.is_station)
            # Station rent: £25 for 1, £50 for 2, £100 for 3, £200 for 4
            return 25 * (2 ** (station_count - 1))
        elif self.is_utility and dice_roll and owner_properties:
            # how many utilities the owner has?
            utility_count = sum(1 for prop in owner_properties if prop.is_utility)
            # Utility rent: 4x dice if owner has 1 utility, 10x dice if owner has both
            multiplier = 10 if utility_count > 1 else 4
            return dice_roll * multiplier
        return self.rent

    def charge_rent(self, player, dice_roll=None):
        if self.owner and self.owner != player:
            rent = self.calculate_rent(dice_roll, self.owner.properties)
            print(f"{player.name} landed on {self.name}, paying £{rent} rent to {self.owner.name}")
            player.pay(rent)
            self.owner.receive(rent)
            return rent
        return 0