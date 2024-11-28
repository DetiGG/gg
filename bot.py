import logging
import asyncio
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from database import init_db,  add_user, get_all_users # Импортируем функции для работы с БД
logging.basicConfig(level=logging.INFO)
active = True
storage = MemoryStorage()
API_TOKEN = '7253122649:AAF8HtdtVR9YBgG5ZmFGlN--9irY6uhmTNI'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()
DEVELOPER_CHAT_ID = 5497020266

# Список для хранения идентификаторов пользователей
user_ids = set()
class Feedback(StatesGroup):
    waiting_for_feedback = State()

@dp.message(Command("feedback"))
async def feedback_command(message: types.Message, state: FSMContext):
    global active
    if not active:
        # Игнорируем сообщения, если бот не активен
        return
    await message.answer("Пожалуйста, напишите ваш отзыв.")
    await state.set_state(Feedback.waiting_for_feedback)

@dp.message(Command("chat_info"))
async def chat_info(message: types.Message):
    global active
    if not active:
        # Игнорируем сообщения, если бот не активен
        return
    chat = message.chat
    await message.answer(f"Название чата: {chat.title} \nТип чата: {chat.type}\nВаш айди: {message.from_user.id}")
users_id = []

async def load_users():
    global users_id
    users_id = await get_all_users()  # Загружаем всех пользователей из базы данных

@dp.message(Command("adminf_start"))
async def admin_stop_command(message: types.Message):
    if message.from_user.id == DEVELOPER_CHAT_ID:
        global active
        active = True
        for user_id in users_id:
            try:
                await bot.send_message(user_id, "Бот запущен и готов к работе!")
            except Exception as e:
                logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
        logging.info("БОТ ЗАПУЩЕН")
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")
        await message.answer("Напишите в поддержку о выдаче доступа к фунциям админа!")

@dp.message(Command("adminf_stop"))
async def admin_stop_command(message: types.Message):
    global active
    if not active:
        # Игнорируем сообщения, если бот не активен
        return
    if message.from_user.id == DEVELOPER_CHAT_ID:  # Проверка на администратора
        for user_id in users_id:
            try:
                await bot.send_message(user_id, "Ушёл на технический перерыв. Спасибо, что вы с нами!")
            except Exception as e:
                logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

        active = False
        while not active:
            logging.info("БОТ ГОТОВ К ТЕХОБСЛУЖИВАНИЮ. ЗАВЕРШИТЕ РАБОТУ.")
            await asyncio.sleep(8)
    else:
        await message.answer("У вас нет прав для выполнения этой команды.")
        await message.answer("Напишите в поддержку (о проекте) о выдаче доступа к фунциям админа!")

@dp.message(F.text, Feedback.waiting_for_feedback)
async def feedback_response(message: types.Message, state: FSMContext):
    feedback_text = message.text.strip()

    if not feedback_text:
        await message.answer("Ваш отзыв не может быть пустым. Пожалуйста, напишите что-то.")
        return

    await bot.send_message(DEVELOPER_CHAT_ID, f"Новый отзыв от {message.from_user.username}:\n{feedback_text}")
    await message.answer("Спасибо за ваш отзыв!")
    await state.clear()  # Завершение состояния

WELCOME_TEXT = (
    "Привет! Я чат-бот, твой школьный помощник. Вот, что я могу:\n"
    "1. Начать - запустить взаимодействие с ботом.\n"
    "2. Помощь - получить информацию о командах и функциях.\n"
    "3. О проекте - узнать больше о проекте (разработчик, поддержка, текущая версия)"
)

def create_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Начать"), KeyboardButton(text="Помощь"), KeyboardButton(text="О проекте")]
        ],
        resize_keyboard=True
    )

