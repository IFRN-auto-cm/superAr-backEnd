import os

import MySQLdb
from MySQLdb.cursors import DictCursor

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# ============================================================
# SQLAlchemy
# ============================================================

class Base(DeclarativeBase):
    pass


DATABASE_URL = (
    f"mysql+mysqldb://"
    f"{os.getenv('MYSQL_USER')}:"
    f"{os.getenv('MYSQL_PASSWORD')}@"
    f"{os.getenv('HOST_DATABASE')}:"
    f"{os.getenv('DB_PORT', '3306')}/"
    f"{os.getenv('MYSQL_DATABASE')}"
)


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)


def get_session():
    return SessionLocal()

# ============================================================
# MySQLdb - código legado
# ============================================================

def get_db():

    return MySQLdb.connect(
        host=os.getenv("HOST_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        passwd=os.getenv("MYSQL_PASSWORD"),
        db=os.getenv("MYSQL_DATABASE"),
        port=int(os.getenv("DB_PORT", "3306")),
        cursorclass=DictCursor
    )


def executar_select(sql, valores=None):

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(sql, valores or ())
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


def executar_insert(sql, valores=None):

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(sql, valores or ())
        conn.commit()

        return cursor.lastrowid

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


def executar_update(sql, valores=None):

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute(sql, valores or ())
        conn.commit()

        return cursor.rowcount

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


def executar_delete(sql, valores=None):

    return executar_update(sql, valores)


def executar_insert_many(sql, valores):

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.executemany(sql, valores)
        conn.commit()

        return cursor.rowcount

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()