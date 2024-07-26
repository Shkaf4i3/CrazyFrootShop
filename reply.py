from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup

# Замена клавиатур-переменных на билдеры (более эффективное решение)

def main_kb() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='🛒 Купить аккаунт 🛒')
    keyboard.button(text='🖥 Наличие товаров 🖥')
    keyboard.button(text='👥 Профиль 👥')
    keyboard.button(text='🌍 Пользовательское соглашение 🌍')
    return keyboard.adjust(2).as_markup(resize_keyboard=True)


def backup_main_kb() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='Вернуться в меню 👈')
    return keyboard.as_markup(resize_keyboard=True)


def admin_panel() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text='📕 Добавить товар 📕')
    keyboard.button(text='👤 Список пользователей 👤')
    keyboard.button(text='Вернуться в меню 👈')
    keyboard.button(text='Информация для главного')
    return keyboard.adjust(2).as_markup(resize_keyboard=True)


def check_order() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='💵 Проверить платеж 💵', callback_data='check_invoice')
    return keyboard.as_markup()


def add_product() -> InlineKeyboardMarkup:
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(text='Social Club 🎉', callback_data='add_social_club')
    inline_keyboard.button(text='Epic Games 🥂', callback_data='add_epic_games')
    return inline_keyboard.adjust(1).as_markup()


def items_kb() -> InlineKeyboardMarkup:
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(text='Social club | GTA 5 | 300 RUB 💵', callback_data='social_club')
    inline_keyboard.button(text='Epic Games | GTA 5 | 300 RUB 💵', callback_data='epic_games')
    return inline_keyboard.adjust(1).as_markup()


def profile_kb() -> InlineKeyboardMarkup:
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(text='Пополнить баланс 💸', callback_data='balance')
    return inline_keyboard.as_markup()


def buy_sc_kb() -> InlineKeyboardMarkup:
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(text='Купить товар 💳', callback_data='buy_sc')
    inline_keyboard.button(text='Вернуться назад 👈', callback_data='back_inline_sc')
    return inline_keyboard.as_markup()


def buy_eg_kb() -> InlineKeyboardMarkup:
    inline_keyboard = InlineKeyboardBuilder()
    inline_keyboard.button(text='Купить товар 💳', callback_data='buy_eg')
    inline_keyboard.button(text='Вернуться назад 👈', callback_data='back_inline_eg')
    return inline_keyboard.as_markup()


def url_channel() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Подписаться на канал 🧩', url='https://t.me/check_channel_subs')
    return keyboard.as_markup()
