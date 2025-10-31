import os
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

import logging
import requests
import feedparser
import re
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Get Telegram Bot Token from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Google News RSS Feed URLs
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=Ukraine+OR+Russia+OR+Kyiv+OR+Zelensky+OR+Putin+OR+Donbas+OR+Ukrainian+OR+Trump+OR+FPV+OR+offensive+OR+assault+OR+Drone+OR+Russian+OR+strike+OR+missile+OR+Shahed+OR+artillery+OR+ATACMS+OR+Flamingo+OR+frontline+OR+POW+OR+Sanctions+OR+Korea+OR+NATO+OR+ammunition+OR+defense+OR+warfare+OR+military+OR+counteroffensive+OR+nuclear+OR+submarine&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=Україна+OR+Росія+OR+Путін+OR+Трамп+OR+Зеленський+OR+Війська+OR+ФПВ+OR+Наступ+OR+штурм+OR+атака+OR+обстріл+OR+Санкції+OR+Корея+OR+НАТО+OR+ракета+OR+балістична+OR+крилата+OR+шахед+OR+герань+OR+артилерія+OR+атакували+OR+опк+OR+війна+OR+військова+OR+контрнаступ+OR+ядерна&hl=uk&gl=UA&ceid=UA:uk"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

sent_news_links = set()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def escape_markdown_v2(text):
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(r"([{}])".format(re.escape(escape_chars)), r"\\\1", text)

def fetch_latest_news():
    try:
        news_list = []
        for feed_url in RSS_FEEDS:
            response = requests.get(feed_url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            feed = feedparser.parse(response.content)

            for entry in feed.entries:
                title = escape_markdown_v2(entry.title)
                link = escape_markdown_v2(entry.link)

                if link not in sent_news_links:
                    sent_news_links.add(link)
                    news_list.append(f"📌 *{title}*\n🔗 [Read More]({link})")

                if len(news_list) >= 10:
                    return news_list
        return news_list
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching news: {e}")
        return []

async def news_command(update: Update, context: CallbackContext) -> None:
    news = fetch_latest_news()
    if not news:
        await update.message.reply_text("⚠️ No new articles available. Try again later.")
        return
    for article in news:
        await update.message.reply_markdown_v2(article)

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("👋 Hello! Send /news to get the latest news.")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("news", news_command))
    app.run_polling()

if __name__ == "__main__":
    main()
