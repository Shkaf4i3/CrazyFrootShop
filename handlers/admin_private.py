from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import reply as kb
from handlers.database import get_sc, get_eg, get_list_user
from handlers.classes_functions import IsAdmin, Add_sc, Add_eg, check_balance


admin_private_router = Router()


# Полная версия админ-панели для пользователя, кто прошел проверку через IsAdmin()
@admin_private_router.message(IsAdmin(), Command('admin_panel'))
async def admin_panel(message: Message):
    await message.answer('Что интересует?', reply_markup=kb.admin_panel())


@admin_private_router.message(IsAdmin(), F.text == '📕 Добавить товар 📕')
async def add_product(message: Message):
    await message.answer('Что желаете добавить?', reply_markup=kb.add_product())


@admin_private_router.message(IsAdmin(), F.text == '👤 Список пользователей 👤')
async def list_user(message: Message):
    all_users: str = await get_list_user()
    await message.answer(f'Список пользователей:\n{all_users}')


@admin_private_router.message(IsAdmin(), F.text == 'Вернуться в админ-панель 📊')
async def exit_menu(message: Message):
    await message.answer('Вы вернулись в главное меню', reply_markup=kb.admin_panel())


@admin_private_router.message(IsAdmin(), F.text == 'Вернуться в меню 👈')
async def back_main(message: Message):
    await message.answer('Вы вернулись в главное меню', reply_markup=kb.main_kb())


@admin_private_router.message(IsAdmin(), F.text == 'Информация для главного')
async def info_main(message: Message):
    balance = await check_balance()
    await message.answer(f'{balance}')


# Используем FSMContext для добавления логина и пароля в БД
@admin_private_router.callback_query(F.data == 'add_social_club')
async def call_add_sc_login(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Add_sc.login)
    await callback.answer()
    await callback.message.answer('🔑 Введите логин товара 🔑')

@admin_private_router.message(Add_sc.login, F.text)
async def call_add_sc_password(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await state.set_state(Add_sc.password)
    await message.answer('🔒 Введите пароль товара 🔒')

@admin_private_router.message(Add_sc.password, F.text)
async def call_add_sc_owner(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data: dict = await state.get_data()
    login = data['login']
    password = data['password']

    if await get_sc(login, password):
        await message.answer(
            '🔐 Товар успешно добавлен в таблицу 🔐',
            reply_markup=kb.admin_panel())
        await state.clear()
    else:
        await message.answer(
            '❌ Такой товар уже есть в базе ❌',
            reply_markup=kb.admin_panel())
        await state.clear()


@admin_private_router.callback_query(F.data == 'add_epic_games')
async def call_add_eg_login(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Add_eg.login)
    await callback.answer()
    await callback.message.answer('🔑 Введите логин товара 🔑')

@admin_private_router.message(Add_eg.login, F.text)
async def call_add_eg_password(message: Message, state: FSMContext):
    await state.update_data(login=message.text)
    await state.set_state(Add_eg.password)
    await message.answer('🔒 Введите пароль товара 🔒')

@admin_private_router.message(Add_eg.password, F.text)
async def call_add_eg_owner(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data: dict = await state.get_data()
    login = data['login']
    password = data['password']

    if await get_eg(login, password):
        await message.answer(
            '🔐 Товар успешно добавлен в таблицу 🔐',
            reply_markup=kb.admin_panel())
        await state.clear()
    else:
        await message.answer(
            '❌ Такой товар уже есть в базе ❌',
            reply_markup=kb.admin_panel())
        await state.clear()
