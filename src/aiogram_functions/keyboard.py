from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup


def main_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="🛒 Купить аккаунт 🛒")
    builder.button(text="🖥 Наличие товаров 🖥")
    builder.button(text="👥 Профиль 👥")
    builder.button(text="🌍 Пользовательское соглашение 🌍")

    return builder.adjust(2).as_markup(resize_keyboard=True)


def admin_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="📕 Добавить товары 📕")
    builder.button(text="👤 Список пользователей 👤")
    builder.button(text="✅ Рассылка всем пользователям бота ✅")
    builder.button(text="Вернуться в меню пользователя 👈")

    return builder.adjust(2).as_markup(resize_keyboard=True)


def cancel_mailing() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отменить рассылку ❌")

    return builder.as_markup(resize_keyboard=True)


def cancel_saving() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отменить сохранение аккаунта ❌")

    return builder.as_markup(resize_keyboard=True)


def cancel_top_up() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Отменить пополнение ❌")

    return builder.as_markup(resize_keyboard=True)


def available_platforms() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Social club | GTA 5 | 600 RUB 💵", callback_data="social_club")
    builder.button(text="Epic Games | GTA 5 | 600 RUB 💵", callback_data="epic_games")
    builder.button(text="❌ Закрыть окно ❌", callback_data="close_window")

    return builder.adjust(1).as_markup()


def top_up_balance() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💵 Пополнить баланс 💵", callback_data="top_up_balance")

    return builder.as_markup()


def buy_account(type_platform: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Купить аккаунт 💳", callback_data=f"buy_account_{type_platform}")
    builder.button(text="Вернуться назад 👈", callback_data="go_back")

    return builder.as_markup()


def check_invoice() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Проверить платеж", callback_data="check_invoice")
    builder.button(text="Отменить платеж", callback_data="cancel_top_up")
    return builder.as_markup()
