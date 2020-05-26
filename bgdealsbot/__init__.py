from bgdealsbot import lookups
from bgdealsbot.bot import BgDealsBot

def post_daily_deals(subreddit="boardgamedeals"):
    bot = BgDealsBot(subreddit)
    bot.register_lookup(lookups.get_cardhaus_dotd)
    bot.register_lookup(lookups.get_gamenerdz_dotd)
    bot.register_lookup(lookups.get_miniaturemarket_dotd)
    bot.register_lookup(lookups.get_boardlandia_dotw)
    bot.run()


if __name__ == '__main__':
    post_daily_deals(subreddit="testingground4bots")