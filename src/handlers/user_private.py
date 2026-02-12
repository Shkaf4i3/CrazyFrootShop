from logging import getLogger
from asyncio import sleep

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from aiocryptopay.exceptions.factory import CodeErrorFactory
from aiocryptopay.models.invoice import InvoiceStatus

from ..service import UserService, AccountService
from ..aiogram_functions import kb, Balance
from ..settings import settings
from ..client import CryptoPay


router = Router()
crypto_pay = CryptoPay()
logger = getLogger(__name__)


@router.message(CommandStart())
async def start_message(message: Message, user_service: UserService) -> None:
    await user_service.save_user(
        tg_id=message.from_user.id,
        tg_username=message.from_user.first_name,
    )
    await message.answer(
        f"Hello, {message.from_user.first_name}\n"
        "Добро пожаловать в самый лучший магазин с аккаунтами GTA 5\n"
        "Для работы воспользуйся меню ниже 👇",
        reply_markup=kb.main_kb(),
    )


@router.message(Command("help"))
async def help_message(message: Message) -> None:
    await message.answer(
        "☺️ В данном боте вы сможете купить по хорошей цене качественные аккаунты GTA 5 ☺️\n"
        "🧩 Площадки с аккаунтами - Social Club, Epic Games 🧩\n"
        "\n"
        f"По всем вопросам о боте обращаться - 👉 {settings.admin_username} 👈",
    )


@router.message(Command("menu"))
async def menu_message(message: Message) -> None:
    await message.answer(
        "Вы вернулись в меню",
        reply_markup=kb.main_kb(),
    )


@router.message(F.text == "🛒 Купить аккаунт 🛒")
async def get_list_accounts(message: Message) -> None:
    await message.answer(
        "Ниже приведен список доступных платформ",
        reply_markup=kb.available_platforms(),
    )


@router.message(F.text == "👥 Профиль 👥")
async def get_user_profile(message: Message, user_service: UserService) -> None:
    check_balance = await user_service.get_user(tg_id=message.from_user.id)

    await message.answer(
        f"🍬 ID: <code> {message.from_user.id} </code> \n"
        f"🤩 Имя: {message.from_user.first_name} \n"
        "\n"
        f"Баланс - {check_balance.balance} rub",
        reply_markup=kb.top_up_balance(),
    )


@router.message(F.text == "🌍 Пользовательское соглашение 🌍")
async def user_agreement(message: Message) -> None:
    await message.answer(
        "Перед использованием бота прочтите данное соглашение \n"
        f"<a href='{settings.user_agreement}'>тык</a>",
        disable_web_page_preview=True,
    )


@router.message(F.text == "🖥 Наличие товаров 🖥")
async def get_count_accounts(message: Message, account_service: AccountService) -> None:
    social_accounts = await account_service.get_count_accounts(type_platform="Social Club")
    epic_accounts = await account_service.get_count_accounts(type_platform="Epic Games")

    await message.answer(
        f"💚 Social Club 💚 - {social_accounts} шт.\n"
        f"❤️ Epic Games ❤️ - {epic_accounts} шт."
    )


@router.message(F.text == "❌ Отменить пополнение ❌")
async def cancel_top_up(message: Message, state: FSMContext) -> None:
    state_data = await state.get_state()
    if state_data is None:
        await message.answer(
            "Вы не запрашивали пополнение баланса",
            reply_markup=kb.main_kb(),
        )
        return

    await state.clear()
    await message.answer(
        "Вы отменили пополнение",
        reply_markup=kb.main_kb(),
    )


@router.callback_query(F.data == "top_up_balance")
async def get_amount(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Balance.amount)
    await callback.message.answer(
        "Введите сумму для пополнения",
        reply_markup=kb.cancel_top_up(),
    )


@router.message(Balance.amount)
async def proccess_top_up_balance(
    message: Message,
    state: FSMContext,
) -> None:
    try:
        await state.update_data(amount=int(message.text))
        data = await state.get_data()
        amount = data.get("amount")

        created_invoice = await crypto_pay.create_invoice(amount=amount)
        await state.update_data(invoice_id=created_invoice.invoice_id)

        await message.answer(
            "Перейдите по ссылке, чтобы произвести оплату\n"
            f"{created_invoice.bot_invoice_url}",
            reply_markup=kb.check_invoice(),
        )
    except ValueError:
        await message.answer(
            "Вы ввели не число, попробуйте еще раз",
        )
        return
    except CodeErrorFactory as e:
        await message.answer(
            "Ошибка при создании платежа, попробуйте снова",
            reply_markup=kb.main_kb(),
        )
        logger.error("Произошла непредвиденная ошибка - %s", str(e))
        await state.clear()


