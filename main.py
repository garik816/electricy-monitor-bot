# -*- coding: utf-8 -*-
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from PIL import Image
from io import BytesIO
import urllib3

# Отключение предупреждений о неподтвержденных HTTPS-запросах
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Токен вашего бота
TOKEN = '7382618332:AAEl2u1YAY9yhCZcjLbNOTXiIslTtkhHNHY'

# Включение ведения журнала
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет!')

# Команда для получения и отправки изображения
async def send_image(update: Update, context: CallbackContext) -> None:
    # URL страницы
    url = 'https://www.zoe.com.ua/%D0%B3%D1%80%D0%B0%D1%84%D1%96%D0%BA%D0%B8-%D0%BF%D0%BE%D0%B3%D0%BE%D0%B4%D0%B8%D0%BD%D0%BD%D0%B8%D1%85-%D1%81%D1%82%D0%B0%D0%B1%D1%96%D0%BB%D1%96%D0%B7%D0%B0%D1%86%D1%96%D0%B9%D0%BD%D0%B8%D1%85/'

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        img_tag = soup.find('img', {'class': 'wp-image-378560 aligncenter'})
        if img_tag is None:
            await update.message.reply_text('Не удалось найти изображение.')
            return

        # Поиск максимального качества изображения из атрибута srcset
        srcset = img_tag.get('srcset')
        if srcset:
            max_quality_url = max(srcset.split(', '), key=lambda x: int(x.split(' ')[1][:-1])).split(' ')[0]
        else:
            max_quality_url = img_tag['src']
        
        if not max_quality_url.startswith('http'):
            max_quality_url = url + max_quality_url

        img_response = requests.get(max_quality_url, verify=False)
        img_response.raise_for_status()

        img = Image.open(BytesIO(img_response.content))

        img_file = BytesIO()
        img.save(img_file, format='PNG')
        img_file.name = 'stabilization_graph.png'
        img_file.seek(0)

        await update.message.reply_photo(photo=img_file)

    except Exception as e:
        logger.error(e)
        await update.message.reply_text('Произошла ошибка при получении изображения.')

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("get_image", send_image))

    application.run_polling()

if __name__ == '__main__':
    main()
