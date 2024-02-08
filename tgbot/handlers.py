import logging
import telebot
from django.conf import settings
from telebot import types

from .models import Admin, UserBot, News

logger = logging.getLogger("main")

# Вставляем токен бота
bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)


##################################################### CLIENT PART #######################################################################
@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    markup = types.ForceReply(selective=False)
    try:
        if UserBot.objects.get(user_id=user_id):
            bot.send_message(
                message.chat.id,
                f"Привет, {first_name}! \nЭто фитнес-клуб Solevar. \n\nВоспользуйся: \n/help для того, чтобы узнать все возможности бота \n/news чтобы узнать о самых главных новостях нашего клуба.",
                reply_markup=markup,
            )

    except UserBot.DoesNotExist:
        UserBot.objects.create(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        bot.send_message(
            message.chat.id,
            f"Привет, {first_name}! Это компания МАСТЕР GSM ИСТРА. \n\nВоспользуйся /help для подробной информации или /catalog чтобы посмотреть наши товары.",
            reply_markup=markup,
        )


@bot.message_handler(commands=["help"])
def help(message):
    text = "Команды:\n/start - перезапуск бота \n/help - Помощь \n/app - ссылка на наше приложение \n/news - новости нашего проекта"
    bot.send_message(
        message.chat.id,
        f"Приветствую {message.from_user.first_name}\n \n{text}",
        parse_mode="html",
    )


@bot.message_handler(commands=["about_us"])
def help(message):
    markup = types.ForceReply(selective=False)
    text = "Компания - МАСТЕР GSM ИСТРА. \n\nНОВЫЕ ТОПОВЫЕ ТЕЛЕФОНЫ ПО РАЗУМНЫМ ЦЕНАМ! ДЛЯ ЗАКАЗА ПИШИТЕ СООБЩЕНИЯ В ЛИЧКУ.  \n\nВнимание!!! Гарантия на продукцию Apple 5 ДНЕЙ (проверка заводского брака). Срок гарантии указан с даты покупки телефона. При наличии косметических дефектов гарантия распространяется только на неактивированные устройства. При наличии брака принимаем устройства ТОЛЬКО в первоначальном виде. \n Наш телефон: 89774532753 \nМы ВКонтакте: https://vk.com/id224104632"
    bot.send_message(message.chat.id, text=text, parse_mode="html", reply_markup=markup)


@bot.message_handler(commands=["news"])
def news(message):
    news = News.objects.all()
    if news.count() > 0:
        for new in news:
            if new.photo is not None:
                photo_path = new.photo.path
                caption = new.text
                send_photo_with_caption(bot, message.chat.id, photo_path, caption)
            else:
                bot.send_message(message.chat.id, f"{new.text}")
    else:
        bot.send_message(message.chat.id, f"Новостей пока нет!")


def send_photo_with_caption(bot, chat_id, photo_path, caption):
    with open(photo_path, "rb") as photo:
        bot.send_photo(chat_id, photo, caption=caption)


@bot.message_handler(commands=["app"])
def app(message):
    bot.send_message(
        message.chat.id, "Скачайте наше бесплатное приложение по ссылке: https.."
    )


# ##################################################### ADMIN PART #######################################################################
# Рассылка всем пользователям от лица админа
@bot.message_handler(commands=["send_message"])
def send_message(message):
    user = Admin.objects.filter(UUID=int(message.chat.id)).first()
    if user:
        markup = types.ForceReply(selective=False)
        bot.send_message(
            message.chat.id,
            "Введите текст сообщения, которое хотите отправить:",
            reply_markup=markup,
        )
        bot.register_next_step_handler(message, process_text)
    else:
        bot.send_message(message.chat.id, "Вы не администратор")


def process_text(message):
    text = message.text.strip()
    markup = types.ForceReply(selective=False)
    bot.send_message(
        message.chat.id,
        "Теперь отправьте фотографию для этого сообщения: \nЕсли не хотите то '-'",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_photo, text)


def process_photo(message, text):
    if message.photo:
        photo = message.photo[-1].file_id  # Получаем file_id фотографии
        users = UserBot.objects.all()

        for user in users:
            try:
                bot.send_photo(user.user_id, photo, caption=text)
                News.objects.create(text=text, photo=photo)
            except Exception as e:
                print(f"Произошла ошибка {e}")
        else:
            bot.send_message(message.chat.id, "Рассылка завершена")
    else:
        users = UserBot.objects.all()

        for user in users:
            try:
                bot.send_message(user.user_id, text)
                News.objects.create(
                    text=text,
                )
            except Exception as e:
                print(f"Произошла ошибка {e}")

# Добавление администратора
@bot.message_handler(commands=["admin_add"])
def admin_add(message):
    user = Admin.objects.filter(UUID=int(message.chat.id)).first()
    if user:
        markup = types.ForceReply(selective=False)
        bot.send_message(
            message.chat.id,
            "Введите ID аккаунта, нового администратора",
            reply_markup=markup,
        )
        bot.register_next_step_handler(message, process_text_admin)
    else:
        bot.send_message(message.chat.id, "Вы не администратор")


def process_text_admin(message):
    id_admin = message.text.strip()
    markup = types.ForceReply(selective=False)
    try:
        Admin.objects.create(UUID=id_admin)
        bot.send_message(
            message.chat.id,
            "Отлично! Админ добавлен",
            reply_markup=markup,
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            "Админ уже создан или ID ошибочный",
            reply_markup=markup,
        )


# Ловит любое сообщение
@bot.message_handler()
def info(message):
    if message.text.lower() == "id":
        bot.reply_to(message, f"ID: {message.from_user.id}")
        admin_id = Admin.objects.filter(UUID=message.from_user.id)
        if admin_id:
            bot.reply_to(
                message,
                f"Вы администратор! Вам доступны особенные команды. \n\n/admin_add - Добавление админа\n\n/product_add - Добавление товара \n\n/price_up_with_price - Повышение цены по определенной цене \n\n/price_up - Повышение цены по определенной категории и бренду \n\n/price_up_all - Повышение цены для всех товаров \n\n/price_down - Понижение цены по определенной категории или вендору  \n\n/price_down_with_price - Понижение цены по определенной цене \n\n/send_message - Рассылка сообщения всем юзерам \n\n/updateList - изменения всего прайса одним файлом",
            )
    bot.reply_to(message, f"Лучше закажите у нас!")


def start_bot():
    bot.polling(non_stop=True)


def stop_bot():
    bot.stop_polling()