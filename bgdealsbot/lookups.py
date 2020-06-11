import requests
from bs4 import BeautifulSoup

from bgdealsbot.utils import Deal, DealQueryError, schedule


# New deal really at 12AM (EST), but 6AM is more user-friendly
@schedule(6)
def get_cardhaus_dotd():
    """ Cardhaus for a daily deal

    Returns:
        (Deal) a deal object

    Raises:
        (DealQueryError) If webpage request fails.
    """
    url = "https://www.cardhaus.com/"
    response = requests.get(url, headers={'Cache-Control': 'no-cache'})
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        link = soup.find("img", {"title": "daily-deal-generic-rectangle.png"}).parent['href']
        response = requests.get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            game_name = soup.find("h1", {"class": "productView-title"}).text
            price = soup.find("span", {"class": "price price--withoutTax"})
            price = float(price.text[1:])
            bgg_url_div = soup.find("div", {"class": "customField--BoardGameGeeks URL"})
            if bgg_url_div:
                bgg_url = bgg_url_div.dd.text
            else:
                bgg_url = ""
            deal = Deal(game_name, price, link, "Cardhaus")
            deal.bgg_link = bgg_url
            return deal
        else:
            raise DealQueryError("DealQueryError: Error getting Cardhaus game page")
    else:
        raise DealQueryError("DealQueryError: Error getting Cardhaus home page")

@schedule(11)
def get_gamenerdz_dotd():
    """ GameNerdz for a daily deal

        Returns:
            (Deal) a deal object

        Raises:
            (DealQueryError) If webpage request fails.
        """
    url = "https://www.gamenerdz.com/deal-of-the-day"
    response = requests.get(url, headers={'Cache-Control': 'no-cache'})
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        first_product = soup.find("ul", {"class": "productGrid"}).findChild()
        game_name = first_product.find("h4", {"class":"card-title"}).a.text
        link = first_product.find("h4", {"class":"card-title"}).a['href']
        price = first_product.find("span", {"class":"price price--withoutTax"}).text
        price = float(price[1:])
        deal = Deal(game_name, price, link, "GameNerdz")
        deal.alt_links.append("https://www.gamenerdz.com/deal-of-the-day")
        return deal
    else:
        raise DealQueryError("DealQueryError: Error getting GameNerdz home page")

@schedule(9)
def get_miniaturemarket_dotd():
    """ MiniatureMarket for a daily deal

    Returns:
        (Deal) a deal object

    Raises:
        (DealQueryError) If webpage request fails or the deal has expired
    """
    url = "https://www.miniaturemarket.com/dailydeal/"
    response = requests.get(url, headers={'Cache-Control': 'no-cache'})
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        first_product = soup.find("div", {"class": "product-details"})
        link = first_product.a['href']
        game_name = first_product.find("div", {"class": "product-name"}).text
        if game_name == "":
            raise DealQueryError("DealQueryError: The deal has already expired.")
        price = first_product.find("span", {"class": "price"}).text
        price = float(price[1:])
        deal = Deal(game_name, price, link, "MiniatureMarket")
        deal.alt_links.append("https://www.miniaturemarket.com/dailydeal")
        return deal
    else:
        raise DealQueryError("DealQueryError: Error getting MiniatureMarket home page")

# day=Thursday
@schedule(4, day=3)
def get_boardlandia_dotw():
    """ Boardlandia for a deal of the week

    Returns:
        (Deal) a deal object

    Raises:
        (DealQueryError) If webpage request fails.
    """
    url = "https://boardlandia.com/collections/deal-of-the-week"
    response = requests.get(url, headers={'Cache-Control': 'no-cache'})
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        game_name = soup.find("h2", {"class": "productitem--title"}).a.text
        game_name = game_name.replace("\n", "").strip()
        link = soup.find("h2", {"class": "productitem--title"}).a['href']
        if link.startswith("/"):
            link = "https://boardlandia.com" + link
        price = soup.find("div", {"class": "price--main"}).span.text
        price = float(price.strip()[2:])
        deal = Deal(game_name, price, link, "Boardlandia", deal_type="DotW")
        deal.alt_links.append("https://boardlandia.com/collections/deal-of-the-week")
        return deal
    else:
        raise DealQueryError("DealQueryError: Error getting Boardlandia home page")