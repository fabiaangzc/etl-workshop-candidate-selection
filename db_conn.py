# db_conn.py
from sqlalchemy import create_engine

user = 'root'
password = 'root'
host = 'localhost'
port = 3306
database = 'selection_dw'

engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{database}')