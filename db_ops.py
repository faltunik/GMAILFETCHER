import sqlite3


class DB_Connections:

    @staticmethod
    def create_table():
        print("Creating DB")
        con = sqlite3.connect('email.db')
        cur = con.cursor()
        cur.execute(''' CREATE TABLE IF NOT EXISTS emails (id INTEGER PRIMARY KEY AUTOINCREMENT, sender TEXT, receiver TEXT, subject TEXT, snippet TEXT, received_on DATE, read INTEGER DEFAULT 0)''')
        con.commit()
        con.close()

    @staticmethod
    def describe_table():
        con = sqlite3.connect('email.db')
        cur = con.cursor()
        cur.execute('''PRAGMA table_info(emails)''')
        print(cur.fetchall())
        con.close()

    @staticmethod
    def insert_into_table(values: list[tuple]) -> None:
        values = str(values).replace('[', '').replace(']', '')
        con = sqlite3.connect('email.db')
        cur = con.cursor()
        cur.execute(
            f'''INSERT INTO emails (sender, receiver, subject, snippet, received_on, read) VALUES {values}''')
        con.commit()
        con.close()

    @staticmethod
    def empty_table(db_name: str, table_name: str) -> None:
        con = sqlite3.connect(db_name)
        cur = con.cursor()
        cur.execute('''DELETE FROM {}'''.format(table_name))
        con.commit()
        con.close()

    @staticmethod
    def select_from_table(where=None) -> list[tuple]:
        con = sqlite3.connect('email.db')
        cur = con.cursor()
        if where:
            print('''SELECT * FROM emails WHERE ''' + where)
            cur.execute('''SELECT * FROM emails WHERE ''' + where)
        else:
            cur.execute('''SELECT * FROM emails''')
        result = cur.fetchall()
        print(result)
        con.close()
        return result

    @staticmethod
    def delete_email(where: str) -> None:
        con = sqlite3.connect('email.db')
        cur = con.cursor()
        # fetch id's of emails that match the where clause
        cur.execute(f'''SELECT id FROM emails WHERE {where}''')
        ids = cur.fetchall()
        print("OBJ WITH FOLLOWING IDS WILL BE DELETED", ids)
        cur.execute(f'''DELETE FROM emails WHERE {where}''')
        con.commit()
        con.close()

    @staticmethod
    def read_or_unread(where: str, read: bool) -> None:
        con = sqlite3.connect('email.db')
        cur = con.cursor()
        cur.execute(f'''UPDATE emails SET read = {read} WHERE {where}''')
        con.commit()
        cur.execute(f'''SELECT * FROM emails WHERE {where}''')
        print(cur.fetchall())
        con.close()
