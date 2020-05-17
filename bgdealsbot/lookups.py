import requests
from bs4 import BeautifulSoup

from bgdealsbot.utils import Deal, DealQueryError


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
            raise DealQueryError("DealQueryError: Error getting Cardhaus game page")
    else:
        raise DealQueryError("DealQueryError: Error getting Cardhaus home page")


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
        raise DealQueryError("DealQueryError: Error getting GameNerdz home page")


def get_miniaturemarket_dotd():
    url = "https://www.miniaturemarket.com/dailydeal/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        first_product = soup.find("div", {"class": "product-details"})
        link = first_product.a['href']
        game_name = first_product.find("div", {"class": "product-name"}).text
        price = first_product.find("span", {"class": "price"}).text
        price = float(price[1:])
        return Deal(game_name, price, link, "MiniatureMarket")
    else:
        raise DealQueryError("DealQueryError: Error getting MiniatureMarket home page")


def get_boardlandia_dotw():
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
        raise DealQueryError("DealQueryError: Error getting Boardlandia home page")