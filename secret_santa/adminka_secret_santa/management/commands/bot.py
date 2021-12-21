import logging
from dotenv import load_dotenv
import os
import re
import sys
import telegram
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import ConversationHandler
from telegram.utils.request import Request
from telegram.ext import Filters
from telegram.ext import CallbackContext
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, MessageHandler
from telegram import ReplyKeyboardMarkup
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
import phonenumbers
from random import randint
from typing import Optional
import random
from datetime import datetime
from django.utils import timezone

#import django
#os.environ['DJANGO_SETTINGS_MODULE'] = 'secret_santa.settings'
#django.setup()
from django.core.management.base import BaseCommand
from adminka_secret_santa.models import Game_in_Santa, User_telegram, Wishlist, Toss_up, Interest

logger = logging.getLogger('logger_main')

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

states_database = {}


def create_test_game(context):
    context.user_data['creator_telephone_number'] = '+79528949027'
    context.user_data['creator_first_name'] = 'Евгений'
    context.user_data['creator_username'] = 'OxFFFFFFF'
    context.user_data['game_name'] = 'Тайный Санта'
    context.user_data['cost_limit'] = '500-1000 рублей'
    context.user_data['registration_period'] = '31.12.2021'
    context.user_data['departure_date'] = '15.01.2022'
    context.user_data['game_id'] = 123456

def load_to_context(id_game,context):
    try:
        game = Game_in_Santa.objects.get(id_game=id_game)
        context.user_data['game_id'] = id_game
        context.user_data['creator_telephone_number'] = game.organizer.organizer.telephone_number
        context.user_data['creator_first_name'] = game.organizer.name
        context.user_data['creator_username'] = game.organizer.username
        context.user_data['game_name'] = game.name
        context.user_data['cost_limit'] = game.price_range
        context.user_data['registration_period'] = game.last_day_and_time_of_registration
        context.user_data['departure_date'] = game.draw_time

    except ObjectDoesNotExist:
        pass

def save_new_game(context):
    print(context.user_data)
    print('='*80)
    game = Game_in_Santa.objects.create(
        id_game=context.user_data['game_id'],
        name_game=context.user_data['game_name'],
        price_range=context.user_data['cost_limit'],
        last_day_and_time_of_registration=context.user_data['registration_period'],
        draw_time=context.user_data['departure_date'],
        organizer=User_telegram.objects.get(telephone_number=context.user_data['creator_telephone_number']),
    )
    game.save()


def save_creator_user(update,context):
    chat_id = update.effective_message.chat_id
    user = User_telegram.objects.get(external_id= chat_id)
    #for item in context.user_data['wish_list']:
    #    user.wishlist.create(name=item)

    #user.letter = context.user_data['letter']
    user.name = context.user_data['creator_first_name']
    user.user_name = context.user_data['creator_username']
    user.telephone_number = context.user_data['creator_telephone_number']
    #user.interest_user =
    #user.wishes_user =
    user.save()

def save_player_user (update,context):
    chat_id = update.effective_message.chat_id
    user = User_telegram.objects.get(external_id= chat_id)
    for item in context.user_data['wish_list']:
        user.wishlist.create(name=item)

    user.letter = context.user_data['letter']
    user.name = context.user_data['player_first_name']
    user.user_name = context.user_data['player_username']
    user.telephone_number = context.user_data['player_telephone_number']
    user.games.objects.add(Game_in_Santa.objects.filter(id_game=context.user_data['game_id']))
    #user.interest_user =
    #user.wishes_user =
    user.save()



def chunks_generators(buttons, chunks_number):
    for button in range(0, len(buttons), chunks_number):
        yield buttons[button: button + chunks_number]


def keyboard_maker(buttons, number):
    keyboard = list(chunks_generators(buttons, number))
    markup = ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=True
    )
    return markup


