import os

BOT_TOKEN = os.getenv('BOT_TOKEN', '7428021954:AAGYs1GH45notSeSg3-3YAGeNnLj118-ESk')

# Optional API token for football-data.org. Set this if you want to
# use the open football API in matches.py.

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/91.0.4472.124 Safari/537.36'
    ),
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}
