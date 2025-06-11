import requests
from bs4 import BeautifulSoup
import telebot
from telebot.types import ReplyKeyboardMarkup

BOT_TOKEN = '7428021954:AAGYs1GH45notSeSg3-3YAGeNnLj118-ESk'
bot = telebot.TeleBot(BOT_TOKEN)

# Настройки для парсинга
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
}


def get_main_menu():
    """Создает главное меню с кнопками"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('📢 Новости', '⚽️ Матчи', '🔄 Трансферы', 'ℹ️ Помощь')
    return markup


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Обработчик команд start и help"""
    welcome_text = """
Привет! Я футбольный бот. Вот что я умею:

📢 Новости - последние футбольные новости
⚽️ Матчи - матчи на сегодня
🔄 Трансферы - свежие трансферы

Выбери интересующий раздел:
"""
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_main_menu())


def get_news_from_championat():
    """Парсим новости с championat.com"""
    try:
        url = "https://www.championat.com/football/"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        news = []
        for item in soup.select('.news-item__content')[:5]:
            title = item.select_one('.news-item__title')
            link = item.find('a')['href']
            if title and link:
                news.append({
                    'title': title.get_text(strip=True),
                    'link': f"https://www.championat.com{link}" if link.startswith('/') else link
                })
        return news
    except Exception as e:
        print(f"Ошибка парсинга новостей: {e}")
        return [{'title': 'Не удалось загрузить новости', 'link': '#'}]


def get_matches_from_sportsru():
    """Парсим матчи с sports.ru"""
    try:
        url = "https://www.sports.ru/stat/football/center/today/"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')

        matches = []

        # Ищем все блоки с матчами
        for match in soup.select('.stat-results__row')[:15]:  # Берем первые 15 матчей
            # Время матча
            time = match.select_one('.stat-results__time')
            time = time.get_text(strip=True) if time else "Время не указано"

            # Команды
            teams = match.select('.stat-results__team-name')
            if len(teams) >= 2:
                home_team = teams[0].get_text(strip=True)
                away_team = teams[1].get_text(strip=True)
            else:
                continue

            # Счет
            score = match.select_one('.stat-results__count')
            score = score.get_text(strip=True) if score else "vs"

            # Турнир
            tournament = match.select_one('.stat-results__tournament')
            tournament = tournament.get_text(strip=True) if tournament else "Турнир не указан"

            # Ссылка на матч
            link = match.find('a')
            link = f"https://www.sports.ru{link['href']}" if link and link.has_attr('href') else "#"

            matches.append({
                'time': time,
                'teams': f"{home_team} - {away_team}",
                'score': score,
                'tournament': tournament,
                'link': link
            })

        return matches

    except Exception as e:
        print(f"Ошибка парсинга матчей: {e}")
        return [{
            'time': "-",
            'teams': "Не удалось загрузить матчи",
            'score': "-",
            'tournament': "-",
            'link': "#"
        }]

    def get_transfers_from_transfermarkt():
        try:
            url = "https://www.transfermarkt.com/neueste-transfergeruechte/geruechte"

    r = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')

    transfers = []
    for row in soup.select('.odd, .even')[:5]:
        player = row.select_one('.spielprofil_tooltip')
        clubs = row.select('.vereinprofil_tooltip')
        value = row.select_one('.rechts.hauptlink')

        if player and len(clubs) >= 2:
            transfers.append({
                'player': player.text.strip(),
                'from': clubs[0].text.strip(),
                'to': clubs[1].text.strip(),
                'value': value.text.strip() if value else '?',
                'link': f"https://www.transfermarkt.com{player['href']}"
            })
    return transfers

except Exception as e:
print(f"Ошибка парсинга трансферов: {e}")
return [{
    'player': "Нет данных о трансферах",
    'from': "-",
    'to': "-",
    'value': "-",
    'link': "#"
}]


@bot.message_handler(func=lambda m: m.text == '📢 Новости')
def send_news(message):
    """Отправляем новости"""


news = get_news_from_championat()
response = "📰 Последние футбольные новости:\n\n" + "\n\n".join(
    f"▪️ {item['title']}\n🔗 {item['link']}" for item in news
)
bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda m: m.text == '⚽️ Матчи')
def send_matches(message):
    """Отправляем матчи"""
    matches = get_matches_from_sportsru()

    if not matches or 'Не удалось' in matches[0]['teams']:
        bot.send_message(message.chat.id, "⚠️ Не удалось получить информацию о матчах")
        return

    response = "⚽️ Матчи на сегодня:\n\n"

    for match in matches:
        response += (
            f"⏰ {match['time']}\n"
            f"🏆 {match['tournament']}\n"
            f"🔹 {match['teams']}\n"
            f"📊 Счет: {match['score']}\n"
            f"🔗 {match['link']}\n\n"
        )

    # Разбиваем на части если сообщение слишком длинное
    if len(response) > 4000:
        parts = [response[i:i + 4000] for i in range(0, len(response), 4000)]
        for part in parts:
            bot.send_message(message.chat.id, part)
    else:
        bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda m: m.text == '🔄 Трансферы')
def send_transfers(message):
    """Отправляем трансферы"""
    transfers = get_transfers_from_transfermarkt()
    response = "🔄 Последние трансферные слухи:\n\n" + "\n\n".join(
        f"👤 {t['player']}\n"
        f"🛫 {t['from']} → 🛬 {t['to']}\n"
        f"💵 Стоимость: {t['value']}\n"
        f"🔗 {t['link']}"
        for t in transfers
    )
    bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda m: True)
def handle_unknown(message):
    """Обработчик неизвестных команд"""
    bot.send_message(message.chat.id, "Я не понимаю эту команду. Используйте кнопки меню.",
                     reply_markup=get_main_menu())


if name == 'main':
    print("Бот запущен и готов к работе...")
    bot.infinity_polling()