def start(update, context):
    chat_id = update.effective_message.chat_id
    #create_test_game(context)

    p, _ = User_telegram.objects.get_or_create(
        external_id = chat_id,
        defaults = {
            'name': '',
            'last_name': '',
            'username': '',
            'telephone_number': ''
        }
    )    
    game_id = update.message.text[7:]
    if game_id:
        print('game_id', game_id)
        load_to_context(game_id,context)
        #context.user_data['game_id'] = game_id
        buttons = ['Продолжить']
        markup = keyboard_maker(buttons, 1)
        context.bot.send_message(
            chat_id=chat_id,
            text=' Вы присоединились к игре! Поздравляем!',
            reply_markup=markup,
        )

        return 'SHOW_GAME_INFO'
    chat_id = update.effective_message.chat_id

    buttons = ['Создать игру', 'Вступить в игру']
    markup = keyboard_maker(buttons, 2)
    context.bot.send_message(
        chat_id=chat_id,
        text=' Организуй или присоединись к тайному обмену подарками,'
             ' запусти праздничное настроение!',
        reply_markup=markup,
    )

    return 'SELECT_BRANCH'


def select_branch(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    if user_message == 'Создать игру':
        reply_markup = telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton(
            'Поделиться номером телефона',
            request_contact=True,
        )]])

        context.bot.send_message(
            chat_id=chat_id,
            text='Введи свой номер телефона или нажми кнопку',
            reply_markup=reply_markup,
        )
        return 'GET_CREATOR_CONTACT'

    if user_message == 'Вступить в игру':
        context.bot.send_message(
            chat_id=chat_id,
            text='Введите 6-значный идентификатор игры',
        )
        return 'CHECK_GAME'


def get_player_name(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    context.user_data['player_name'] = user_message

    buttons = ['Пропустить']
    markup = keyboard_maker(buttons, 1)
    context.bot.send_message(
        chat_id=chat_id,
        text=' Введи свой список желаний по одной вещи\n'
             'или пропусти шаг',
        reply_markup=markup,
    )
    context.user_data['wish_list'] = []
    return 'GET_WISH_LIST'


def get_wish_list(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    if user_message == 'Завершить' or user_message == 'Пропустить':
        buttons = ['Пропустить']
        markup = keyboard_maker(buttons, 1)
        context.bot.send_message(
            chat_id=chat_id,
            text='Теперь напиши письмо своему Санте или пропусти шаг',
            reply_markup=markup,
        )
        return 'GET_LETTER_FOR_SANTA'
    context.user_data['wish_list'].append(user_message)
    #print(context.user_data['wish_list'])
    buttons = ['Завершить']
    markup = keyboard_maker(buttons, 1)
    context.bot.send_message(
        chat_id=chat_id,
        text='Желание добавлено. Введи еще или нажми кнопку',
        reply_markup=markup,
    )
    return 'GET_WISH_LIST'


def get_letter_for_santa(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    context.user_data['letter'] = user_message
    buttons = ['Создать игру', 'Вступить в игру']
    markup = keyboard_maker(buttons, 2)
    context.bot.send_message(
        chat_id=chat_id,
        text=f'Превосходно, ты в игре! {context.user_data["departure_date"]}'
             ' мы проведем жеребьевку и ты узнаешь имя и контакты своего '
             'тайного друга. Ему и нужно будет подарить подарок!',
        reply_markup=markup,
    )
    print(context.user_data)

    return 'SELECT_BRANCH'


def check_telephone_number(number):
    try:
        parsed_number = phonenumbers.parse(number)
        if phonenumbers.is_valid_number(parsed_number):
            correct_number = f'+{parsed_number.country_code}' \
                             f'{parsed_number.national_number}'
            return correct_number
        else:
            return
    except:
        return


def check_game(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    print(int(user_message))
    print(int(context.user_data.get('game_id')))
    try:
        game = Game_in_Santa.objects.get(id_game=int(user_message))
        buttons = ['Продолжить']
        markup = keyboard_maker(buttons, 1)
        context.bot.send_message(
            chat_id=chat_id,
            text=' Вы присоединились к игре! Поздравляем!',
            reply_markup=markup,
        )
        context.user_data['game_id'] = game.id_game
        return 'SHOW_GAME_INFO'
    except ObjectDoesNotExist:
        buttons = ['Создать игру', 'Вступить в игру']
        markup = keyboard_maker(buttons, 2)
        context.bot.send_message(
            chat_id=chat_id,
            text='Игры с таким идентификатором не существует',
            reply_markup=markup,
        )
        return 'SELECT_BRANCH'
    """
    if int(user_message) == int(context.user_data.get('game_id')): #проверка есть ли игра с таким id
        buttons = ['Продолжить']
        markup = keyboard_maker(buttons, 1)
        context.bot.send_message(
            chat_id=chat_id,
            text=' Вы присоединились к игре! Поздравляем!',
            reply_markup=markup,
        )
        return 'SHOW_GAME_INFO'
    else:
        buttons = ['Создать игру', 'Вступить в игру']
        markup = keyboard_maker(buttons, 2)
        context.bot.send_message(
            chat_id=chat_id,
            text='Игры с таким идентификатором не существует',
            reply_markup=markup,
        )
        return 'SELECT_BRANCH'
    """

def show_game_info(update, context):
    chat_id = update.effective_message.chat_id

    context.bot.send_message(
        chat_id=chat_id,
        text=f'Название игры: {context.user_data["game_name"]}\n'
             f'Ограничение стоимости: {context.user_data["cost_limit"]}\n'
             f'Период регистрации до: {context.user_data["registration_period"]}\n'
             f'Дата отправки подарков: {context.user_data["departure_date"]}'
    )
    reply_markup = telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton(
        'Поделиться номером телефона',
        request_contact=True,
    )]])

    context.bot.send_message(
        chat_id=chat_id,
        text='Введи свой номер телефона или нажми кнопку',
        reply_markup=reply_markup,
    )
    return 'GET_PLAYER_CONTACT'


def get_creator_contact(update, context):
    user = update.message.from_user
    chat_id = update.effective_message.chat_id
    if update.message.contact is not None:
        user_phone_number = update.message.contact.phone_number
        context.user_data['creator_telephone_number'] = user_phone_number
    else:
        user_phone_number = update.message.text
        correct_phone_number = check_telephone_number(user_phone_number)
        if not correct_phone_number:
            reply_markup = telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton(
                'Поделиться номером телефона',
                request_contact=True,
            )]])

            context.bot.send_message(
                chat_id=chat_id,
                text='Неверно введен номер!\n'
                     'Введи свой номер телефона в формате '
                     '"+7 (123) 456-78-90" или нажми кнопку',
                reply_markup=reply_markup,
            )
            return 'GET_CREATOR_CONTACT'
        context.user_data['creator_telephone_number'] = user_phone_number
        if correct_phone_number != user_phone_number:
            context.bot.send_message(
                chat_id=chat_id,
                text=f'Ваш номер телефона: {correct_phone_number}',
            )

    context.user_data['creator_first_name'] = user.first_name
    context.user_data['creator_username'] = user.username
    context.bot.send_message(
        chat_id=chat_id,
        text='Введите название игры',
        reply_markup=telegram.ReplyKeyboardRemove(),
    )
    save_creator_user(update,context)
    return 'GET_GAME_NAME'


