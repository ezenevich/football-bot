from __future__ import annotations

from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup

from config import BOT_TOKEN
from news import fetch_all_news
from matches import fetch_all_matches
from transfers import fetch_all_transfers


bot = TeleBot(BOT_TOKEN)


def _main_menu() -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add('📢 Новости', '⚽️ Матчи', '🔄 Трансферы', 'ℹ️ Помощь')
    return markup


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    text = (
        'Привет! Я футбольный бот. Вот что я умею:\n\n'
        '📢 Новости - последние футбольные новости\n'
        '⚽️ Матчи - матчи на сегодня\n'
        '🔄 Трансферы - свежие трансферы\n\n'
        'Выбери интересующий раздел:'
    )
    bot.send_message(message.chat.id, text, reply_markup=_main_menu())


@bot.message_handler(func=lambda m: m.text == '📢 Новости')
def send_news(message):
    news = fetch_all_news()
    response = '📰 Последние футбольные новости:\n\n'
    for site, items in news.items():
        response += f'🔹 {site}\n'
        for item in items:
            response += (
                f"▪️ {item['title']}\n"
                f"🔗 <a href=\"{item['link']}\">Читать...</a>\n\n"
            )
        response += '\n'
    bot.send_message(message.chat.id, response, parse_mode='HTML')


@bot.message_handler(func=lambda m: m.text == '⚽️ Матчи')
def send_matches(message):
    matches = fetch_all_matches()
    if not matches:
        bot.send_message(message.chat.id, '⚠️ Не удалось получить информацию о матчах')
        return
    response = '⚽️ Матчи на сегодня:\n\n'
    for site, items in matches.items():
        response += f'🔹 {site}\n'
        for match in items:
            score = match.get('score', '')
            score_part = f" | {score}" if score and score.lower() != 'vs' else ''
            response += (
                f"⏰ {match['time']}\n"
                f"🏆 {match['tournament']}\n"
                f"{match['teams']}{score_part}\n"
                f"🔗 <a href=\"{match['link']}\">Смотреть...</a>\n\n"
            )
        response += '\n'
    if len(response) > 4000:
        for part in [response[i:i + 4000] for i in range(0, len(response), 4000)]:
            bot.send_message(message.chat.id, part, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, response, parse_mode='HTML')


@bot.message_handler(func=lambda m: m.text == '🔄 Трансферы')
def send_transfers(message):
    transfers = fetch_all_transfers()
    response = '🔄 Последние трансферные слухи:\n\n'
    for site, items in transfers.items():
        response += f'🔹 {site}\n'
        for t in items:
            response += (
                f"👤 {t['player']}\n"
                f"🛫 {t['from']} → 🛬 {t['to']}\n"
                f"💵 {t['value']}\n"
                f"🔗 {t['link']}\n\n"
            )
        response += '\n'
    bot.send_message(message.chat.id, response)


@bot.message_handler(func=lambda m: True)
def handle_unknown(message):
    bot.send_message(
        message.chat.id,
        'Я не понимаю эту команду. Используйте кнопки меню.',
        reply_markup=_main_menu(),
    )


def run():
    print('Бот запущен и готов к работе...')
    bot.infinity_polling()


if __name__ == '__main__':
    run()
