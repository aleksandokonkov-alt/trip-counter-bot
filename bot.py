import telebot
from telebot import types
from datetime import datetime

# Секретный токен вашего бота
TOKEN = '9197054641:AAGbTGtH8LVhvwn4DkYTWZaHTqPslEiJ2q8'
bot = telebot.TeleBot(TOKEN)

# Стоимость одних суток в евро
RATE_PER_DAY = 100.0

# Временное хранилище для даты старта (для простоты храним прямо в памяти)
user_trips = {}

def calculate_money(start_dt):
    """Считает деньги на текущий момент времени"""
    now = datetime.now()
    
    # Если вдруг дата старта в будущем (ошибка ввода)
    if start_dt > now:
        return None, None, None
        
    # Считаем разницу во времени
    diff = now - start_dt
    
    # Общее количество секунд, прошедших со старта
    total_seconds = diff.total_seconds()
    
    # Переводим секунды в дни (в 1 сутках = 86400 секунд)
    days_passed = total_seconds / 86400.0
    
    # Считаем итоговую сумму
    total_money = days_passed * RATE_PER_DAY
    
    # Для красивого вывода считаем чистые дни, часы и минуты
    days = diff.days
    hours, remainder = divmod(diff.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    time_str = f"{days} дн. {hours} ч. {minutes} мин."
    return round(total_money, 2), time_str, now.strftime('%d.%m.%Y %H:%M')

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_command(message):
    user_trips.pop(message.chat.id, None) # сбрасываем старые данные если были
    
    msg = (
        "👋 Привет! Я калькулятор командировочных.\n"
        "Считаю деньги в реальном времени из расчета *100 евро = 1 сутки*.\n\n"
        "Пожалуйста, введите **дату и время начала командировки** в формате:\n"
        "`ДД.ММ.ГГГГ ЧЧ:ММ`\n\n"
        "Пример: `25.10.2026 08:30`"
    )
    bot.send_message(message.chat.id, msg, parse_mode='Markdown')

# Обработка ввода даты и расчет
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    text = message.text.strip()
    
    # Если пользователь нажал кнопку обновления
    if text == "💰 Обновить сумму":
        if chat_id in user_trips:
            start_dt = user_trips[chat_id]
            money, duration, current_time = calculate_money(start_dt)
            
            response = (
                f"📊 *Текущий расчет командировки:*\n\n"
                f"📅 Начало: `{start_dt.strftime('%d.%m.%Y %H:%M')}`\n"
                f"⏱ Сейчас: `{current_time}`\n"
                f"⏳ Прошло времени: *{duration}*\n\n"
                f"💵 Начислено: 👇\n"
                f"🔥 **{money} EUR** 🔥"
            )
            bot.send_message(chat_id, response, parse_mode='Markdown')
        else:
            bot.send_message(chat_id, "Данные потерялись. Нажмите /start, чтобы ввести дату заново.")
        return

    # Попытка прочитать введенную дату старта
    try:
        start_dt = datetime.strptime(text, "%d.%m.%Y %H:%M")
        
        # Проверяем, не в будущем ли дата
        if start_dt > datetime.now():
            bot.send_message(chat_id, "❌ Дата начала не может быть в будущем! Введите корректную дату.")
            return
            
        # Сохраняем дату старта
        user_trips[chat_id] = start_dt
        
        # Считаем первый раз
        money, duration, current_time = calculate_money(start_dt)
        
        # Создаем кнопку для быстрого обновления без повторного ввода
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("💰 Обновить сумму"))
        
        response = (
            f"✅ Дата принята!\n\n"
            f"📅 Начало: `{start_dt.strftime('%d.%m.%Y %H:%M')}`\n"
            f"⏳ Прошло времени: *{duration}*\n\n"
            f"💵 Сумма на этот момент:\n"
            f"👉 **{money} EUR**\n\n"
            f"Вы можете нажимать кнопку ниже в любой момент, чтобы увидеть, как капают деньги!"
        )
        bot.send_message(chat_id, response, parse_mode='Markdown', reply_markup=markup)
        
    except ValueError:
        bot.send_message(
            chat_id, 
            "❌ Неверный формат даты! Напишите точно как в примере:\n`25.10.2026 08:30` (день.месяц.год час:минуты)"
        )

if __name__ == '__main__':
    print("Бот-счетчик командировок запущен...")
    bot.infinity_polling()
