import telebot
import requests
import json
from telebot import types
from datetime import datetime, timedelta

API_TOKEN = ''
CHANNEL_ID = 
WEATHER_API = ''

bot = telebot.TeleBot(API_TOKEN)

try:
    bot_info = bot.get_me()
    print(f'Бот успешно запущен: @{bot_info.username}')
except telebot.apihelper.ApiTelegramException as e:
    print(f'Ошибка при запуске бота: {e}')
    exit()

user_languages = {}

translations = {
    'en': {
        'welcome': '🇷🇺Добро пожаловать! Пожалуйста, выберите язык: \n🇬🇧Welcome! Please choose a language: ',
        'choose_language': 'Please choose a language:',
        'subscribe_message': 'To use the bot, please subscribe to the developer\'s channel 🥺',
        'check_subscription': 'Check subscription ✅',
        'subscribe': 'Subscribe ➕',
        'subscription_verified': 'Subscription verified, you can use the bot ✔️',
        'not_subscribed': 'You have not subscribed to the channel, or an error occurred ❌',
        'choose_action': 'Choose an action:',
        'weather': 'Check weather ☂️',
        'developer_info': 'Developer info 👀',
        'forecast_5days': 'Check 5-day forecast ⛅️',
        'enter_city_weather': 'Enter your city to get the weather.',
        'enter_city_forecast': 'Enter your city to get the 5-day forecast.',
        'weather_info': (
            "☀️ Current temperature: {temp}°C\n"
            "🌡 Feels like: {feels_like}°C\n"
            "🔽 Minimum temperature: {temp_min}°C\n"
            "🔼 Maximum temperature: {temp_max}°C\n"
            "🌬 Wind speed: {wind_speed} m/s\n"
            "💧 Humidity: {humidity}%\n"
            "🌫 Pressure: {pressure} hPa"
        ),
        'city_invalid': 'Invalid city ❌',
        'developer_projects': 'All my projects/social networks:',
        'telegram_channel': 'Telegram channel ✉️',
        'youtube_channel': 'YouTube channel 📹',
        'instagram': 'Instagram 📷',
        'telegram_account': 'Telegram account (for questions) 🎮',
        'forecast_message': '5-day weather forecast:\n',
        'days': {
            'Monday': 'Monday',
            'Tuesday': 'Tuesday',
            'Wednesday': 'Wednesday',
            'Thursday': 'Thursday',
            'Friday': 'Friday',
            'Saturday': 'Saturday',
            'Sunday': 'Sunday'
        }
    },
    'ru': {
        'welcome': '🇷🇺Добро пожаловать! Пожалуйста, выберите язык: \n🇬🇧Welcome! Please choose a language: ',
        'choose_language': 'Пожалуйста, выберите язык:',
        'subscribe_message': 'Чтобы пользоваться ботом, пожалуйста, подпишитесь на канал разработчика 🥺',
        'check_subscription': 'Проверить подписку ✅',
        'subscribe': 'Подписаться ➕',
        'subscription_verified': 'Подписка проверена, вы можете пользоваться ботом ✔️',
        'not_subscribed': 'Вы видимо не подписались на канал, или же произошла ошибка ❌',
        'choose_action': 'Выберите действие:',
        'weather': 'Посмотреть погоду ☂️',
        'developer_info': 'Информация об разработчике 👀',
        'forecast_5days': 'Посмотреть погоду на 5 дней ⛅️',
        'enter_city_weather': 'Напиши название своего города чтобы узнать погоду.',
        'enter_city_forecast': 'Напиши название своего города чтобы узнать прогноз погоды на 5 дней.',
        'weather_info': (
            "☀️ Сейчас погода: {temp}°C\n"
            "🌡 Ощущается как: {feels_like}°C\n"
            "🔽 Минимальная температура: {temp_min}°C\n"
            "🔼 Максимальная температура: {temp_max}°C\n"
            "🌬 Скорость ветра: {wind_speed} м/с\n"
            "💧 Влажность: {humidity}%\n"
            "🌫 Давление: {pressure} гПа"
        ),
        'city_invalid': 'Город указан неверно ❌',
        'developer_projects': 'Все мои проекты/соц сети:',
        'telegram_channel': 'Телеграмм канал ✉️',
        'youtube_channel': 'Ютуб канал 📹',
        'instagram': 'Инстаграмм 📷',
        'telegram_account': 'Телеграмм аккаунт (Если есть вопросы) 🎮',
        'forecast_message': 'Прогноз погоды на 5 дней:\n',
        'days': {
            'Monday': 'Понедельник',
            'Tuesday': 'Вторник',
            'Wednesday': 'Среда',
            'Thursday': 'Четверг',
            'Friday': 'Пятница',
            'Saturday': 'Суббота',
            'Sunday': 'Воскресенье'
        }
    }
}

