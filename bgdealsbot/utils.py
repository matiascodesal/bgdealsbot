from datetime import datetime
import calendar

class DealQueryError(Exception):
    pass


class Deal(object):
    def __init__(self, game_name, price, link, site_name, type="DotD"):
        self.game_name = game_name
        self.price = price
        self.link = link
        self.site_name = site_name
        self.bgg_link = ""
        self.alt_links = []
        self.type = type

    @property
    def formatted_price(self):
        return "${:.2f}".format(self.price)

    def __str__(self):
        return "{site_name} Deal: {game_name}, {price}".format(site_name=self.site_name,
                                                               game_name=self.game_name,
                                                               price=self.formatted_price)

    def get_formatted_title(self):
        return "[{}][{}] {} -- {}".format(self.site_name, self.type, self.game_name, self.formatted_price)

    def get_possible_links(self):
        return self.alt_links + [self.link]


class schedule(object):
    def __init__(self, hour, day=-1):
        self.day = day
        self.hour = hour

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            now = datetime.now()
            if self.day in [-1, now.weekday()] and now.hour == self.hour:
                result = func(*args, **kwargs)
                print(result)
                return result
            else:
                if self.day == -1:
                    day_name = "Everyday"
                else:
                    day_name = list(calendar.day_name)[self.day] + "s"
                print("Skipping {}.  It's scheduled to run {} at {}00 hours.".format(func, day_name, self.hour))
                return

        return wrapper