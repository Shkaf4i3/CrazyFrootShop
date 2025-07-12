from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import reply as kb
from other_func.database import get_sc, get_eg, get_list_user
from other_func.classes_functions import IsAdmin, Add_sc, Add_eg, check_balance
from other_func.encrypt_db import generate_crypto_key


admin_private_router = Router()


# Полная версия админ-панели для пользователя, кто прошел проверку через IsAdmin()
@admin_private_router.message(IsAdmin(), Command("admin_panel"))
async def admin_panel(message: Message):
    await message.answer(f"Приветствую, {message.from_user.first_name}\n"
                         "Что интересует?",
                         reply_markup=kb.admin_panel(),
                         )


@admin_private_router.message(IsAdmin(), Command("get_crypto_key"))
async def get_crypto_key(message: Message):
    encrypt_key = await generate_crypto_key()

    await message.answer(
        f"Ваш ключ шифрования - {encrypt_key}",
    )


@admin_private_router.message(IsAdmin(), F.text == "📕 Добавить товар 📕")
async def add_product(message: Message):
    await message.answer("Что желаете добавить?", reply_markup=kb.add_product())


@admin_private_router.message(IsAdmin(), F.text == "👤 Список пользователей 👤")
async def list_user(message: Message):
    all_users: str = await get_list_user()
    await message.answer(f"Список пользователей:\n{all_users}")


@admin_private_router.message(IsAdmin(), F.text == "Вернуться в админ-панель 📊")
async def exit_menu(message: Message):
    await message.answer("Вы вернулись в главное меню", reply_markup=kb.admin_panel())


@admin_private_router.message(IsAdmin(), F.text == "Вернуться в меню 👈")
async def back_main(message: Message):
    await message.answer("Вы вернулись в главное меню", reply_markup=kb.main_kb())


@admin_private_router.message(IsAdmin(), F.text == "Информация для главного")
async def info_main(message: Message):
    balance = await check_balance()
    await message.answer(f"{balance}")


# Используем FSMContext для добавления логина и пароля в БД
@admin_private_router.callback_query(F.data == "add_social_club")
async def get_sc_info(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Add_sc.info)
    await callback.answer()
    await callback.message.answer(
        "🔑 Введите информацию о товаре в формате 'login:password:key' 🔑"
        )


@admin_private_router.message(Add_sc.info, F.text)
async def add_sc_info(message: Message, state: FSMContext):
    await state.update_data(info=message.text.split(":"))
    data: dict = await state.get_data()
    info = data["info"]

    if len(info) == 3:
        login = info[0]
        password = info[1]
        key: str = info[2]

        if await get_sc(login, password, key=key.replace("b'", "").replace("'", "")):
            await message.answer(
                "🔐 Товар успешно добавлен в таблицу 🔐",
                reply_markup=kb.admin_panel())
        else:
            await message.answer(
                "❌ Такой товар уже есть в базе ❌",
                reply_markup=kb.admin_panel())
    else:
        await message.answer(
            "Вы отправили данные в неправильном формате",
        )
    await state.clear()


@admin_private_router.callback_query(F.data == "add_epic_games")
async def get_eg_info(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Add_eg.info)
    await callback.answer()
    await callback.message.answer(
        "🔑 Введите информацию о товаре в формате 'login:password:key 🔑"
        )

@admin_private_router.message(Add_eg.info, F.text)
async def add_eg_info(message: Message, state: FSMContext):
    await state.update_data(info=message.text.split(":"))
    data: dict = await state.get_data()
    info = data["info"]

    if len(info) == 3:
        login = info[0]
        password = info[1]
        key: str = info[2]

        if await get_eg(login, password, key=key.replace("b'", "").replace("'", "")):
            await message.answer(
                "🔐 Товар успешно добавлен в таблицу 🔐",
                reply_markup=kb.admin_panel())
        else:
            await message.answer(
                "❌ Такой товар уже есть в базе ❌",
                reply_markup=kb.admin_panel())
    else:
        await message.answer(
            "Вы отправили данные в неправильном формате",
        )
    await state.clear()
