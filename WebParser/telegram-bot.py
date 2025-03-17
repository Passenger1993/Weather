import telebot
from telebot import types
from main import *

# Создаем экземпляр бота
bot = telebot.TeleBot('6890173067:AAG5NxPyBPdwnP_X_6AsaHi8VUedOSScGF4')

waiting_for_region = False
waiting_for_period = False
last_callback_data = None
chat_id = None
data_mode = None
region = None
period = None


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    global chat_id
    chat_id = message.chat.id
    # Создаем клавиатуру с кнопками
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton('Сведения о вспышках в регионе',callback_data='button1')
    button2 = types.InlineKeyboardButton('Диаграмма вспышек в регионе',callback_data='button2')
    button3 = types.InlineKeyboardButton('Данные обо всех событиях за 7/14/30 дней',callback_data='button3')
    button4 = types.InlineKeyboardButton('График всех событий за 7/14/30 дней',callback_data='button4')
    button5 = types.InlineKeyboardButton('Все события за период N',callback_data='button5')
    button6 = types.InlineKeyboardButton('График событий за период N',callback_data='button6')
    button7 = types.InlineKeyboardButton('Обновление базы данных',callback_data='button7')
    keyboard.add(button1, button2, button3, button4, button5, button6, button7)
    bot.send_message(message.chat.id, "Выберите режим:",reply_markup=keyboard)

#button1_1 - числа обозначают иерархию - после нажатия 1-ой кнопки выполняется 1-е действие
@bot.callback_query_handler(func=lambda call: call.data == 'button1')
def button_1_data(call):
    global last_callback_data
    global chat_id
    last_callback_data = "button1_1"
    bot.send_message(chat_id, "Введите регион:")

@bot.callback_query_handler(func=lambda call: call.data == 'button1_1')
def button_1_data():
    global chat_id
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton('Solarsoft',callback_data='button1_1_1')
    button2 = types.InlineKeyboardButton('Solardemon',callback_data='button1_1_2')
    keyboard.add(button1, button2)
    bot.send_message(chat_id, "Какую базу данных вы хотите использовать?", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'button1_1_1')
def button_1_solarsoft(call):
    global region
    global chat_id
    resp = data_request(False,True,region=region)
    resp = '\n'.join(['\t'.join(sublist) + '\n------------------------------' for sublist in resp[0]])
    bot.send_message(chat_id, f"Данные из solarsoft по региону {region}:\n{resp},")

@bot.callback_query_handler(func=lambda call: call.data == 'button1_1_2')
def button_1_solardemon(call):
    global region
    global chat_id
    resp = data_request(True,region=region)
    resp = '\n'.join(['\t'.join(sublist) + '\n------------------------------' for sublist in resp[0]])
    bot.send_message(chat_id, f"Данные из solardemon по региону {region}:\n{resp}")

@bot.callback_query_handler(func=lambda call: call.data == 'button2')
def button_2_region(call):
    global last_callback_data
    last_callback_data = "button2_1"
    bot.send_message(chat_id, "Введите следующие данные:\nРегион\nРазрешение по x\nРазрешение по events\nРазрешение по flux")

@bot.callback_query_handler(func=lambda call: call.data == 'button2_1')
def button_2_graphs(x,events,flux):
    global region
    global chat_id
    show_mode("2",region=region,console=False, x=int(x),events=int(events),flux=None)
    with open('plot.png', 'rb') as f:
        bot.send_photo(chat_id=chat_id, photo=f)

@bot.callback_query_handler(func=lambda call: call.data == 'button3')
def button_3_region(call):
    global last_callback_data
    last_callback_data = "button3_1"
    bot.send_message(call.message.chat.id, "Введите регион")

