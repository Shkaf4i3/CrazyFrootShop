from typing import Tuple
from logging import getLogger

from ..service import AccountService
from ..settings import settings


logger = getLogger(__name__)


async def handle_file_to_save_account(
    file: list[str],
    account_service: AccountService,
) -> Tuple[int, int]:
    added_accounts = 0
    missed_account = 0

    for item in file:
        account = item.split(sep=":")

        if len(account) != 3:
            missed_account += 1
            continue
        if settings.available_platforms.get(account[0]) is None:
            missed_account += 1
            continue

        try:
            await account_service.save_account(
                type_platform=account[0],
                login=account[1],
                password=account[2],
            )
            added_accounts += 1
        except KeyError as e:
            logger.error("%s", str(e))
            missed_account += 1
            continue
        except Exception as e:
            logger.error("Произошла непредвиденная ошибка - %s", str(e))
            missed_account += 1
            continue

    return added_accounts, missed_account
