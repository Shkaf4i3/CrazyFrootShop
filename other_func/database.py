from psqlpy import ConnectionPool, QueryResult
from psqlpy.extra_types import BigInt

from aiogram.types import CallbackQuery

from other_func.config_reader import config
from other_func.encrypt_db import encrypt_password, decrypt_password, get_crypto_key


db_pool = ConnectionPool(password=config.password,
                         db_name=config.dbname,
                         username=config.user,
                         host=config.host,
                         port=config.port,
                         max_db_pool_size=5)


# Создание базы данных с таблицами Social Club, Epic Games и Users
async def create_table() -> None:
    cursor = await db_pool.connection()

    await cursor.execute(querystring="""CREATE TABLE IF NOT EXISTS Social_Club (
                        login TEXT NOT NULL,
                        password BYTEA NOT NULL)""")

    await cursor.execute(querystring="""CREATE TABLE IF NOT EXISTS Epic_Games (
                        login TEXT NOT NULL,
                        password BYTEA NOT NULL)""")

    await cursor.execute(querystring="""CREATE TABLE IF NOT EXISTS Users (
                        id SERIAL,
                        tg_id BIGINT,
                        first_name VARCHAR(255),
                        balance INTEGER DEFAULT 0)""")


# Вывод информации о балансе пользователя
async def get_count_balance(first_name):
    cursor = await db_pool.connection()

    data: QueryResult = await cursor.execute(
                            querystring="SELECT balance FROM Users WHERE first_name = ($1)",
                            parameters=[first_name])

    result = data.result()
    return result[0]["balance"]

# Добавление пользователя в базу данных
async def add_user(user_id: int, first_name: str):
    connection = await db_pool.connection()
    cursor = connection.transaction()

    await cursor.begin()

    data = await cursor.fetch(
                querystring="SELECT * FROM Users WHERE first_name = ($1)",
                parameters=[first_name],
            )

    if not data.result():
        await cursor.execute(
            querystring="INSERT INTO Users (tg_id, first_name) VALUES ($1, $2)",
            parameters=[BigInt(user_id), first_name],
        )
        await cursor.commit()


# Добавление товаров в БД
async def get_sc(login: str, password: str, key: bytes):
    connection = await db_pool.connection()
    cursor = connection.transaction()

    await cursor.begin()

    data = await cursor.fetch(
                querystring="SELECT * FROM Social_Club WHERE login = ($1)",
                parameters=[login])

    if data.result():
            return False
    else:
        encrypt_pass = encrypt_password(password=password, key=key)
        await cursor.execute(
            querystring="INSERT INTO Social_Club VALUES ($1, $2)",
            parameters=[login, encrypt_pass])
        await cursor.commit()
        return True


async def get_eg(login: str, password: str, key: bytes):
    connection = await db_pool.connection()
    cursor = connection.transaction()

    await cursor.begin()

    data = await cursor.fetch(
                querystring="SELECT * FROM Epic_Games WHERE login = ($1)",
                parameters=[login])

    if data.result():
            return False
    else:
        encrypt_pass = encrypt_password(password=password, key=key)
        await cursor.execute(
            querystring="INSERT INTO Epic_Games VALUES ($1, $2)",
            parameters=[login, encrypt_pass])
        await cursor.commit()
        return True


# Поиск товаров в таблицах Social Club и Epic Games
async def get_count_sc():
    cursor = await db_pool.connection()

    data: QueryResult = await cursor.execute(querystring="SELECT COUNT(*) FROM Social_Club")

    result = data.result()
    return result[0]["count"]

async def get_count_eg():
    cursor = await db_pool.connection()

    data: QueryResult = await cursor.execute(querystring="SELECT COUNT(*) FROM Epic_Games")

    result = data.result()
    return result[0]["count"]


# Список пользователей из БД
async def get_list_user():
    cursor = await db_pool.connection()

    data: QueryResult = await cursor.execute(querystring="SELECT * FROM Users")

    result = data.result()
    user_list = "\n".join([f"{user["tg_id"]} | {user["first_name"]} | {user["balance"]}" for user in result])

    return user_list


# Проверка баланса для покупки
async def check_balance_id(tg_id: int):
    connection = await db_pool.connection()
    cursor = connection.transaction()
    await cursor.begin()

    data: QueryResult = await cursor.execute(
        querystring="SELECT balance FROM Users WHERE tg_id = ($1)",
        parameters=[BigInt(tg_id)]
    )
    result = data.result()
    balance = result[0]["balance"]

    if balance >= 250:
        await cursor.execute(querystring="UPDATE users SET balance = balance - 250 WHERE tg_id = ($1)",
                             parameters=[BigInt(tg_id)])
        await cursor.commit()
        return True
    else:
        return False


# Выдача товаров из бд
async def get_item_sc(callback: CallbackQuery):
    cursor = await db_pool.connection()
    data: QueryResult = await cursor.fetch(
        querystring="SELECT login, password FROM Social_Club LIMIT 1"
        )
    result = data.result()

    if result:
        if await check_balance_id(callback.from_user.id):
            log = result[0]["login"]
            pas = result[0]["password"]
            key = await get_crypto_key()
            decrypt_pas = decrypt_password(password=pas, key=key)

            await callback.answer()
            await callback.message.answer(f"Твои данные: {log}:{decrypt_pas}")
            await cursor.execute(
                    querystring="DELETE FROM Social_Club WHERE login = ($1) AND password = ($2)",
                    parameters=(log, pas))
        else:
            await callback.answer()
            await callback.message.answer("Недостаточно средств на счету")
    else:
        await callback.answer()
        await callback.message.answer("В данный момент товаров нет 😰")

async def get_item_eg(callback: CallbackQuery):
    cursor = await db_pool.connection()
    data: QueryResult = await cursor.fetch(
        querystring="SELECT login, password FROM Epic_Games LIMIT 1"
        )
    result = data.result()

    if result:
        if await check_balance_id(callback.from_user.id):
            log = result[0]["login"]
            pas = result[0]["password"]
            key = await get_crypto_key()
            decrypt_pas = decrypt_password(password=pas, key=key)

            await callback.answer()
            await callback.message.answer(f"Твои данные: {log}:{decrypt_pas}")
            await cursor.execute(
                    querystring="DELETE FROM Epic_Games WHERE login = ($1) AND password = ($2)",
                    parameters=(log, pas))
        else:
            await callback.answer()
            await callback.message.answer("Недостаточно средств на счету")
    else:
        await callback.answer()
        await callback.message.answer("В данный момент товаров нет 😰")


# Пополнение баланса с платежа
async def app_balance(amount, tg_id):
    connection = await db_pool.connection()
    cursor = connection.transaction()
    await cursor.begin()

    await cursor.execute(querystring="UPDATE users SET balance = ($1) - 250 WHERE tg_id = ($2)",
                         parameters=[amount, BigInt(tg_id)])
    await cursor.commit()