@bot.callback_query_handler(func=lambda call: call.data == 'button3_1')
def button_3_period(chat_id):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton('7 дней',callback_data='button3_1_1')
    button2 = types.InlineKeyboardButton('14 дней',callback_data='button3_1_2')
    button3 = types.InlineKeyboardButton('30 дней',callback_data='button3_1_3')
    keyboard.add(button1, button2, button3)
    bot.send_message(chat_id, "Выберите период:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'button3_1_1')
def button_3_7(call):
    global region
    resp = data_request(True,True,True,region,(current_datetime- timedelta(days=7),current_datetime))
    bot.send_message(call.message.chat.id, f"Получены данные:\n{resp}")

@bot.callback_query_handler(func=lambda call: call.data == 'button3_1_2')
def button_3_14(call):
    global region
    resp = data_request(True,True,True,region,(current_datetime- timedelta(days=14),current_datetime))
    bot.send_message(call.message.chat.id, f"Получены данные:\n{resp}")

@bot.callback_query_handler(func=lambda call: call.data == 'button3_1_3')
def button_3_30(call):
    global region
    resp = data_request(True,True,True,region,(current_datetime- timedelta(days=30),current_datetime))
    bot.send_message(call.message.chat.id, f"Получены данные:\n{resp}")

@bot.callback_query_handler(func=lambda call: call.data == 'button4')
def button_4_region(chat_id):
    global last_callback_data
    last_callback_data = "button4_1"
    bot.send_message(chat_id, "Введите регион:")

@bot.callback_query_handler(func=lambda call: call.data == 'button4_1')
def button_4_period(call):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    button1 = types.InlineKeyboardButton('7 дней',callback_data='button4_1_1')
    button2 = types.InlineKeyboardButton('14 дней',callback_data='button4_1_2')
    button3 = types.InlineKeyboardButton('30 дней',callback_data='button4_1_3')
    keyboard.add(button1, button2, button3)
    bot.send_message(call.message.chat.id, "Выберите период:", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'button4_1_1')
def button_4_7(call):
    global region
    show_mode("4",current_datetime- timedelta(days=7),current_datetime,region,console=False)
    with open('plot.png', 'rb') as f:
        bot.send_photo(chat_id=call.message.chat.id, photo=f)

@bot.callback_query_handler(func=lambda call: call.data == 'button4_1_2')
def button_4_14(call):
    global region
    show_mode("4",current_datetime- timedelta(days=14),current_datetime,region,console=False)
    with open('plot.png', 'rb') as f:
        bot.send_photo(chat_id=call.message.chat.id, photo=f)

@bot.callback_query_handler(func=lambda call: call.data == 'button4_1_3')
def button_4_30(call):
    global region
    show_mode("4",current_datetime- timedelta(days=30),current_datetime,region,console=False)
    with open('plot.png', 'rb') as f:
        bot.send_photo(chat_id=call.message.chat.id, photo=f)

@bot.callback_query_handler(func=lambda call: call.data == 'button5')
def button_5_period(call):
    global last_callback_data
    last_callback_data = "button5_1"
    bot.send_message(call.message.chat.id, "Введите интервал времени в формате:\n2000-01-01 00:00:00\n2010-01-01 00:00:00")

@bot.callback_query_handler(func=lambda call: call.data == 'button5_1')
def button_5_req(chat_id):
    global last_callback_data
    global period
    resp = data_request(True,True,True,period=period, filters=True)
    bot.send_message(chat_id, f"Получены данные:{resp}")

@bot.callback_query_handler(func=lambda call: call.data == 'button6')
def button_6_period(call):
    global last_callback_data
    last_callback_data = "button6_1"
    bot.send_message(call.message.chat.id, "Введите интервал времени в формате:\n2000-01-01 00:00:00\n2010-01-01 00:00:00")

@bot.callback_query_handler(func=lambda call: call.data == 'button6_1')
def button_6_req(chat_id):
    global last_callback_data
    global period
    show_mode("6",period[0],period[1],console=False)
    bot.send_message(chat_id, f"Получены данные:{resp}")

@bot.callback_query_handler(func=lambda call: call.data == 'button7')
def button_7_update(call):
    bot.send_message(call.message.chat.id, "Обновление базы данных....")
    update_base()
    bot.send_message(call.message.chat.id, "База данных обновлена")

@bot.message_handler(content_types=['text'])
def text_handler(message):
    global last_callback_data
    global region
    global period
    global chat_id
    global last_message_id
    if last_callback_data == "button1_1":
        region = message.text
        button_1_data()
    elif last_callback_data == "button2_1":
        info = message.text.split("\n")
        region = info[0]
        button_2_graphs(info[1],info[2],info[3])
    elif last_callback_data == "button3_1":
        region = message.text
        button_3_period(chat_id)
    elif last_callback_data == "button4_1":
        region = message.text
        button_4_period(chat_id)
    elif last_callback_data == "button5_1":
        info = message.text.split("\n")
        period = (info[0],info[1])
        button_5_req(chat_id)
    elif last_callback_data == "button6_1":
        info = message.text.split("\n")
        period = (info[0],info[1])
        button_6_req(chat_id)

bot.polling()
