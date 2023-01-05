import json
import sqlite3 as lite
from datetime import datetime


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
            "FOREIGN KEY (id) REFERENCES user_info(id))",
            "CREATE TABLE IF NOT EXISTS holidays_status"
            "(id INTEGER PRIMARY KEY,"
            "status INTEGER NOT NULL,"
            "till_date TEXT,"
            "FOREIGN KEY (id) REFERENCES user_info(id))"
        ]
        for query in queries:
            try:
                self.query(query=query)
            except Exception:
                continue

    def query(self, query, values=None):
        """Выполнение запроса к базе кроме select."""
        if values is None:
            self.cur.execute(query)
        else:
            self.cur.execute(query, values)
        self.conn.commit()

    def select_query(self, query, values=None):
        """Выполнение select_запроса к базе."""
        if values is None:
            result = self.cur.execute(query)
        else:
            result = self.cur.execute(query, values)
        self.conn.commit()
        return result

    def update_mets(self, match_info: dict):
        """Записывает в базу информацию о новых встречах."""
        today = datetime.now().strftime('%d.%m.%Y')
        for match in match_info.items():
            if all(match):
                first_user = match[0]
                second_user = match[1]
                query = ('INSERT INTO met_info(first_user_id,'
                         'second_user_id, date) VALUES (?,?,?)')
                self.query(query, (first_user, second_user, today))

    def update_one_user_mets(self, first_user: int, second_user: int):
        """Записывает в user_mets информацию об одном пользователе."""
        today = datetime.now().strftime('%d.%m.%Y')
        all_mets_query = 'SELECT met_info FROM user_mets WHERE id = ?'
        db_result = self.select_query(all_mets_query,
                                               (first_user,)).fetchone()
        if db_result:
            user_mets = json.loads(db_result[0])
            new_met_query = ('SELECT id FROM met_info WHERE date = ? '
                             'and (first_user_id = ? or second_user_id = ?)')
            met_id = self.select_query(new_met_query,
                                                (today,
                                                 first_user,
                                                 first_user)).fetchone()[0]
            user_mets[met_id] = second_user
            new_mets_value = json.dumps(user_mets)
            insert_query = 'UPDATE user_mets SET met_info = ? WHERE id = ?'
            self.query(insert_query, (new_mets_value, first_user))
        else:
            user_mets = {}
            new_met_query = ('SELECT id FROM met_info WHERE date = ? '
                             'and (first_user_id = ? or second_user_id = ?)')
            met_id = self.select_query(new_met_query,
                                                (today,
                                                 first_user,
                                                 first_user)).fetchone()[0]
            user_mets[met_id] = second_user
            new_mets_value = json.dumps(user_mets)
            insert_query = 'INSERT INTO user_mets VALUES (?, ?)'
            self.query(insert_query, (first_user, new_mets_value))

    def update_all_user_mets(self, match_info: dict):
        """Записывает в user_mets всю информацию о новых встречaх."""
        for match in match_info.items():
            if all(match):
                first_user = match[0]
                second_user = match[1]
                self.update_one_user_mets(first_user, second_user)
                first_user = match[1]
                second_user = match[0]
                self.update_one_user_mets(first_user, second_user)

    def __del__(self):
        self.conn.close()