def create_action_keyboard():
    # Создаем клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Расписание📌", callback_data="action1"),
            InlineKeyboardButton(text="Помощь с дз💬", callback_data="action2")
        ],
        [
            InlineKeyboardButton(text="Клубы, секции, кружки😎", callback_data="action3")
        ],
        [
            InlineKeyboardButton(text="Как провести день⏰?", callback_data="action4")
        ],
        [
            InlineKeyboardButton(text="Информация о школе🏫", callback_data="action5")
        ],
        [
            InlineKeyboardButton(text="Напоминание✅", callback_data="action6"),
            InlineKeyboardButton(text="Объявление📢", callback_data="action7")
        ]
    ])
    return keyboard

main_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Назад", callback_data="main_menu")
    ]
])

@dp.callback_query()
async def handle_callback(callback_query: types.CallbackQuery):
    global active
    if not active:
        return
    if callback_query.data == "action1":
        await callback_query.answer("Ищем ваше расписание...", show_alert=True)
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await asyncio.sleep(2.6)
        await callback_query.message.answer(text="ТЕСТ", reply_markup=main_keyboard)
    elif callback_query.data == "action2":
        await callback_query.answer("Сейчас решим проблему)", show_alert=True)
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await asyncio.sleep(2.6)
        await callback_query.message.answer(text="ТЕСТ", reply_markup=main_keyboard)
    elif callback_query.data == "action3":
        await callback_query.answer("Круто! Уже готовлю ответ)", show_alert=True)
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await asyncio.sleep(2.6)
        await callback_query.message.answer(text="ТЕСТ", reply_markup=main_keyboard)
    elif callback_query.data == "action4":
        await callback_query.answer("Сейчас расскажу!", show_alert=True)
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await asyncio.sleep(2.6)
        await callback_query.message.answer(text="ТЕСТ", reply_markup=main_keyboard)
    elif callback_query.data == "action5":
        await callback_query.answer("Какая классная школа!", show_alert=True)
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await asyncio.sleep(2.6)
        await callback_query.message.answer(text="ТЕСТ", reply_markup=main_keyboard)
    elif callback_query.data == "main_menu":
        # Возвращаем пользователя к основной инлайн клавиатуре
        KEYBOARD1 = create_action_keyboard()
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text="Пожалуйста, выберите действие:",
            reply_markup=KEYBOARD1
        )

@dp.message(Command("joke"))
async def joke_command(message: types.Message):
    global active
    if not active:
        # Игнорируем сообщения, если бот не активен
        return
    jokes = [
        "Почему программисты не любят природу? Потому что в ней слишком много багов.",
        "Какой язык программирования самый оптимистичный? Python, потому что он всегда делает то, что ты ему говоришь.",
        "Познакомил родителей со своей девушкой. Она им сразу понравилась, теперь относятся к ней, как к родной дочке — ищут ей нормального парня.",
        "Сижу на двух диетах.. Одной не наедаюсь!",
        "Учёные нашли черепаху, которая прожила 300 лет. Интересно, сколько бы ещё она прожила, если бы её не нашли учёные...",
        "У чиновника из Томской области нашли подвал, полный денег. Он хотел раздать их сиротам, но не успел до прихода полиции.",
        "Мне батя сказал если я еще буду долго сидеть у компа и в тг, не сделав уроки, то он меня мордой по клавиатуре возить будет, но я не лыком шитпрауекрогр8гоп66гшамджзщ8п679шгппппвукнпеирщз..",
        "Почему Java-программисты не могут найти себе пары? Потому что они всегда работают с классами.",
        "Только русский человек найдя одну бутылку водки купит еще… две, чтобы отпраздновать находку!"
    ]
    joke = random.choice(jokes)
    await message.answer(joke)

async def anim(message: types.Message, word: str):
    msg = await message.answer("В")
    text = "В"
    cp = 0
    for char in range(len(word)):
        await asyncio.sleep(0.08)

        if cp == 1:
            char += 1

        if cp == 2:
            char += 2
        if char == len(word):
            break
        if word[char] == " ":
            text += str(word[char]) + str(word[char + 1])
            cp += 1
        else:
            text += word[char]
        await msg.edit_text(text)
    await asyncio.sleep(0.6)

