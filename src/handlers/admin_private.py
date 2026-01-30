from logging import getLogger

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
    TelegramAPIError,
)

from ..aiogram_functions import IsAdmin, kb, Mailing, Account
from ..service import UserService, AccountService
from ..settings import settings


router = Router()
router.message.filter(IsAdmin())
logger = getLogger(__name__)


@router.message(Command("admin_menu"))
async def admin_menu_message(message: Message) -> None:
    await message.answer(
        f"Hello, {message.from_user.first_name}\n"
        "Добро пожаловать в админ панель",
        reply_markup=kb.admin_kb(),
    )


@router.message(F.text == "👤 Список пользователей 👤")
async def get_list_users(message: Message, user_service: UserService) -> None:
    list_users_from_db = await user_service.get_list_users()
    exists_users = "\n".join(
        f"Id - {user.tg_id} | Tg_name - {user.tg_username} | Balance - {user.balance} rub"
        for user in list_users_from_db
    )
    await message.answer(
        "Список пользователей: \n"
        f"{exists_users}",
    )


@router.message(F.text == "Вернуться в меню пользователя 👈")
async def return_to_user_menu(message: Message) -> None:
    await message.answer(
        "Вы вернулись в меню",
        reply_markup=kb.main_kb(),
    )


@router.message(F.text == "✅ Рассылка всем пользователям бота ✅")
async def get_message_for_mailing(message: Message, state: FSMContext) -> None:
    await state.set_state(Mailing.mailing_message)
    await message.answer(
        "Отправьте сообщение для рассылки (поддерживаются фотки и документы)",
        reply_markup=kb.cancel_mailing(),
    )


@router.message(F.text == "❌ Отменить рассылку ❌")
async def cancel_send_mailing(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            "Вы не запрашивали рассылку по пользователям!",
            reply_markup=kb.admin_kb(),
        )
        return

    await state.clear()
    await message.answer("Вы отменили рассылку", reply_markup=kb.admin_kb())


@router.message(Mailing.mailing_message)
async def send_mailing_message(message: Message, state: FSMContext, user_service: UserService) -> None:
    message_text = message.text if message.text or message.caption else None
    message_media = message.photo[-1].file_id if message.photo or message.document.file_id else None
    available_users = await user_service.get_list_users()

    await state.update_data(mailing_message_text=message_text)
    await state.update_data(mailing_message_media=message_media)
    data = await state.get_data()

    for user in available_users:
        try:
            if message.photo:
                await message.bot.send_photo(
                    chat_id=user.tg_id,
                    photo=data.get("mailing_message_media"),
                    caption=data.get("mailing_message_text"),
                )
            elif message.document:
                await message.bot.send_document(
                    chat_id=user.tg_id,
                    document=data.get("mailing_message_media"),
                    caption=data.get("mailing_message_text"),
                )
            elif message.text:
                await message.bot.send_message(
                    chat_id=user.tg_id,
                    text=data.get("mailing_message_text"),
                )
        except (TelegramBadRequest, TelegramAPIError, TelegramForbiddenError, TelegramRetryAfter) as e:
            logger.error(
                "Ошибка отправки сообщения пользователю %s - %s",
                user.tg_id,
                str(e),
            )

    await message.answer(
        "❗️ Рассылка запущена ❗️",
        reply_markup=kb.main_kb(),
    )
    await state.clear()


@router.message(F.text == "📕 Добавить товар 📕")
async def get_account_for_saving(message: Message, state: FSMContext) -> None:
    await state.set_state(Account.account)
    await message.answer(
        "Отправьте данные аккаунта в формате 'type_platform:login:password'\n"
        "Доступные площадки для добавления - Social Club и Epic Games",
        reply_markup=kb.cancel_saving(),
    )


@router.message(F.text == "❌ Отменить сохранение аккаунта ❌")
async def cancel_saving_account(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(
            "Вы не запрашивали доступ к добавлению аккаунта",
            reply_markup=kb.admin_kb(),
        )
        return

    await message.answer(
        "Вы отменили запрос на сохранение аккаунта",
        reply_markup=kb.admin_kb(),
    )
    await state.clear()


@router.message(Account.account)
async def save_account_in_db(
    message: Message,
    state: FSMContext,
    account_service: AccountService,
) -> None:
    await state.update_data(account=message.text.split(sep=":"))
    data = await state.get_data()
    account = data.get("account")

    if len(account) != 3:
        await message.answer("Вы отправили данные в неправильном формате!")
        return

    if settings.available_platforms.get(account[0]) is None:
        await message.answer("Вы указали недоступную платформу для работы!")
        return

    try:
        saved_account = await account_service.save_account(
            type_platform=account[0],
            login=account[1],
            password=account[2],
        )
        await message.answer(
            f"Аккаунт {saved_account.id} сохранен",
            reply_markup=kb.admin_kb(),
        )
    except KeyError as e:
        await message.answer(text=str(e).replace("'", ""), reply_markup=kb.admin_kb())

    await state.clear()
