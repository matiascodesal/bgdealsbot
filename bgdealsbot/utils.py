import calendar
from datetime import datetime
import re
import time

import praw


class DealQueryError(Exception):
    pass


class Deal(object):
    """Class for storing data required for posting a deal."""
    def __init__(self, game_name, price, link, site_name, deal_type="DotD"):
        """ Constructor

        Args:
            game_name(str): The name of the board game
            price(float): The price of the deal
            link(str): The url to the deal
            site_name(str): The formal name for the site the deal is from
            deal_type(str): The type of deal (DotD, DotW, etc).
        """
        self.game_name = game_name
        self.price = price
        self.link = link
        self.site_name = site_name
        self.bgg_link = ""
        self.alt_links = []
        self.deal_type = deal_type

    @property
    def formatted_price(self):
        """Returns price with $ symbol and two decimal places"""
        return "${:.2f}".format(self.price)

    def __str__(self):
        return "{site_name} Deal: {game_name}, {price}".format(site_name=self.site_name,
                                                               game_name=self.game_name,
                                                               price=self.formatted_price)

    def get_formatted_title(self):
        """Returns the formatted title for the reddit post."""
        return "[{}][{}] {} -- {}".format(self.site_name, self.deal_type, self.game_name, self.formatted_price)

    def get_possible_links(self):
        """Returns all links that could be associated with a deal.

        This is used for checking if a deal has been posted already by
        checking if any of the possible links have been used.
        """
        return self.alt_links + [self.link]


class schedule(object):
    """ Decorator for scheduling a function run

    The decorator will only run the decorated function
    on the hour and day provided.
    """
    def __init__(self, hour, day=-1):
        """

        Args:
            hour(int): Hour the function should run represented as 0-24
            day(int): Day to run the function.  0-6, starting with
                Monday.  -1 means run everyday.
        """
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


def ratelimit_retry(retries):
    """ Decorator to return the function

    Automatically retries the function if it encounters
    a RATELIMIT error.

    Args:
        retries(2): How many times to retry.

    Returns:
        Result from the decorated function.
    """
    if retries < 0:
        raise ValueError("retries cannot be negative.")
    def wrapper(func):
        def wrapper_f(*args, **kwargs):
            tries = retries + 1
            attempted = 0
            while attempted < tries:
                try:
                    attempted += 1
                    return func(*args, **kwargs)
                except praw.exceptions.RedditAPIException as e:
                    # RedditAPIException new in praw 7.X, removed in praw 8+
                    for suberr in e.items:
                        if suberr.error_type == "RATELIMIT":
                            delay = re.search("(\d+) (seconds|minutes)", suberr.message)
                            if delay:
                                if delay.group(2) == "minutes":
                                    delay_seconds = int(delay.group(1)) * 60
                                else:
                                    delay_seconds = int(delay.group(1))
                                print("RATE LIMITED!  Waiting {} seconds".format(delay_seconds))
                                time.sleep(delay_seconds)
                                continue
                    # If no RATELIMIT occurred raise the parent exception
                    raise e

        return wrapper_f
    return wrapper