def get_player_contact(update, context):
    user = update.message.from_user
    chat_id = update.effective_message.chat_id
    if update.message.contact is not None:
        user_phone_number = update.message.contact.phone_number
        context.user_data['player_telephone_number'] = user_phone_number
    else:
        user_phone_number = update.message.text
        correct_phone_number = check_telephone_number(user_phone_number)
        if not correct_phone_number:
            reply_markup = telegram.ReplyKeyboardMarkup([[telegram.KeyboardButton(
                'Поделиться номером телефона',
                request_contact=True,
            )]])

            context.bot.send_message(
                chat_id=chat_id,
                text='Неверно введен номер!\n'
                     'Введи свой номер телефона в формате '
                     '"+7 (123) 456-78-90" или нажми кнопку',
                reply_markup=reply_markup,
            )
            return 'GET_PLAYER_CONTACT'
        context.user_data['player_telephone_number'] = correct_phone_number
        if correct_phone_number != user_phone_number:
            context.bot.send_message(
                chat_id=chat_id,
                text=f'Ваш номер телефона: {correct_phone_number}',
            )

    context.user_data['player_first_name'] = user.first_name
    context.user_data['player_username'] = user.username

    buttons = [user.first_name]
    markup = keyboard_maker(buttons, 1)
    context.bot.send_message(
        chat_id=chat_id,
        text='Введите ваше имя в игре или нажмите кнопку',
        reply_markup=markup,
    )
    save_player_user(update,context)
    return 'GET_PLAYER_NAME'


