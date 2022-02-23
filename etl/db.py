import datetime
from select import select
from sqlite3 import Cursor
from .logs import die
from geoalchemy2 import Geometry, WKTElement
import sqlalchemy as sql
import pandas as pd
import geopandas as gpd



class DBController:
    def __init__(self, host: str, port: str, database: str, username: str, password: str):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.uri = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        
    def select_data(self, query: str) -> pd.DataFrame:
        """This functions abstracts the `SELECT` queries

        Args:
            query (str): the select query to be executed

        Returns:
            pd.DataFrame: the selection
        """
        try:
            con = sql.create_engine(self.uri)
            # As the purpose of the porject is based on dates selection, here was neccesary to personalize the format date

            select_df = pd.read_sql(query, con, parse_dates={ "date": {"format": "%Y-%m-%d"}})
        except Exception as e:
            die(f"select_data: {e}")
        return select_df

    def insert_data(self, df: pd.DataFrame, schema: str, table: str, chunksize: int=100) -> None:
        """This function abstracts the `INSERT` queries

        Args:
            df (pd.DataFrame): dataframe to be inserted
            schema (str): the name of the schema
            table (str): the name of the table
            chunksize (int): the number of rows to insert at the time
        """
        try:
            engine = sql.create_engine(self.uri)
            with engine.connect() as con:
                tran = con.begin()
                df.to_sql(
                    name=table, schema=schema,
                    con=con, if_exists="append", index=False,
                    chunksize=chunksize, method="multi"
                )
                tran.commit()
        except Exception as e:
            if 'tran' in locals():
                tran.rollback()
            die(f"{e}")
    
    def insert_geodata(self, gdf: gpd.GeoDataFrame, schema: str, table: str) -> None:
        """This function abstracts the `INSERT` geojson data into database

        Args:
            df (pd.DataFrame): dataframe to be inserted
            schema (str): the name of the schema
            table (str): the name of the table
        """
        try:
            engine = sql.create_engine(self.uri)
            with engine.connect() as con:
                tran = con.begin()
                gdf.to_postgis(name=table, schema=schema, con=con, if_exists="replace", index=False)
                tran.commit()
        except Exception as e:
            if 'tran' in locals():
                tran.rollback()
            die(f"{e}")
    