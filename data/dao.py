import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ProgrammingError
from dotenv import load_dotenv

from typing import Literal
import os


class SDA:
    def __init__(self):
        load_dotenv()
        username = os.getenv('USERNAME')
        password = os.getenv('PASSWORD')
        host = os.getenv('PG_HOST')
        port = os.getenv('PG_PORT')
        name = os.getenv('PG_NAME')

        # Create an engine
        self.engine_str = f'postgresql://{username}:{password}@{host}:{port}/{name}'

    def create_table_with_id(self,
                             data: pd.DataFrame,
                             target_table: str,
                             target_schema: str,
                             engine: Engine):
        create_table_sql = f"""
create table if not exists {target_schema}.{target_table} ( 
    id SERIAL PRIMARY KEY,
    {", ".join([f'"{col}" {self.get_sqlalchemy_type(data[col])}' for col in data.columns])}
)
"""
        with engine.connect() as connection:
            try:
                connection.execute(text(create_table_sql))
                connection.commit()
            except ProgrammingError as e:
                print(f"Table {target_schema}.{target_table} already exists or {e}")

    @staticmethod
    def get_sqlalchemy_type(series: pd.Series):
        if pd.api.types.is_integer_dtype(series):
            if series.max() > 2147483647 or series.min() < -2147483648:
                return "BIGINT"
            return "INTEGER"
        elif pd.api.types.is_float_dtype(series):
            return "FLOAT"
        elif pd.api.types.is_datetime64_any_dtype(series):
            return "TIMESTAMP"
        elif pd.api.types.is_bool_dtype(series):
            return "BOOLEAN"
        else:
            return "VARCHAR"

    def insert_dataframe(self,
                         data: pd.DataFrame,
                         target_table: str,
                         target_schema: str,
                         if_exists: Literal['append', 'replace'] = 'append',
                         verbose: bool = True,
                         override_id: bool = False):
        engine = create_engine(self.engine_str)
        # Check if the DataFrame has an 'id' column
        if not override_id and 'id' not in data.columns:
            self.create_table_with_id(data, target_table, target_schema, engine)
            if if_exists == 'replace':
                data.to_sql(
                    target_table,
                    con=engine,
                    schema=target_schema,
                    if_exists='append',
                    index=False
                )
            else:
                data.to_sql(
                    target_table,
                    con=engine,
                    schema=target_schema,
                    if_exists=if_exists,
                    index=False
                )
        else:
            data.to_sql(
                target_table,
                con=engine,
                schema=target_schema,
                if_exists=if_exists,
                index=False
            )

        if verbose:
            print(f"Inserted {len(data)} rows into {target_schema}.{target_table}")
        engine.dispose()

    def select_sql_dataframe(self, sql_statement: str, verbose: bool = True) -> pd.DataFrame:
        if verbose:
            print(f"Sending query: {sql_statement}")

        # Prepare connection
        engine = create_engine(self.engine_str)

        df = pd.read_sql(sql_statement, engine)
        engine.dispose()
        return df
