from aiogram.fsm.state import State, StatesGroup


class Mailing(StatesGroup):
    mailing_message = State()


class Account(StatesGroup):
    account = State()


class Balance(StatesGroup):
    amount = State()
