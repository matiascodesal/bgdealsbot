

class DealQueryError(Exception):
    pass


class Deal(object):
    def __init__(self, game_name, price, link, site_name):
        self.game_name = game_name
        self.price = price
        self.link = link
        self.site_name = site_name
        self.bgg_link = ""

    @property
    def formatted_price(self):
        return "${:.2f}".format(self.price)

    def __str__(self):
        return "{site_name} Deal: {game_name}, {price}".format(site_name=self.site_name,
                                                               game_name=self.game_name,
                                                               price=self.formatted_price)

    def get_formatted_title(self):
        return "[{}][DotD] {} -- {}".format(self.site_name, self.game_name, self.formatted_price)