import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.errors import UniqueViolation
from datetime import datetime

import os
from dotenv import load_dotenv


load_dotenv()


host = "localhost"
admin_user = os.getenv("ADMIN_USER")
admin_password = os.getenv("ADMIN_PASSWORD")

new_user = os.getenv("NEW_USER")
new_user_password = os.getenv("NEW_USER_PASSWORD")

new_db_name = "chat_read"
table_name = "chat_table"

def init_database():
    _create_user_if_not_exists()
    _create_database_if_not_exists()
    _create_table_if_not_exists()

def _create_user_if_not_exists():
    conn = psycopg2.connect(
        dbname="postgres", user=admin_user, password=admin_password, host=host
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Check if user exists
    cur.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (new_user,))
    exists = cur.fetchone()

    if not exists:
        # Create user
        cur.execute(sql.SQL(
            "CREATE USER {} WITH PASSWORD %s"
        ).format(sql.Identifier(new_user)), [new_user_password])
        print(f"User '{new_user}' created.")
    else:
        print(f"User '{new_user}' already exists.")
        

    cur.close()
    conn.close()

def _create_database_if_not_exists():
    conn = psycopg2.connect(
        dbname="postgres", user=admin_user, password=admin_password, host=host
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Check if database exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (new_db_name,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {} OWNER {}").format(
            sql.Identifier(new_db_name),
            sql.Identifier(new_user)
        ))
        print(f"Database '{new_db_name}' created with owner '{new_user}'.")
    else:
        print(f"Database '{new_db_name}' already exists.")

    cur.close()
    conn.close()

def _create_table_if_not_exists():
    conn = psycopg2.connect(
        dbname=new_db_name, user=new_user, password=new_user_password, host=host
    )
    cur = conn.cursor()

    cur.execute(sql.SQL("""
        CREATE TABLE IF NOT EXISTS {} (
            dbid SERIAL PRIMARY KEY,
            msg_id TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            time TIME NOT NULL
        );
    """).format(sql.Identifier(table_name)))
    conn.commit()
    print(f"Table '{table_name}' checked/created.")

    cur.close()
    conn.close()


def insert_chat(msg_id, username, message, time_str):
    try:
        time_obj = datetime.strptime(time_str, "%H:%M").time()

        conn = psycopg2.connect(
            dbname=new_db_name,
            user=new_user,
            password=new_user_password,
            host=host
        )
        cur = conn.cursor()

        insert_query = sql.SQL("""
            INSERT INTO {} (msg_id, username, message, time)
            VALUES (%s, %s, %s, %s);
        """).format(sql.Identifier(table_name))

        cur.execute(insert_query, (msg_id, username, message, time_obj))
        conn.commit()
        

        cur.close()
        conn.close()

    except UniqueViolation:
        conn.rollback()

    except psycopg2.Error as e:
        print("Error inserting data:", e)

    finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

