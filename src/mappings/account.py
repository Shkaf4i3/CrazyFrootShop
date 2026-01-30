from ..dto import AccountDto
from ..model import Account


def mapping_account(account: Account) -> AccountDto:
    return AccountDto(
        id=account.id,
        type_platform=account.type_platform,
        login=account.login,
        password=account.password,
        created_at=account.created_at,
    )
