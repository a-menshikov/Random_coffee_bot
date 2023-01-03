import sqlite3

def add_new_user_in_status_table(teleg_id):
    """Добавляем нового пользователя в базу."""
    conn = sqlite3.connect('../data/coffee_database.db')
    cur = conn.cursor()
    id_obj = cur.execute(
        """SELECT id FROM user_info WHERE teleg_id=?""", (teleg_id,)
    )
    cur.execute("""insert into user_status(id, status) values (
    ?,?)""", (
        id_obj.fetchone()[0], 1
    ))
    conn.commit()

add_new_user_in_status_table(1)