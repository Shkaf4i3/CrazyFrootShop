from ..repo import AccountRepo, UnitOfWork, transactional
from ..dto import AccountDto
from ..model import Account
from ..mappings import account_mappings


class AccountService:
    def __init__(self, unit_of_work: UnitOfWork, account_repo: AccountRepo):
        self.unit_of_work = unit_of_work
        self.account_repo = account_repo


    @transactional
    async def save_account(self, type_platform: str, login: str, password: str) -> None:
        exists_account = await self.account_repo.get_account_by_login(
            login=login,
            type_platform=type_platform,
        )
        if exists_account:
            raise KeyError(f"Аккаунт с айди {exists_account.id} уже существует")

        new_account = Account(
            type_platform=type_platform,
            login=login,
            password=password,
        )
        await self.account_repo.save_account(account=new_account)


    @transactional
    async def delete_account(self, id: str) -> None:
        exists_account = await self.account_repo.get_account_by_id(id=id)
        if not exists_account:
            raise KeyError(f"Аккаунт с айди {id} не существует")

        await self.account_repo.delete_account(account=exists_account)


    async def get_count_accounts(self, type_platform: str) -> int:
        count_accounts = await self.account_repo.get_count_accounts(type_platform=type_platform)
        if not count_accounts:
            return 0

        return count_accounts


    async def get_account_by_type_platform(self, type_platform: str) -> AccountDto | None:
        exists_account = await self.account_repo.get_account_by_type_platform(
            type_platform=type_platform,
        )
        if not exists_account:
            return None

        return account_mappings.mapping_account(account=exists_account)
