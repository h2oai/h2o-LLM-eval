import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, Union
import psycopg


@dataclass
class PSQLConfig:
    host: str
    dbname: str
    user: str
    password: str

    @classmethod
    def from_env(cls):
        return PSQLConfig(
            host=os.getenv("POSTGRES_HOST", ""),
            dbname=os.getenv("POSTGRES_DB", ""),
            user=os.getenv("POSTGRES_USER", ""),
            password=os.getenv("POSTGRES_PASSWORD", ""),
        )


async def select_from(db_config: PSQLConfig, sql_select_from: str, row_factory=None):
    # Connect to an existing database
    async with await psycopg.AsyncConnection.connect(
        **asdict(db_config),
    ) as a_conn:
        # Open a cursor to perform database operations
        async with a_conn.cursor(row_factory=row_factory) as a_cur:  # type: ignore
            await a_cur.execute(sql_select_from)  # type: ignore
            rows = await a_cur.fetchall()
        return rows


async def insert_into(
    db_config: PSQLConfig, sql_insert_into: str, values: Dict[str, Any]
):
    # Connect to an existing database
    async with await psycopg.AsyncConnection.connect(
        **asdict(db_config), autocommit=True
    ) as a_conn:
        # Open a cursor to perform database operations
        async with a_conn.cursor() as a_cur:
            await a_cur.execute(sql_insert_into, values)  # type: ignore


async def sql_execute(db_config: PSQLConfig, sql_query: Union[str, Any]):
    # Connect to an existing database
    async with await psycopg.AsyncConnection.connect(
        **asdict(db_config), autocommit=True
    ) as a_conn:
        # Open a cursor to perform database operations
        async with a_conn.cursor() as a_cur:
            await a_cur.execute(sql_query)  # type: ignore
