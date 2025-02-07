class Property:
    def __init__(self, name, price, rent):
        self.name = name
        self.price = price
        self.rent = rent
        self.owner = None

    def charge_rent(self, player):
        if self.owner and self.owner != player:
            print(f"{player.name} landed on {self.name}, paying ${self.rent} rent to {self.owner.name}")
            player.pay(self.rent)
            self.owner.receive(self.rent)