import requests
import smtplib
from os import environ
from datetime import timedelta, date

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla"
# Alert email will be sent is the price changes by alert threshold
ALERT_THRESHOLD = 0.03
# Set your own API keys and email credentials as environmental variables
API_KEY_ALPHAVANTAGE = environ.get('AV_KEY')
API_KEY_API_NEWS = environ.get('NEWS_KEY')
FROM_EMAIL = environ.get('FROM_EMAIL')
TO_EMAIL = environ.get('TO_EMAIL')
APP_PASSWORD = environ.get('APP_PASSWORD')


def get_stock_price_difference() -> float:
    """Make an API request to AlphaVantage for the current and previous day stock price - returns a
    relative difference as float. """
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={STOCK_NAME}&apikey={API_KEY_ALPHAVANTAGE}'
    r = requests.get(url)
    r.raise_for_status()
    r_json = r.json()
    current_price = float(r_json['Global Quote']['05. price'])
    yesterday_price = float(r_json['Global Quote']['08. previous close'])
    abs_stock_price_change_percent = (current_price - yesterday_price) / yesterday_price
    return abs_stock_price_change_percent


def get_news_articles() -> str:
    """Make a news article request from API News for articles form the yesterday and today. Returns top 3 stories
    with url links as a string """
    todays_date = date.today()
    yesterdays_date = date.today() - timedelta(days=1)
    url = f'https://newsapi.org/v2/top-headlines?language=en&q={COMPANY_NAME}&from={yesterdays_date}&to={todays_date}&apiKey={API_KEY_API_NEWS}'
    r_json = requests.get(url).json()
    top3_articles_summary = []
    for i in range(min(3, len(r_json['articles']))):
        top3_articles_summary.append(f'\nArticle {i + 1}:')
        top3_articles_summary.append(f"Title: {r_json['articles'][i]['title']}")
        top3_articles_summary.append(f"Decription: {r_json['articles'][i]['description']}")
        top3_articles_summary.append(r_json['articles'][i]['url'])
    return '\n'.join(top3_articles_summary).strip()


def send_email_with_top3_news_articles(price_diff):
    """Send an email alert with top 3 news articles summary"""
    # UnicodeEncodeError: 'ascii' codec can't encode character '\U0001f53a' in position 15: ordinal not in range(128)
    # message_title = f'{STOCK_NAME}: 🔺{abs(price_diff):.0%}' if price_diff > 0 else \
    #     f'{STOCK_NAME}: 🔻{abs(price_diff):.0%} '
    message_title = f'{STOCK_NAME} is up: {abs(price_diff):.0%}' if price_diff > 0 else \
        f'{STOCK_NAME} is down: {abs(price_diff):.0%} '
    message_body = get_news_articles()
    print(message_body)
    connection = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    connection.login(user=FROM_EMAIL, password=APP_PASSWORD)
    connection.sendmail(FROM_EMAIL, to_addrs=TO_EMAIL, msg=f"subject: {message_title}\n\n{message_body}")
    connection.close()

# Driver code

stock_price_diff = get_stock_price_difference()
if stock_price_diff > ALERT_THRESHOLD:
    send_email_with_top3_news_articles(stock_price_diff)