def get_translation(user_id, text_key):
    language = user_languages.get(user_id, 'en')
    return translations[language][text_key]

def is_user_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        print(f'User {user_id} status: {member.status}')
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f'Error checking subscription for user {user_id}: {e}')
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button_en = types.KeyboardButton('🇬🇧English')
    button_ru = types.KeyboardButton('🇷🇺Русский')
    markup.add(button_en, button_ru, )
    bot.send_message(message.chat.id, get_translation(message.from_user.id, 'welcome'), reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['🇬🇧English', '🇷🇺Русский'])
def set_language(message):
    user_languages[message.from_user.id] = 'en' if message.text == '🇬🇧English' else 'ru'
    send_subscription_prompt(message)

def send_subscription_prompt(message):
    user_id = message.from_user.id
    markup = types.InlineKeyboardMarkup()
    subscribe_button = types.InlineKeyboardButton(text=get_translation(user_id, 'subscribe'), url=f'')
    check_button = types.InlineKeyboardButton(text=get_translation(user_id, 'check_subscription'), callback_data='check_subscription')
    markup.add(subscribe_button)
    markup.add(check_button)
    bot.send_message(message.chat.id, get_translation(user_id, 'subscribe_message'), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'check_subscription')
def handle_check_subscription(call):
    user_id = call.from_user.id
    if is_user_subscribed(user_id):
        bot.send_message(call.message.chat.id, get_translation(user_id, 'subscription_verified'))
        keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        button1 = types.KeyboardButton(get_translation(user_id, 'weather'))
        button2 = types.KeyboardButton(get_translation(user_id, 'developer_info'))
        button3 = types.KeyboardButton(get_translation(user_id, 'forecast_5days'))
        button4 = types.KeyboardButton('🌏Change language \nСменить язык🌏')
        keyboard.add(button1, button2)
        keyboard.add(button3, button4)
        bot.send_message(call.message.chat.id, get_translation(user_id, 'choose_action'), reply_markup=keyboard)
    else:
        bot.send_message(call.message.chat.id, get_translation(user_id, 'not_subscribed'))

@bot.message_handler(func=lambda message: message.text in [translations['en']['weather'], translations['ru']['weather'],
                                                           translations['en']['developer_info'], translations['ru']['developer_info'],
                                                           translations['en']['forecast_5days'], translations['ru']['forecast_5days'],])
def handle_buttons(message):
    user_id = message.from_user.id
    if message.text in [translations['en']['weather'], translations['ru']['weather']]:
        bot.send_message(message.chat.id, get_translation(user_id, 'enter_city_weather'))
        bot.register_next_step_handler(message, get_weather)
    elif message.text in [translations['en']['developer_info'], translations['ru']['developer_info']]:
        send_developer_info(message)
    elif message.text in [translations['en']['forecast_5days'], translations['ru']['forecast_5days']]:
        bot.send_message(message.chat.id, get_translation(user_id, 'enter_city_forecast'))
        bot.register_next_step_handler(message, get_5day_forecast)
      
def get_weather(message):
    user_id = message.from_user.id
    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        weather_info = get_translation(user_id, 'weather_info').format(
            temp=data['main']['temp'],
            feels_like=data['main']['feels_like'],
            temp_min=data['main']['temp_min'],
            temp_max=data['main']['temp_max'],
            wind_speed=data['wind']['speed'],
            humidity=data['main']['humidity'],
            pressure=data['main']['pressure']
        )
        bot.reply_to(message, weather_info)
    else:
        bot.reply_to(message, get_translation(user_id, 'city_invalid'))

