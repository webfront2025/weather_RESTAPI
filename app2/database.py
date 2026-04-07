import psycopg2
#                            connect to database
"""
def get_connection():
    conn = psycopg2.connect(
        host="localhost",   # Important!
        port=5432,
        database="vejr_db",
        user="postgres",
        password="password"
    )
    return conn

import psycopg2
"""

def get_connection():
    return psycopg2.connect(
        host="localhost",   # because DB inside Docker &  port be  expose --- in Docker have  => DB_HOST=db
        port=5432,
        database="vejr_db",
        user="postgres",
        password="password"
    )


def get_all_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
    """)

    tables = [t[0] for t in cursor.fetchall()]

    cursor.close()
    conn.close()

    return tables


def get_columns(table_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s
    """, (table_name,))

    columns = [col[0] for col in cursor.fetchall()]

    cursor.close()
    conn.close()

    return columns



