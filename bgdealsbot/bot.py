import os
import re
import sys
import time

import praw

from bgdealsbot.utils import DealQueryError

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


class BgDealsBot(object):
    def __init__(self, subreddit):
        reddit = praw.Reddit(client_id=os.environ['REDDIT_CLIENT_ID'],
                             client_secret=os.environ['REDDIT_CLIENT_SECRET'],
                             user_agent='bgdealsbot-0.0.1 by /u/elpybe',
                             username=os.environ['REDDIT_USER'],
                             password=os.environ['REDDIT_PW'])

        self.subreddit = reddit.subreddit(subreddit)
        self.lookups = []
        self.deals = []
        self.failed_lookups = []

    def register_lookup(self, func):
        self.lookups.append(func)

    def query_deals(self):
        for lookup in self.lookups:
            try:
                self.deals.append(lookup())
            except Exception as e:
                self.failed_lookups.append((lookup, e))

    def run(self):
        self.query_deals()
        for deal in self.deals:
            self.submit_deal(deal)

        self.check_failures()

    def check_failures(self):
        if self.failed_lookups:
            for item in self.failed_lookups:
                print("{} failed with error:\n\t{}".format(item[0], item[1]))
            raise RuntimeError("BgDealsBot completed with errors!")

    @ratelimit_retry(2)
    def submit_deal(self, deal):
        submission = self.subreddit.submit(deal.get_formatted_title(), url=deal.link)
        if deal.bgg_link:
            self.post_details_comment(submission, deal)

    @ratelimit_retry(2)
    def post_details_comment(self, submission, deal):
        submission.reply("Game Info: [BGG]({})".format(deal.bgg_link))