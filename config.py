import os

BOT_TOKEN = os.getenv('BOT_TOKEN', 'PASTE_YOUR_TOKEN_HERE')

# Optional API token for football-data.org. Set this if you want to
# use the open football API in matches.py.
FOOTBALL_DATA_TOKEN = os.getenv('FOOTBALL_DATA_TOKEN')

HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/91.0.4472.124 Safari/537.36'
    ),
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
}
