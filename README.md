# Football Bot

This Telegram bot provides recent football news, today's matches and transfer rumours. Data is collected from several public sources.

## Open football API support

The bot can optionally fetch match information from the [football-data.org](https://www.football-data.org/) API. To enable it, obtain a free API token and set the `FOOTBALL_DATA_TOKEN` environment variable when running the bot.

## Running the bot

Set the `BOT_TOKEN` with your Telegram bot token and run `bot.py`:

```bash
BOT_TOKEN=... FOOTBALL_DATA_TOKEN=... python bot.py
```
