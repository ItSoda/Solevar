import logging

import telebot
from django.conf import settings
from telebot import types

from .models import Admin, News, UserBot

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
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text='Новости', callback_data='/news'))
    markup.add(types.InlineKeyboardButton(text='Скачать приложение', callback_data='/apps'))
    markup.add(types.InlineKeyboardButton(text='FAQ', callback_data='/faq'))
    markup.add(types.InlineKeyboardButton(text='Перезапустить бота', callback_data='/start'))

    try:
        if UserBot.objects.get(user_id=user_id):
            bot.send_message(
                message.chat.id,
                f"Привет, {first_name}! \nЭто фитнес-клуб Solevar! Что вас интересует?",
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
            f"Привет, {first_name}! \nЭто фитнес-клуб Solevar! Что вас интересует?",
            reply_markup=markup,
        )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == '/faq':
        faq(call.message)
    if call.data == '/apps':
        apps(call.message)
    if call.data == '/news':
        news(call.message)
    if call.data == '/start':
        handle_start(call.message)
    

@bot.message_handler(commands=["faq"])
def faq(message):
    text = "Команды:\n/start - перезапуск бота \n/help - Помощь \n/app - ссылка на наше приложение \n/news - новости нашего проекта"
    bot.send_message(
        message.chat.id,
        f"Приветствую {message.from_user.first_name}\n \n{text}",
        parse_mode="html",
    )


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


@bot.message_handler(commands=["apps"])
def apps(message):
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
            "Введите заголовок сообщения, которое хотите отправить:",
            reply_markup=markup,
        )
        bot.register_next_step_handler(message, process_title)
    else:
        bot.send_message(message.chat.id, "Вы не администратор")


def process_title(message):
    title = message.text.strip()
    markup = types.ForceReply(selective=False)
    bot.send_message(
        message.chat.id,
        "Теперь отправьте текст для этого сообщения",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_text, title)


def process_text(message, title):
    text = message.text.strip()
    markup = types.ForceReply(selective=False)
    bot.send_message(
        message.chat.id,
        "Теперь отправьте фотографию для этого сообщения: \nЕсли не хотите то '-'",
        reply_markup=markup,
    )
    bot.register_next_step_handler(message, process_photo, text, title)


def process_photo(message, text, title):
    if message.photo:
        photo = message.photo[-1].file_id  # Получаем file_id фотографии
        users = UserBot.objects.all()

        for user in users:
            try:
                bot.send_photo(user.user_id, photo, caption=text)
            except Exception as e:
                print(f"Произошла ошибка {e}")
        else:
            bot.send_message(message.chat.id, "Рассылка завершена")
            News.objects.create(text=text, photo=photo, title=title)
    else:
        users = UserBot.objects.all()

        for user in users:
            try:
                bot.send_message(user.user_id, text)
                News.objects.create(
                    text=text,
                    title=title,
                )
            except Exception as e:
                print(f"Произошла ошибка {e}")
        else:
            News.objects.create(text=text, title=title,)


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
                f"Вы администратор! Вам доступны особенные команды. \n\nsend_message - Добавление новости",
            )
    bot.reply_to(message, f"Лучше закажите у нас!")


def start_bot():
    bot.polling(non_stop=True)


def stop_bot():
    bot.stop_polling()
