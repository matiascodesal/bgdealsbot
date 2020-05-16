from functools import partial, wraps
import os
import re
import time

from bs4 import BeautifulSoup
import praw
import requests


def post_daily_deals(subreddit="boardgamedeals"):
    queries = [get_cardhaus_dotd, get_gamenerdz_dotd]
    deals = []
    for query in queries:
        deals.append(query())


    reddit = praw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'],
                         client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                         user_agent='bgdealsbot-0.0.1 by /u/elpybe',
                         username=os.environ['REDDIT_USER'],
                         password=os.environ['REDDIT_PW'])

    subred = reddit.subreddit(subreddit)
    for deal in deals:
        submission = reddit_call(partial(subred.submit, deal.get_formatted_title(), url=deal.link))
        if deal.bgg_link:
            reddit_call(partial(submission.reply, "Game Info: [BGG]({})".format(deal.bgg_link)))

def ratelimit_retry(retries):
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
                except praw.exceptions.APIException as e:
                    if e.error_type == "RATELIMIT":
                        delay = re.search("(\d+) minutes", e.message)
                        if delay:
                            delay_seconds = float(int(delay.group(1)) * 60)
                            print("RATE LIMITED!  Waiting {} seconds".format(delay_seconds))
                            time.sleep(delay_seconds)
                        else:
                            delay = re.search("(\d+) seconds", e.message)
                            delay_seconds = float(delay.group(1))
                            print("RATE LIMITED!  Waiting {} seconds".format(delay_seconds))
                            time.sleep(delay_seconds)
        return wrapper_f
    return wrapper

@ratelimit_retry(2)
def reddit_call(func):
    print("Running: {}".format(func))
    return func()


def get_cardhaus_dotd():
    url = "https://www.cardhaus.com/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        link = soup.find("img", {"title": "daily-deal-generic-rectangle.png"}).parent['href']
        response = requests.get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            game_name = soup.find("h1", {"class": "productView-title"}).text
            price = soup.find("span", {"class": "price price--withoutTax"})
            price = float(price.text[1:])
            bgg_url = soup.find("div", {"class": "customField--BoardGameGeeks URL"}).dd.text
            deal = Deal(game_name, price, link, "Cardhaus")
            deal.bgg_link = bgg_url
            return deal
        else:
            raise DealQueryError("Error getting Cardhaus game page")
    else:
        raise DealQueryError("Error getting Cardhaus home page")


def get_gamenerdz_dotd():
    url = "https://www.gamenerdz.com/deal-of-the-day"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        first_product = soup.find("ul", {"class": "productGrid"}).findChild()
        game_name = first_product.find("h4", {"class":"card-title"}).a.text
        link = first_product.find("h4", {"class":"card-title"}).a['href']
        price = first_product.find("span", {"class":"price price--withoutTax"}).text
        price = float(price[1:])
        return Deal(game_name, price, link, "GameNerdz")
    else:
        raise DealQueryError("Error getting GameNerdz home page")

def get_miniaturemarket_dotd():
    url = "https://www.miniaturemarket.com/dailydeal/"

def get_borlandia_dotw():
    url = "https://boardlandia.com/collections/deal-of-the-week"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        game_name = soup.find("h2", {"class": "productitem--title"}).a.text
        game_name = game_name.replace("\n", "").strip()
        link = soup.find("h2", {"class": "productitem--title"}).a['href']
        price = soup.find("div", {"class": "price--main"}).span.text
        price = float(price.strip()[2:])
        return Deal(game_name, price, link, "Boardlandia")
    else:
        raise DealQueryError("Error getting Boardlandia home page")

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


class DealQueryError(Exception):
    pass

if __name__ == '__main__':
    post_daily_deals(subreddit="testingground4bots")