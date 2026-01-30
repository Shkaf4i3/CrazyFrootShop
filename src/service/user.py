from ..repo import UnitOfWork, UserRepo, transactional
from ..model import User
from ..dto import UserDto
from ..mappings import user_mappings


class UserService:
    def __init__(self, unit_of_work: UnitOfWork, user_repo: UserRepo):
        self.unit_of_work = unit_of_work
        self.user_repo = user_repo


    @transactional
    async def save_user(self, tg_id: int, tg_username: str) -> None:
        exists_user = await self.user_repo.get_user_by_tg_id(tg_id=tg_id)
        if exists_user:
            return

        new_user = User(tg_id=tg_id, tg_username=tg_username)
        await self.user_repo.save_user(user=new_user)


    async def get_user(self, tg_id: int) -> UserDto | None:
        exists_user = await self.user_repo.get_user_by_tg_id(tg_id=tg_id)
        if not exists_user:
            return None

        return user_mappings.mapping_user(user=exists_user)


    async def get_list_users(self) -> list[UserDto]:
        exists_users = await self.user_repo.get_list_users()
        return [user_mappings.mapping_user(user=user) for user in exists_users]


    @transactional
    async def update_balance_user(self, tg_id: int, amount: int, type_update: str) -> UserDto:
        exists_user = await self.user_repo.get_user_by_tg_id(tg_id=tg_id)
        if exists_user:
            if type_update == "plus":
                exists_user.balance += amount
            elif type_update == "minus":
                exists_user.balance -= amount
            await self.user_repo.save_user(user=exists_user)