@router.callback_query(F.data == "check_invoice")
async def check_invoice(callback: CallbackQuery, state: FSMContext, user_service: UserService) -> None:
    data = await state.get_data()
    invoice_id = data.get("invoice_id")
    amount = data.get("amount")

    try:
        checked_invoice = await crypto_pay.check_invoice(invoice_id=invoice_id)
        if checked_invoice.status == InvoiceStatus.PAID:
            await user_service.update_balance_user(
                tg_id=callback.from_user.id,
                amount=amount,
                type_update="plus",
            )
            await callback.message.answer(
                "✅ Платеж прошел, ваш баланс пополен ✅",
                reply_markup=kb.main_kb(),
            )
            await state.clear()
        elif checked_invoice.status == InvoiceStatus.ACTIVE:
            response_message = await callback.message.answer(
                "❗️ Платеж еще не прошел ❗️"
            )

            await sleep(delay=5)
            await callback.message.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=response_message.message_id,
            )
        elif checked_invoice.status == InvoiceStatus.EXPIRED:
            response_message = await callback.message.answer(
                "❌ Ваш платеж устарел, создайте новый ❌",
                reply_markup=kb.main_kb(),
            )

            await sleep(delay=5)
            await callback.message.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=response_message.message_id,
            )
            await state.clear()
    except Exception as e:
        logger.error("Произошла непредвиденная ошибка - %s", str(e))


@router.callback_query(F.data.in_(["social_club", "epic_games"]))
async def get_info_about_platforms(callback: CallbackQuery) -> None:
    type_platform = None
    if callback.data == "social_club":
        type_platform = "🛒 Social Club с GTA 5, без привязок Epic Games и Steam, аккаунт в одни руки 🛒 \n"
    elif callback.data == "epic_games":
        type_platform = "🛒 Epic Games с GTA 5, без привязок Social Club и Steam, аккаунт в одни руки 🛒 \n"

    message_text = (
        type_platform +
        "🧊 Аккаунт может иметь бан в онлайне, но идеально подходит под сюжетку и игру на RP-серверах 🧊 \n"
        "\n"
        "🍾 После покупки вы получаете 🍾: \n"
        "🖥 Данные от аккаунта и почты в формате mail:pass \n"
        "🖥 Возможность полной перепривязки данных аккаунта \n"
        "🖥 Гарантию сутки после покупки аккаунта \n"
        "\n"
        "🦠 ВНИМАНИЕ!! 🦠 \n"
        "\n"
        "🩸 На аккаунте могут быть баны не некоторых серверах, в таких случаях замену не делаю!! 🩸"
    )

    await callback.message.edit_text(
        text=message_text,
        reply_markup=kb.buy_account(type_platform=callback.data),
    )


@router.callback_query(F.data.startswith("buy_account_"))
async def buy_account_by_type_platform(
    callback: CallbackQuery,
    account_service: AccountService,
    user_service: UserService,
) -> None:
    data = callback.data.split(sep="_")
    type_platform = data[2]
    exists_user = await user_service.get_user(tg_id=callback.from_user.id)

    if exists_user and exists_user.balance >= 300:
        try:
            if type_platform.startswith("social"):
                available_account = await account_service.get_account_by_type_platform(
                    type_platform="Social Club",
                )
            elif type_platform.startswith("epic"):
                available_account = await account_service.get_account_by_type_platform(
                    type_platform="Epic Games",
                )

            if not available_account:
                await callback.message.answer(
                    "Сейчас нету доступных аккаунтов под эту платформу для покупки",
                )
                return

            await user_service.update_balance_user(
                tg_id=exists_user.tg_id,
                amount=300,
                type_update="minus",
            )
            await account_service.delete_account(id=available_account.id)
            await callback.message.delete()

            await callback.message.answer(
                f"Ваш аккаунт - {available_account.login}:{available_account.password}",
            )
        except KeyError as e:
            logger.error("Произошла непредвиденная ошибка - %s", str(e))
            await callback.message.answer(
                "Произошла ошибка при покупке, попробуйте еще раз",
                reply_markup=kb.available_platforms(),
            )
    else:
        await callback.message.answer(
            "На вашем балансе недостаточно средств",
        )


@router.callback_query(F.data == "go_back")
async def go_back_to_available_platforms(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        text="Вы вернулись в меню доступных платформ",
        reply_markup=kb.available_platforms(),
    )


@router.callback_query(F.data == "close_window")
async def close_window(callback: CallbackQuery) -> None:
    await callback.message.delete()
