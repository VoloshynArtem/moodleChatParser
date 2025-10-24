import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from datetime import datetime

import os
from dotenv import load_dotenv
from contextlib import contextmanager


load_dotenv()

new_db_name = "chat_read"
table_name = "chat_table"

def init_database():
    _create_user_if_not_exists()
    _create_database_if_not_exists()
    _create_table_if_not_exists()

@contextmanager
def _no_transaction_connection(dbname="postgres", user = os.getenv("NEW_USER"), password=os.getenv("NEW_USER_PASSWORD")):
    conn = psycopg2.connect(
            dbname=dbname,
            user=user, 
            password=password, 
            host="localhost"
            )
    try:
        conn.autocommit = True
        yield conn
    finally:
        conn.close()

def _connect_to_db(dbname = new_db_name, user = os.getenv("NEW_USER"), password=os.getenv("NEW_USER_PASSWORD")):
    return psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host="localhost",
        )


def _create_user_if_not_exists():
    new_user = os.getenv("NEW_USER")
    new_user_password = os.getenv("NEW_USER_PASSWORD")
    
    with _connect_to_db("postgres", os.getenv("ADMIN_USER"), os.getenv("ADMIN_PASSWORD")) as conn:
        with conn.cursor() as cur:   
            # Check if user exists
            cur.execute("SELECT 1 FROM pg_roles WHERE rolname=%s", (new_user,))
            exists = cur.fetchone()

            if not exists:
                # Create user
                cur.execute(sql.SQL(
                    "CREATE USER {} WITH PASSWORD %s"
                ).format(sql.Identifier(new_user)), [new_user_password])
                print(f"User '{new_user}' created.")
            


def _create_database_if_not_exists():
    global new_db_name
    new_user = os.getenv("NEW_USER")
    with _no_transaction_connection("postgres", os.getenv("ADMIN_USER"), os.getenv("ADMIN_PASSWORD")) as conn:
        with conn.cursor() as cur:
            # Check if database exists
            cur.execute("SELECT 1 FROM pg_database WHERE datname=%s", (new_db_name,))
            exists = cur.fetchone()

            if not exists:
                cur.execute(sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(new_db_name),
                    sql.Identifier(new_user)
                ))
                print(f"Database '{new_db_name}' created with owner '{new_user}'.")


def _create_table_if_not_exists():
    with _connect_to_db() as conn:
        with conn.cursor() as cur:

            cur.execute(sql.SQL("""
                CREATE TABLE IF NOT EXISTS {} (
                    dbid SERIAL PRIMARY KEY,
                    msg_id TEXT NOT NULL UNIQUE,
                    username TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL
                );
            """).format(sql.Identifier(table_name)))
            conn.commit()
            print(f"Table '{table_name}' checked/created.")



def insert_chat(msg_id, username, message, time_str):
    try:
        timestamp = None
        if time_str:
            today = datetime.today().date()
            timestamp = datetime.strptime(f"{today} {time_str}", "%Y-%m-%d %H:%M")

        with _connect_to_db() as conn:
            with conn.cursor() as cur:   

                insert_query = sql.SQL("""
                    INSERT INTO {} (msg_id, username, message, timestamp)
                    VALUES (%s, %s, %s, %s);
                """).format(sql.Identifier(table_name))

                cur.execute(insert_query, (msg_id, username, message, timestamp))
                conn.commit()
                
    except psycopg2.Error as e:
        print("Error inserting data:", e)



def check_exists(msg_id):
    with _connect_to_db() as conn:
        with conn.cursor() as cur:   
    
            cur.execute(
                f"""
                SELECT EXISTS (
                    SELECT 1 
                    FROM public.chat_table 
                    WHERE msg_id = '{msg_id}'
                ) AS record_exists;
                """
            )
            return cur.fetchone()[0]

