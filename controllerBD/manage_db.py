import sqlite3 as lite


class DatabaseManager():
    """Класс для работы с базой данных."""

    def __init__(self, path):
        self.conn = lite.connect(path)
        self.conn.execute('pragma foreign_keys = on')
        self.conn.commit()
        self.cur = self.conn.cursor()

    def create_tables(self):
        """Метод создаёт базу данных при первом запуске."""
        queries = [
            "CREATE TABLE IF NOT EXISTS genders"
            "(id INTEGER PRIMARY KEY, gender_name TEXT)",
            "INSERT INTO genders VALUES (0, 'Не указано')",
            "INSERT INTO genders VALUES (1, 'Женский')",
            "INSERT INTO genders VALUES (2, 'Мужской')",
            "CREATE TABLE IF NOT EXISTS user_info"
            "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "teleg_id INTEGER NOT NULL UNIQUE,"
            "name TEXT NOT NULL CHECK(length(name)<=100),"
            "birthday TEXT NOT NULL,"
            "about TEXT CHECK(length(name)<=500),"
            "gender INTEGER,"
            "FOREIGN KEY (gender) REFERENCES genders(id))",
            "CREATE TABLE IF NOT EXISTS user_status"
            "(id INTEGER PRIMARY KEY,"
            "status INTEGER NOT NULL,"
            "FOREIGN KEY (id) REFERENCES user_info(id))",
            "CREATE TABLE IF NOT EXISTS met_info"
            "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "first_user_id INTEGER NOT NULL,"
            "second_user_id INTEGER NOT NULL,"
            "date TEXT NOT NULL,"
            "FOREIGN KEY (first_user_id) REFERENCES user_info(id)"
            "FOREIGN KEY (second_user_id) REFERENCES user_info(id))",
            "CREATE TABLE IF NOT EXISTS user_mets"
            "(id INTEGER PRIMARY KEY,"
            "met_info TEXT NOT NULL,"
            "FOREIGN KEY (id) REFERENCES user_info(id))"
        ]
        for query in queries:
            try:
                self.query(query=query)
                self.conn.commit()
            except Exception:
                continue

    def query(self, query, values=None):
        """Выполнение запроса к базе."""
        if values is None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, values)
        self.conn.commit()

    def fetchone(self, query, values=None):
        """Выполнить запрос и получить одну строку."""
        if values is None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, values)
        return self.cur.fetchone()

    def fetchall(self, query, values=None):
        """Выполнить запрос и получить все строки."""
        if values is None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, values)
        return self.cur.fetchall()

    def __del__(self):
        self.conn.close()


if __name__ == '__main__':
    path = '../data/coffee_database.db'
    db_controller = DatabaseManager(path)
    db_controller.create_tables()
