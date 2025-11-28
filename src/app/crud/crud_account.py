from fastcrud import FastCRUD
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.account import Account
from ..schemas.account import (
    AccountCreate,
    AccountCreateInternal,
    AccountDelete,
    AccountRead,
    AccountUpdate,
    AccountUpdateInternal,
)


async def select_all_account(db: AsyncSession) -> set[str]:
    stmt = select(Account.name)
    result = await db.execute(stmt)
    return set(result.scalars().all())



CRUDAccount = FastCRUD[
    AccountCreate, AccountCreateInternal, AccountRead, AccountUpdate, AccountUpdateInternal, AccountDelete
]

CRUDAccount.select_all_account = staticmethod(select_all_account)

crud_account = CRUDAccount(Account)