async def anim2(message: types.Message, word: str):
    msg = await message.answer("Р")
    text = "Р"
    cp = 0
    for char in range(len(word)):
        await asyncio.sleep(0.08)

        if cp == 1:
            char += 1

        if cp == 2:
            char += 2
        if char == len(word):
            break
        if word[char] == " ":
            text += str(word[char]) + str(word[char + 1])
            cp += 1
        else:
            text += word[char]
        await msg.edit_text(text)
    await asyncio.sleep(0.6)

async def anim3(message: types.Message, i: str):
    msg = await message.answer("П")
    text = "П"
    cp = 0
    for char in range(len(i)):
        await asyncio.sleep(0.08)
        if cp == 1:
            char += 1
        if cp == 2:
            char += 2
        if char == len(i):
            break
        if i[char] == " ":
            text += str(i[char]) + str(i[char + 1])
            cp += 1
        else:
            text += i[char]
        await msg.edit_text(text)
    await asyncio.sleep(0.6)
async def anim4(message: types.Message, i: str):
    msg = await message.answer("Т")
    text = "Т"
    cp = 0
    for char in range(len(i)):
        await asyncio.sleep(0.1)
        if cp == 1:
            char += 1
        if cp == 2:
            char += 2
        if char == len(i):
            break
        if i[char] == " ":
            text += str(i[char]) + str(i[char + 1])
            cp += 1
        else:
            text += i[char]
        await msg.edit_text(text)
    await asyncio.sleep(0.6)
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    global active
    if not active:
        # Игнорируем сообщения, если бот не активен
        return
    await add_user(message.from_user.id)  # Добавляем пользователя в список
    await load_users()
    await state.clear()
    keyboard = create_main_keyboard()
    await message.answer(WELCOME_TEXT, reply_markup=keyboard)

@dp.message(F.text)
async def echo(message: types.Message):
    global active
    if not active:
        # Игнорируем сообщения, если бот не активен
        return
    if message.text == "Начать":
        KEYBOARD = create_action_keyboard()
        await message.answer("Пожалуйста, выберите действие:", reply_markup=KEYBOARD)
    elif message.text == "Помощь":
        await message.answer(
            "Вот список доступных команд:\n"
            "/start - Запустить бота\n"
            "/feedback - Оставить отзыв\n"
            "/chat_info - Получить информацию о чате\n"
            "/joke - Рассказать анекдот \n"
            "/adminf_stop - АДМИНТЕХПЕРЕРЫВ \n"
            "/adminf_start - АДМИНСТАРТ"
        )
    elif message.text == "О проекте":
        await anim2(message, "азработчик: ZK-7 game")
        await anim3(message, "оддержка бота: @DeTiggg")
        await anim(message, "ерсия: 1.5")
    elif message.text == "Назад":
        KEYBOARD = create_main_keyboard()
        await message.answer("Вы вернулись в главное меню.", reply_markup=KEYBOARD)
    else:
        await message.answer("Я не понимаю это сообщение. Пожалуйста, выберите одно из действий.")
async def on_startup():
    global active
    active = True
    await init_db()
    await load_users()  # Загружаем всех пользователей при старте
    global km
    km = True
    if km:
        await gold_func()
    logging.info("Бот запущен")
km = None
async def gold_func():
    for user_id in users_id:
        try:
            await bot.send_message(user_id, "Бот снова работает!")
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
ck = None
async def gold_func2():
    for user_id in users_id:
        try:
            await bot.send_message(user_id, "Бот отключён")
        except Exception as e:
            logging.error(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
async def on_shutdown():
    ck = True
    if ck:
        await gold_func2()
    logging.info("Бот отключен")  # Логируем отключение бота
is_bot_active = False
if __name__ == '__main__':
    async def main():
        await on_startup(skip_updates=True)
        try:
            await dp.start_polling(bot,skip_updates=True)
        finally:
            await on_shutdown()
    asyncio.run(main())
