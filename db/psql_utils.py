import os
from configparser import ConfigParser
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
    def from_file(cls, config_file: str, section: str = "postgresql"):
        config_parser = ConfigParser()
        config_parser.read(config_file)
        db_config = {}
        if config_parser.has_section(section):
            params = config_parser.items(section)
            for param in params:
                db_config[param[0]] = param[1]
        else:
            raise Exception(f'Section "{section}" not found in the file {config_file}')
        return PSQLConfig(**db_config)

    @classmethod
    def from_env(cls):
        return PSQLConfig(
            host=os.getenv("RDS_HOSTNAME", ""),
            dbname=os.getenv("RDS_DB_NAME", ""),
            user=os.getenv("RDS_USERNAME", ""),
            password=os.getenv("RDS_PASSWORD", ""),
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