def get_game_name(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text

    context.user_data['game_name'] = user_message
    buttons = ['До 500 рублей',
               '500-1000 рублей',
               '1000-2000 рублей',
               ]
    markup = keyboard_maker(buttons, 3)
    context.bot.send_message(
        chat_id=chat_id,
        text='Введите ограничение стоимости подарка '
             'или нажмите одну из кнопок',
        reply_markup=markup,
    )
    return 'GET_COST_LIMIT'


def get_cost_limit(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text
    context.user_data['cost_limit'] = user_message
    context.bot.send_message(
        chat_id=chat_id,
        text='Введите дату окончания регистрации участников'
             ' (до 12.00 МСК) в формате ДД-ММ-ГГГГ, например 31-12-2021',
        reply_markup=telegram.ReplyKeyboardRemove()
    )
    return 'GET_REGISTRATION_PERIOD'


def get_registration_period(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text

    try:
        current_tz = timezone.get_current_timezone()
        registration_period = datetime.strptime(user_message, '%d-%m-%Y')
        registration_period_tz =current_tz.localize(registration_period)
        #print(f'registration_period: {registration_period}')
        #print(f'registration_period_tz: {registration_period_tz}')
        #print(f'datetime.now() {datetime.now()}')
        #print(f'timezone.now() {timezone.now()}')
        if registration_period_tz < timezone.now():
            context.bot.send_message(
                chat_id=chat_id,
                text='Прошлая или текущая дата не может быть установлена!\n'
                     'Введи дату в формате ДД-ММ-ГГГГ, например 31-12-2021',
            )
            return 'GET_REGISTRATION_PERIOD'


        context.user_data['registration_period'] = registration_period_tz
        context.bot.send_message(
            chat_id=chat_id,
            text='Дата отправки подарка?\n'
                 'Введи дату в формате ДД-ММ-ГГГГ, например 01-01-2022',
        )
        return 'GET_DEPARTURE_DATE'

    except ValueError:
        context.bot.send_message(
            chat_id=chat_id,
            text='Неверная дата!\n'
                 'Введи дату в формате ДД-ММ-ГГГГ, например 31-12-2021',
        )
        return 'GET_REGISTRATION_PERIOD'


def get_departure_date(update, context):
    chat_id = update.effective_message.chat_id
    user_message = update.message.text

    try:
        departure_date = datetime.strptime(user_message, '%d-%m-%Y')
        current_tz = timezone.get_current_timezone()
        departure_date_tz = current_tz.localize(departure_date)
        context.user_data['departure_date'] = departure_date_tz
        if departure_date_tz <= context.user_data['registration_period']:
            context.bot.send_message(
                chat_id=chat_id,
                text='Неверная дата!\n'
                     f'Дата должна быть быть позже окончания регистрации',
            )
            return 'GET_DEPARTURE_DATE'
        buttons = ['Получить ссылку для регистрации']
        markup = keyboard_maker(buttons, 1)
        context.bot.send_message(
            chat_id=chat_id,
            text='Отлично, Тайный Санта уже готовится к раздаче подарков!',
            reply_markup=markup
        )
        return 'CREATE_REGISTRATION_LINK'
    except ValueError:
        context.bot.send_message(
            chat_id=chat_id,
            text='Неверная дата!\n'
                 'Введи дату в формате ДД-ММ-ГГГГ, например 01-01-2022',
        )
        return 'GET_DEPARTURE_DATE'


def create_registration_link(update, context):
    chat_id = update.effective_message.chat_id
    # TODO список game_id брать из модели
    #game_id = random.randint(111111, 999999)
    if not Game_in_Santa.objects.all():
        game_id = 100000
    else:
        game_id = Game_in_Santa.objects.all().last().id_game + 1

    registration_link = f'{context.bot["link"]}?start={game_id}'

    buttons = ['Создать игру', 'Вступить в игру']
    markup = keyboard_maker(buttons, 2)
    context.bot.send_message(
        chat_id=chat_id,
        text='Вот ссылка для приглашения участников игры, по которой '
             f'они смогут зарегистрироваться: {registration_link}',
        reply_markup=markup,
    )
    context.user_data['game_id'] = game_id
    print(context.user_data)
    save_new_game(context)
    return 'SELECT_BRANCH'


def handle_user_reply(update: Update, context: CallbackContext):
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id

    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return
    if user_reply and '/start' in user_reply:
        user_state = 'START'

    else:
        user_state = states_database.get(chat_id)
    states_functions = {
        'START': start,
        'GET_CREATOR_CONTACT': get_creator_contact,
        'GET_PLAYER_CONTACT': get_player_contact,
        'GET_GAME_NAME': get_game_name,
        'GET_COST_LIMIT': get_cost_limit,
        'GET_REGISTRATION_PERIOD': get_registration_period,
        'GET_DEPARTURE_DATE': get_departure_date,
        'CREATE_REGISTRATION_LINK': create_registration_link,
        'SELECT_BRANCH': select_branch,
        'CHECK_GAME': check_game,
        'GET_PLAYER_NAME': get_player_name,
        'GET_WISH_LIST': get_wish_list,
        'GET_LETTER_FOR_SANTA': get_letter_for_santa,
        'SHOW_GAME_INFO': show_game_info,
    }

    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    states_database.update({chat_id: next_state})



def main():
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger.info(f'Start')
    
    updater = Updater(token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_user_reply))
    dispatcher.add_handler(MessageHandler(Filters.contact, handle_user_reply))
    dispatcher.add_handler(CallbackQueryHandler(handle_user_reply))
    updater.start_polling()


#if __name__ == '__main__':
#    main()

def send_santa_massage(toss_up_list):
    """lottery_list = [[1041573069, 293277450], [1041573069, 386453509], [1041573069, 386453509]]
       Список списков из chat_id
       Первый chat_id получател сообщения
       Второй chat_id кому дарить подарок
    """
    for users in toss_up_list:
        user_1, user_2 = users
        user_2 = User_telegram.objects.get(external_id=user_2)
        text = f"""
        Жеребьевка проведена! Тебе выпал {user_2.username}
        Телефон: {user_2.telephone_number}
        Вишлист: {user_2.wishlist_user}
        """
        #bot.send_message(chat_id=user_1, text=text)

def cancel(update, _):
    user = update.message.from_user
    logger.info(f'Пользователь {user.first_name} закрыл разговор.')
    update.message.reply_text(
        'Передумаешь - пиши',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def Toss_up_game(id_game):
    game = Game_in_Santa.objects.get(id_game=id_game)
    users = User_telegram.objects.filter(games__id_game=id_game)
    random.shuffle(users)
    toss_up_list = []
    toss_up = Toss_up.objects.add(
        game=game
    )
    for number_current_user in users[:-1]:
        toss_up.donators_set.add(users[number_current_user])
        toss_up.donees_set.add(users[number_current_user+1])
        toss_up_list.append([users[number_current_user].external_id, users[number_current_user+1].external_id])
    toss_up.donators_set.add(users[-1])
    toss_up.donees_set.add(users[1])
    toss_up_list.append([users[-1].external_id, users[1].external_id])
    send_santa_massage(toss_up_list)
    toss_up.save()



class Command(BaseCommand):
    """Start the bot."""
    help = "Телеграм-бот Тайный Санта"

    def handle(self, *args, **options):
        updater = Updater(token=TELEGRAM_BOT_TOKEN)
        dispatcher = updater.dispatcher
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                'GET_CREATOR_CONTACT': [MessageHandler(Filters.text, get_creator_contact)],
                'GET_PLAYER_CONTACT': [MessageHandler(Filters.text, get_player_contact)],
                'GET_GAME_NAME': [MessageHandler(Filters.text, get_game_name)],
                'GET_COST_LIMIT': [MessageHandler(Filters.text, get_cost_limit)],
                'GET_REGISTRATION_PERIOD': [MessageHandler(Filters.text, get_registration_period)],
                'GET_DEPARTURE_DATE': [MessageHandler(Filters.text, get_departure_date)],
                'CREATE_REGISTRATION_LINK': [MessageHandler(Filters.text, create_registration_link)],
                'SELECT_BRANCH': [MessageHandler(Filters.text, select_branch)],
                'CHECK_GAME': [MessageHandler(Filters.text, check_game)],
                'GET_PLAYER_NAME': [MessageHandler(Filters.text, get_player_name)],
                'GET_WISH_LIST': [MessageHandler(Filters.text, get_wish_list)],
                'GET_LETTER_FOR_SANTA': [MessageHandler(Filters.text, get_letter_for_santa)],
                'SHOW_GAME_INFO': [MessageHandler(Filters.text, show_game_info)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
        )

        dispatcher.add_handler(conv_handler)

        updater.start_polling()
        updater.idle()