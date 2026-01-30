from typing import Annotated

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from ..repo import UnitOfWork, UserRepo, AccountRepo
from ..service import UserService, AccountService
from ..deps import open_session


def get_user_repo(session: Annotated[AsyncSession, Depends(open_session)]) -> UserRepo:
    return UserRepo(session=session)


def get_account_repo(session: Annotated[AsyncSession, Depends(open_session)]) -> AccountRepo:
    return AccountRepo(session=session)


def get_unit_of_work(session: Annotated[AsyncSession, Depends(open_session)]) -> UnitOfWork:
    return UnitOfWork(session=session)


def get_user_service(
    user_repo: Annotated[UserRepo, Depends(get_user_repo)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> UserService:
    return UserService(unit_of_work=unit_of_work, user_repo=user_repo)


def get_account_service(
    account_repo: Annotated[AccountRepo, Depends(get_account_repo)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
) -> AccountService:
    return AccountService(unit_of_work=unit_of_work, account_repo=account_repo)