def get_5day_forecast(message):
    user_id = message.from_user.id
    city = message.text.strip().lower()
    forecast_res = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API}&units=metric')
    if forecast_res.status_code == 200:
        forecast_data = forecast_res.json()
        daily_forecast = {}
        for forecast in forecast_data['list']:
            date_txt = forecast['dt_txt']
            date = datetime.strptime(date_txt, '%Y-%m-%d %H:%M:%S').date()
            temp = forecast['main']['temp']
            if date not in daily_forecast:
                daily_forecast[date] = []
            daily_forecast[date].append(temp)

        forecast_message = get_translation(user_id, 'forecast_message')
        for date, temps in daily_forecast.items():
            day_name = date.strftime('%A')
            day_name_translated = translations[user_languages[user_id]]['days'].get(day_name, day_name)
            avg_temp = sum(temps) / len(temps)
            forecast_message += f'{day_name_translated} ({date.strftime("%d-%m-%Y")}): {avg_temp:.2f}°C\n'

        bot.reply_to(message, forecast_message)
    else:
        error_message = forecast_res.text
        bot.reply_to(message, f'{get_translation(user_id, "city_invalid")}: {error_message}')

def send_developer_info(message):
    user_id = message.from_user.id
    project = types.InlineKeyboardMarkup()
    telegram_channel = types.InlineKeyboardButton(text=get_translation(user_id, 'telegram_channel'), url='https://t.me/')
    youtube_channel = types.InlineKeyboardButton(text=get_translation(user_id, 'youtube_channel'), url='https://youtube.com/@?si=zbsaG2sop91dvVbi')
    instagram = types.InlineKeyboardButton(text=get_translation(user_id, 'instagram'), url='https://www.instagram.com//?hl=ru')
    personal = types.InlineKeyboardButton(text=get_translation(user_id, 'telegram_account'), url='https://t.me/')
    project.add(telegram_channel)
    project.add(youtube_channel)
    project.add(instagram)
    project.add(personal)
    bot.send_message(message.chat.id, get_translation(user_id, 'developer_projects'), reply_markup=project)

@bot.message_handler(func=lambda message: message.text in '🌏Change language \nСменить язык🌏')
def change_language(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button_en = types.KeyboardButton('🇬🇧English🇬🇧')
    button_ru = types.KeyboardButton('🇷🇺Русский🇷🇺')
    markup.add(button_en, button_ru)
    bot.send_message(message.chat.id, '🌐Выберете желаемый язык \nChoose the desired language🌐', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ['🇬🇧English🇬🇧', '🇷🇺Русский🇷🇺'])
def changed_language(message):
    user_languages[message.from_user.id] = 'en' if message.text == '🇬🇧English🇬🇧' else 'ru'
    send_language_prompt(message)

def send_language_prompt(message):
    user_id = message.from_user.id
    markup = types.InlineKeyboardMarkup()
    check_button_en = types.InlineKeyboardButton('Change the language✅', callback_data='change_language')
    check_button_ru = types.InlineKeyboardButton('Сменить язык✅', callback_data='change_language')
    markup.add(check_button_en)
    markup.add(check_button_ru)
    bot.send_message(message.chat.id, 'Click the button below\nНажмите кнопку ниже', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'change_language')
def handle_check_subscription(call):
    user_id = call.from_user.id
    if is_user_subscribed(user_id):
        keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
        button1 = types.KeyboardButton(get_translation(user_id, 'weather'))
        button2 = types.KeyboardButton(get_translation(user_id, 'developer_info'))
        button3 = types.KeyboardButton(get_translation(user_id, 'forecast_5days'))
        button4 = types.KeyboardButton('🌏Change language \nСменить язык🌏')
        keyboard.add(button1, button2)
        keyboard.add(button3, button4)
        bot.send_message(call.message.chat.id, get_translation(user_id, 'choose_action'), reply_markup=keyboard)
    else:
        markup = types.InlineKeyboardMarkup()
        subscribe_button_en = types.InlineKeyboardButton('Subscribe➕', url=f'https://t.me/')
        subscribe_button_ru = types.InlineKeyboardButton('Подписаться➕', url=f'https://t.me/')
        markup.add(subscribe_button_en)
        markup.add(subscribe_button_ru)
        bot.send_message(call.message.chat.id, '😢Вы не подписаны, пожалуйста подпишитесь и повторите попытку\nYou are not subscribed, please subscribe and try again😢', reply_markup=markup)

bot.polling(non_stop=True)
