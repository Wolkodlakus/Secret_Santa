from dotenv import load_dotenv
import os
import telegram
from telegram import Update
from telegram.ext import Filters
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup
from telegram import KeyboardButton
import json
import logging
from datetime import datetime, timedelta
#import telegramcalendar

from secret_santa.adminka_secret_santa.models import User_telegram
from secret_santa.adminka_secret_santa.models import Game_in_Santa

states_database = {}

def chunks_generators(buttons, chunks_number):
    for button in range(0, len(buttons), chunks_number):
        yield buttons[button : button + chunks_number]


def keyboard_maker(buttons, number):
    keyboard = list(chunks_generators(buttons, number))
    markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=True
    )
    return markup


def start(update, context):
    chat_id = update.effective_message.chat_id
    buttons = ['Создать игру']
    markup = keyboard_maker(buttons, 1)
    context.bot.send_message(
        chat_id=chat_id,
        text=' Организуй тайный обмен подарками, запусти праздничное настроение!',
        reply_markup=markup,
    )

    return 'GET_CONTACTS'


def get_contacts(update, context):
    user = update.message.from_user
    chat_id = update.effective_message.chat_id
    user_message = update.message.text

    if user_message != 'Создать игру':
        return 'START'

    reply_markup = telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton(
        'Поделиться номером телефона',
        request_contact=True,
    )]])
    context.bot.send_message(
        chat_id=chat_id,
        text=' Введите номер телефона или нажмите кнопку',
        reply_markup=reply_markup,
    )

    context.user_data['creator_first_name'] = user.first_name
    context.user_data['creator_username'] = user.username

    #context.user_data['creator_telephone_number'] =
    return 'TELEPHONE_NUMBER_HANDLER'


def telephone_number_handler(update, context):
    user_input = update.effective_message.text
    chat_id = update.effective_message.chat_id
    if update.message.contact is not None:
        user_phone_number = update.message.contact.phone_number
        context.user_data['creator_telephone_number'] = user_phone_number
    else:
        user_phone_number = update.message.text
        context.user_data['creator_telephone_number'] = user_phone_number
    buttons = ['Подтвердить', 'Ввести другой']
    markup = keyboard_maker(buttons, 1)
    context.bot.send_message(
        chat_id=chat_id,
        text=f'Ваш номер {user_phone_number}?',
        reply_markup=markup,
    )

    return 'CREATE_GAME'


def create_game(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    #if user_message == 'Создать игру':
    context.bot.send_message(
        chat_id=chat_id,
        text='Введите название игры',
    )
    return 'GET_GAME_NAME'
    # else:
    #     return 'CREATE_GAME'


def get_game_name(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    context.user_data['game_name'] = user_message
    buttons = ['До 500 рублей',
               '500-1000 рублей',
               '1000-2000 рублей',
               'Без ограничений',
               ]
    markup = keyboard_maker(buttons, 4)
    context.bot.send_message(
        chat_id=chat_id,
        text='Ограничение стоимости подарка?',
        reply_markup=markup,
    )
    return 'GET_COST_LIMIT'

def get_cost_limit(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    context.user_data['cost_limit'] = user_message
    buttons = ['До 25.12.2021', 'До 31.12.2021']
    markup = keyboard_maker(buttons, 4)
    context.bot.send_message(
        chat_id=chat_id,
        text='Период регистрации участников (до 12.00 МСК)?',
        reply_markup=markup,
    )
    return 'GET_REGISTRATION_PERIOD'


def get_registration_period(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    context.user_data['registration_period'] = user_message

    # здесь будет формирование календаря
    context.bot.send_message(
        chat_id=chat_id,
        text='Дата отправки подарка?',
        #reply_markup=calendar,
    )

    return 'GET_DEPARTURE_DATE'


def get_departure_date(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    context.user_data['departure_date'] = user_message
    buttons = ['Получить ссылку для регистрации']
    markup = keyboard_maker(buttons, 1)
    context.bot.send_message(
        chat_id=chat_id,
        text='Отлично, Тайный Санта уже готовится к раздаче подарков!',
        reply_markup=markup
    )
    return 'CREATE_REGISTRATION_LINK'


def create_registration_link(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    registration_link = 'qwwerty/asdfg/zxcv'
    context.bot.send_message(
        chat_id=chat_id,
        text='Вот ссылка для приглашения участников игры, по которой '
             f'они смогут зарегистрироваться: {registration_link}',
    )
    context.user_data['registration_link'] = registration_link
    print(context.user_data)

def handle_user_reply(update: Update, context: CallbackContext):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
        user_id = update.message.from_user.id

    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply == '/start':
        user_state = 'START'

    else:
        user_state = states_database.get(chat_id)
    states_functions = {
        'START': start,
        'CREATE_GAME': create_game,
        'TELEPHONE_NUMBER_HANDLER': telephone_number_handler,
        'GET_CONTACTS': get_contacts,
        'GET_GAME_NAME': get_game_name,
        'GET_COST_LIMIT': get_cost_limit,
        'GET_REGISTRATION_PERIOD': get_registration_period,
        'GET_DEPARTURE_DATE': get_departure_date,
        'CREATE_REGISTRATION_LINK': create_registration_link,
    }

    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    states_database.update({chat_id: next_state})


def main():
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.contact, handle_user_reply))
    #dispatcher.add_handler(MessageHandler(Filters.location, handle_user_reply))
    #dispatcher.add_handler(CallbackQueryHandler(handle_user_reply))
    updater.start_polling()


if __name__ == '__main__':
    main()
