# bgdealsbot
Reddit bot that posts daily board game deals to r/boardgamedeals

### Usage
### Configure
Setup the following environment variables:    
```
REDDIT_CLIENT_ID: Your bot id
REDDIT_CLIENT_SECRET: Your bot's secret key    
REDDIT_USER: Your bot account username
REDDIT_PW: Your bot account password
```
### Run
Run on an hourly cron:    
`bgdealsbot.post_daily_deals()` 

### Posts deals from:
- Miniature Market
- Cardhaus
- GameNerdz
- Boardlandia (Weekly)

### Features:
- Posts new deals only if they haven't been posted already
- Scheduled posting
- Adds a link to the game's entry on BoardGameGeek if available.
