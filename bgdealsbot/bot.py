from datetime import datetime, date, time as dt_time
import os

import praw

from bgdealsbot.utils import ratelimit_retry


class BgDealsBot(object):
    """A bot script for querying and posting deals"""
    def __init__(self, subreddit):
        """ Contructor

        Args:
            subreddit(str): which subreddit to post to
        """
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
        """ Register a function for querying a deal

        You can add new websites to query by registering
        a new function that queries the website.  It should
        scrape a website and return a bgdealsbot.utils.Deal object

        Args:
            func(functor): A deal querying function

        """
        self.lookups.append(func)

    def query_deals(self):
        """ Runs all registered lookups

        Any lookups that encounter an error
        are logged and reported at the end of the script.
        """
        for lookup in self.lookups:
            try:
                deal = lookup()
                if deal:
                    self.deals.append(deal)
            except Exception as e:
                self.failed_lookups.append((lookup, e))

    def run(self):
        """ Execute the bot"""
        self.query_deals()
        for deal in self.deals:
            if self.is_new(deal):
                self.submit_deal(deal)

        self.check_failures()

    def check_failures(self):
        """Reports failures

        Checks to see if any lookups failed,
        reports, and raises an error.

        Raises:
            RuntimeError: If any lookups failed.
        """
        if self.failed_lookups:
            for item in self.failed_lookups:
                print("{} failed with error:\n\t{}".format(item[0], item[1]))
            raise RuntimeError("BgDealsBot completed with errors!")

    def is_new(self, deal):
        """Has the deal been posted already"""
        today_beginning = datetime.combine(date.today(), dt_time())

        for submission in self.subreddit.new(limit=100):
            # create local time datetime
            creation_time = datetime.fromtimestamp(submission.created_utc)
            if creation_time < today_beginning:
                break
            for link in deal.get_possible_links():
                if link in submission.url or link in submission.selftext:
                    return False

        return True

    @ratelimit_retry(2)
    def submit_deal(self, deal):
        """Submit the deal with retries

        If any deals have a BGG link, it also
        replies to the thread with a comment
        mentioning the BGG link.

        Args:
            deal(bgdealsbot.utils.Deal): The deal to post

        """
        submission = self.subreddit.submit(deal.get_formatted_title(), url=deal.link)
        if deal.bgg_link:
            self.post_details_comment(submission, deal)

    @ratelimit_retry(2)
    def post_details_comment(self, submission, deal):
        """Reply to the deal submission with a BGG link

        Args:
            submission(Submission): The deal's thread submission
            deal(bgdealsbot.utils.Deal): The deal to post
        """
        submission.reply("Game Info: [BGG]({})".format(deal.bgg_link))