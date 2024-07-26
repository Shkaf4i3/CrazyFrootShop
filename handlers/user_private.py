from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import reply as kb
from handlers.database import (
    get_count_sc,
    get_count_eg,
    add_user,
    get_count_balance,
    get_item_sc,
    get_item_eg)
from handlers.classes_functions import Balance_state, check_invoice, cryptobot


user_private_router = Router()


@user_private_router.message(CommandStart())
async def start(message: Message):
    await add_user(message.from_user.id, message.from_user.first_name)

    await message.answer(f'❤️ Привет, {message.from_user.first_name} ❤️ \n'
                         '💥Добро пожаловать в самый лучший магазин с аккаунтами GTA 5 💥 \n'
                         'Для работы воспользуйся меню ниже 👇',
                         reply_markup=kb.main_kb())


@user_private_router.message(Command('help'))
async def help(message: Message):
    await message.answer('☺️ В данном боте вы сможете купить по хорошей цене качественные аккаунты GTA 5 ☺️ \n'
                         '🧩 Площадки с аккаунтами - Social Club, Epic Games 🧩 \n'
                         '\n'
                         'По всем вопросам о боте обращаться 👉 @shkaf4i3 👈',
                         reply_markup=kb.backup_main_kb())


@user_private_router.message(F.text == '🛒 Купить аккаунт 🛒')
async def buy_items(message: Message):
    await message.answer('Список товаров', reply_markup=kb.items_kb())


@user_private_router.message(F.text == 'Вернуться в меню 👈')
async def backup(message: Message):
    await message.answer('Вы вернулись в меню 👌', reply_markup=kb.main_kb())


@user_private_router.message(F.text == '👥 Профиль 👥')
async def profile(message: Message):
    check_balance: int = await get_count_balance(message.from_user.first_name)
    await message.answer(f'🍬 ID: <code> {message.from_user.id} </code> \n'
                    f'🤩 Имя: {message.from_user.first_name} \n'
                    '\n'
                    f'Баланс - {check_balance} rub \n',
                    reply_markup=kb.profile_kb())


@user_private_router.message(F.text == '🖥 Наличие товаров 🖥')
async def check_items(message: Message):
    count_sc: int = await get_count_sc()
    count_ec: int = await get_count_eg()
    await message.answer(f'💚 Social Club 💚 | 300 rub | {count_sc} шт.\n'
                         f'❤️ Epic Games ❤️ | 300 rub | {count_ec} шт.')


@user_private_router.message(F.text == '🌍 Пользовательское соглашение 🌍')
async def user_agreement(message: Message):
    await message.answer('Перед использованием бота прочтите данное соглашение \n'
                         '<a href="https://telegra.ph/Polzovatelskoe-soglashenie-05-11-16">тык</a>',
                         disable_web_page_preview=True)


# Работа с пополнением баланса через FSM
@user_private_router.callback_query(F.data == 'balance')
async def app_balance(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Balance_state.amount)
    await callback.answer()
    await callback.message.answer(
        'Введите сумму USDT, на которую желаете пополнить баланс \n'
        'Оплата производится через CryptoBot',
        reply_markup=kb.backup_main_kb()
    )


@user_private_router.message(Balance_state.amount, F.text)
async def create_order(message: Message, state: FSMContext):
    await state.update_data(amount=message.text)
    data = await state.get_data()
    amount = data['amount']
    order = await cryptobot.create_invoice(amount=amount, currency_type='crypto', asset='USDT')
    await state.update_data(check_amount=order.invoice_id)

    await message.answer('Перейдите по ссылке, чтобы произвести оплату \n'
                         f'{order.pay_url}', reply_markup=kb.check_order())


@user_private_router.callback_query(F.data == 'check_invoice')
async def check_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    amount = data['amount']
    invoice = data['check_amount']

    await check_invoice(invoice, callback, state, amount)
    await callback.answer()


@user_private_router.callback_query(F.data == 'social_club')
async def social_gta5(callback: CallbackQuery):
    await callback.message.edit_text(
        '🛒 Social Club с GTA 5, без привязок Epic Games и Steam, аккаунт в одни руки 🛒 \n'
        '🧊 Аккаунт имеет бан в онлайне, но идеально подходит под сюжетку и игру на RP-серверах 🧊 \n'
        '\n'
        '🍾 После покупки вы получаете 🍾: \n'
        '🖥 Данные от аккаунта и почты в формате mail:pass \n'
        '🖥 Возможность полной перепривязки данных аккаунта \n'
        '🖥 Гарантию сутки после покупки аккаунта \n'
        '\n'
        '🦠 ВНИМАНИЕ!! 🦠 \n'
        '\n'
        '🩸 На аккаунте могут быть баны не некоторых серверах, в таких случаях замену не делаю!! 🩸',
        reply_markup=kb.buy_sc_kb())

@user_private_router.callback_query(F.data == 'epic_games')
async def epic_gta5(callback: CallbackQuery):
    await callback.message.edit_text(
        '🛒 Epic Games с GTA 5, без привязок Social Club и Steam, аккаунт в одни руки 🛒 \n'
        '🧊 Аккаунт имеет бан в онлайне, но идеально подходит под сюжетку и игру на RP-серверах 🧊 \n'
        '\n'
        '🍾 После покупки вы получаете 🍾: \n'
        '🖥 Данные от аккаунта и почты в формате mail:pass \n'
        '🖥 Возможность полной перепривязки данных аккаунта \n'
        '🖥 Гарантию сутки после покупки аккаунта \n'
        '\n'
        '🦠 ВНИМАНИЕ!! 🦠 \n'
        '\n'
        '🩸 На аккаунте могут быть баны не некоторых серверах, в таких случаях замену не делаю!! 🩸',
        reply_markup=kb.buy_eg_kb())


@user_private_router.callback_query(F.data == 'buy_sc')
async def buy_sc(callback: CallbackQuery):
    # В метод delete не нужно указывать chat_id, если удаляется последнее сообщение в диалоге
    await callback.message.delete()
    await get_item_sc(callback)


@user_private_router.callback_query(F.data == 'buy_eg')
async def buy_eg(callback: CallbackQuery):
    await callback.message.delete()
    await get_item_eg(callback)


@user_private_router.callback_query(F.data == 'back_inline_sc')
async def backup_sc(callback: CallbackQuery):
    await callback.message.edit_text('Список товаров', reply_markup=kb.items_kb())


@user_private_router.callback_query(F.data == 'back_inline_eg')
async def backup_eg(callback: CallbackQuery):
    await callback.message.edit_text('Список товаров', reply_markup=kb.items_kb())
