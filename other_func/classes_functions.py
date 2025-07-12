from AsyncPayments.cryptoBot import AsyncCryptoBot
from cachetools import TTLCache
from typing import Any, Awaitable, Callable, Dict

from aiogram.filters import Filter
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext

from other_func.database import app_balance
from other_func.config_reader import config
import reply as kb


cryptobot = AsyncCryptoBot(token=config.pay_key)


# Проверка пользователя на наличие в списке admin_id для доступа к админским командам и запросам
class IsAdmin(Filter):
    @staticmethod
    async def __call__(message: Message):
        return str(message.from_user.id) in config.admin_id


# Классы для работы через FSM
class Add_sc(StatesGroup):
    info = State()

class Add_eg(StatesGroup):
    info = State()

class Balance_state(StatesGroup):
    amount = State()
    invoice_id = State()
    check_amount = State()


# Класс для проверки наличия подписки пользователя на телеграм канал
class CheckSubscribe(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        chat_members = await event.bot.get_chat_member(
            chat_id=config.channel_id,
            user_id=event.from_user.id)

        if chat_members.status == 'left':
            await event.answer('Для продолжения работы подпишитесь на канал 💚',
                           reply_markup=kb.url_channel())
        else:
            return await handler(event, data)


# Класс для анти-спам системы (кд сообщений - 1 секунда)
class AntiFloodMiddleware(BaseMiddleware):

    def __init__(self, time_limit: int=1) -> None:
        self.limit = TTLCache(maxsize=10_000, ttl=time_limit)

    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        if event.chat.id in self.limit:
            return
        else:
            self.limit[event.chat.id] = None
        return await handler(event, data)


# Работа с платежной системой CryptoBot
async def check_balance() -> str:
    balance_all = await cryptobot.get_balance()

    for balance in balance_all:
        text = (f'Доступно {balance.currency_code} - {balance.available} \n'
                f'Холд  - {balance.onhold}')

        return text


async def delete_invoice(invoice_id: int) -> None:
    delete_invoice = await cryptobot.delete_invoice(invoice_id=int(invoice_id))
    return delete_invoice


async def check_invoice(invoice_id: list,
                        callback: CallbackQuery,
                        state: FSMContext,
                        amount) -> None:
    info_crypto_bot = await cryptobot.get_invoices(invoice_ids=invoice_id, asset='USDT', count=1)

    if info_crypto_bot.status == 'active':
        await callback.message.answer('Ваш платеж находится в активном состоянии, повторите попытку',
                                      reply_markup=ReplyKeyboardRemove())
        return
    elif info_crypto_bot.status == 'expired':
        await callback.message.answer('Время платежа истекло, создайте новую заявку',
                                      reply_markup=kb.main_kb())
        return
    elif info_crypto_bot.status == 'paid':
        await callback.message.answer('Ваш платеж принят, вы вернулись в главное меню',
                                      reply_markup=kb.main_kb())
        await app_balance(amount, callback.from_user.id)
        await delete_invoice(int(invoice_id))

    await state.clear()
