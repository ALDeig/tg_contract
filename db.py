import json
import os

import sqlite3

from num2words import num2words

conn = sqlite3.connect(os.path.join("db", "users.db"))
cursor = conn.cursor()


def choice_of_ending(number: str) -> str:
    endings = {'1': 'месяц', '2': 'месяца', '3': 'месяца', '4': 'месяца', '5': 'месяцев', '6': 'месяцев',
               '7': 'месяцев', '8': 'месяцев',
               '9': 'месяцев', '0': 'месяцев'}
    endings_2 = {'11': 'месяцев', '12': 'месяцев', '13': 'месяцев'}
    try:
        ending = endings_2[number[-2:]]
    except KeyError:
        ending = endings[number[-1]]

    return ending


def get_type_executor(id_tg: int):
    cursor.execute(f'SELECT type_executor FROM users WHERE id_tg={id_tg}')
    type_executor = cursor.fetchone()

    return type_executor[0]


def get_users():
    cursor.execute('SELECT id_tg FROM users')
    users = cursor.fetchall()

    return users


def get_number_kp(id_tg):
    cursor.execute(f'SELECT number_kp FROM users WHERE id_tg={id_tg}')
    number_kp = cursor.fetchone()

    return number_kp[0]


def write_number_kp(id_tg, number_kp: int):
    cursor.execute(f"UPDATE users SET number_kp = '{number_kp}' WHERE id_tg = {id_tg}")
    conn.commit()


def transform_warranty(warranty: str) -> str:
    ending = choice_of_ending(warranty)
    warranty = f"{warranty} ({num2words(int(warranty), lang='ru')}) {ending}"

    return warranty


def get_count_users():
    cursor.execute('SELECT COUNT(*) FROM users')
    count_users = cursor.fetchone()

    return count_users[0]


def get_count_executors():
    cursor.execute('SELECT COUNT(*) FROM executor_ooo')
    count_executors_ooo = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM executor_ip')
    count_executors_ip = cursor.fetchone()[0]
    count_executor = count_executors_ooo + count_executors_ip

    return count_executor


def create_data_to_db(data: dict):
    api_inn = data.pop('api_inn')[0]
    api_bik = data.pop('api_bik')
    api_inn.update(api_bik)
    api_inn.update(data)
    return api_inn


def insert(table: str, columns: list, data: dict):
    columns = ', '.join(columns)
    values = [tuple(data.values())]
    placeholders = ", ".join("?" * len(data.keys()))
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def update_type_executor(type_executor: str, id_tg: int):
    cursor.execute(f"UPDATE users SET type_executor = '{type_executor}' WHERE id_tg = {id_tg}")
    conn.commit()


def get_table_executor_for_type_executor(id_tg):
    cursor.execute(f"SELECT type_executor FROM users WHERE id_tg={id_tg}")
    type_executor = cursor.fetchone()[0]
    if type_executor == 'ЮЛ':
        table = 'executor_ooo'
    else:
        table = 'executor_ip'
    return table


def update_number_account(id_tg: int):
    table = get_table_executor_for_type_executor(id_tg)
    cursor.execute(f"SELECT number_contract FROM {table} WHERE user_id_tg={id_tg}")
    number = cursor.fetchone()[0]
    cnt = len(number)
    tmp = ''
    for word in number[::-1]:
        if word.isdigit():
            tmp = f'{word}{tmp}'
            cnt -= 1
        else:
            break
    start_number = str()
    for num in tmp:
        if num == '0':
            start_number += '0'
        else:
            break
    tmp = str(int(tmp) + 1)
    number = number[:cnt] + start_number + tmp
    cursor.execute(f"UPDATE {table} SET number_contract = '{number}' WHERE user_id_tg = {id_tg}")
    conn.commit()


def fetchall_ooo(id_tg: int):
    columns = [
        'executor_ooo.name_org',
        'executor_ooo.initials',
        'executor_ooo.position_in_org',
        'executor_ooo.ogrn',
        'executor_ooo.address',
        'executor_ooo.name_bank',
        'executor_ooo.number_account',
        'executor_ooo.inn',
        'executor_ooo.kpp',
        'executor_ooo.form',
        'executor_ooo.bik',
        'executor_ooo.check_acc',
        'executor_ooo.warranty',
        'executor_ooo.number_contract',
        'executor_ooo.user_id_tg']
    columns = ', '.join(columns)
    cursor.execute(f"SELECT users.city, {columns} FROM users JOIN executor_ooo ON users.id_tg=executor_ooo.user_id_tg "
                   f"WHERE users.id_tg={id_tg}")
    rows = cursor.fetchone()

    return rows


def fetchall_ip(id_tg: int):
    columns = [
        'executor_ip.name_ip',
        'executor_ip.inn',
        'executor_ip.ogrn',
        'executor_ip.type_ip',
        'executor_ip.code_region',
        'executor_ip.address',
        'executor_ip.form',
        'executor_ip.bik',
        'executor_ip.name_bank',
        'executor_ip.cor_account',
        'executor_ip.check_acc',
        'executor_ip.warranty',
        'executor_ip.number_contract',
        'executor_ip.user_id_tg'
    ]
    columns = ', '.join(columns)
    cursor.execute(f"SELECT users.city, {columns} FROM users JOIN executor_ip ON users.id_tg=executor_ip.user_id_tg "
                   f"WHERE users.id_tg={id_tg}")

    rows = cursor.fetchone()
    return rows


def get_data_from_db_ooo(id_tg: int) -> dict:
    tmp_data = fetchall_ooo(id_tg)
    warranty = transform_warranty(tmp_data[13])
    result = {
        'number': tmp_data[14],
        'city_ex': tmp_data[0],
        'ogrn_ex': tmp_data[4],
        'kpp_ex': tmp_data[9],
        'warranty': warranty,
        'address_ex': tmp_data[5],
        'bik_ex': tmp_data[11],
        'inn_ex': tmp_data[8],
        'name_bank_ex': tmp_data[6],
        'cor_account_ex': tmp_data[7],
        'check_account_ex': tmp_data[12],
        'director_ex': tmp_data[2],
        'taxation': tmp_data[10],
        'name_ip': tmp_data[1],
    }

    return result


def get_data_from_db_ip(id_tg: int) -> dict:
    tmp_data = fetchall_ip(id_tg)
    # return
    warranty = transform_warranty(tmp_data[12])
    result = {
        'number': tmp_data[13],
        'city_ex': tmp_data[0],
        'ogrn_ex': tmp_data[3],
        'warranty': warranty,
        'address_ex': tmp_data[6],
        'bik_ex': tmp_data[8],
        'inn_ex': tmp_data[2],
        'cor_account_ex': tmp_data[10],
        'name_bank_ex': tmp_data[9],
        'check_account_ex': tmp_data[11],
        'director_ex': tmp_data[1],
        'taxation': tmp_data[7],
        'name_ip': tmp_data[1]
    }

    return result


def check_user_in(id_tg: int, column: str, table: str) -> bool:
    cursor.execute(f"SELECT {column} FROM {table}")
    data_from_db = cursor.fetchall()
    users = []

    for user in data_from_db:
        users.append(int(user[0]))

    if int(id_tg) in users:
        return True

    else:
        return False


def check_executor_in(id_tg: int):
    if not check_user_in(id_tg, 'user_id_tg', 'executor_ip') and not check_user_in(id_tg, 'user_id_tg', 'executor_ooo'):
        return False
    else:
        return True


def delete(id_tg: int):
    cursor.execute(f"DELETE FROM executor_ooo WHERE user_id_tg={id_tg}")
    cursor.execute(f"DELETE FROM executor_ip WHERE user_id_tg={id_tg}")
    conn.commit()


def delete_user(id_tg: int):
    cursor.execute(f"DELETE FROM users WHERE id_tg={id_tg}")
    conn.commit()


def delete_cost_work(id_tg: int):
    cursor.execute(f'DELETE FROM cost_work WHERE id_tg = {id_tg}')
    conn.commit()


def get_number_contract(id_tg):
    cursor.execute(f"SELECT type_executor FROM users WHERE id_tg={id_tg}")
    type_executor = cursor.fetchone()[0]
    if type_executor == 'ЮЛ':
        cursor.execute(f"SELECT number_contract FROM executor_ooo WHERE user_id_tg={id_tg}")
        number = cursor.fetchone()[0]
    else:
        cursor.execute(f"SELECT number_contract FROM executor_ip WHERE user_id_tg={id_tg}")
        number = cursor.fetchone()[0]

    return number


def insert_cost(data: dict, id_tg: int):
    data.update({'id_tg': id_tg})
    columns = ', '.join(['cost_1_cam', 'cost_1_m', 'cnt_m', 'cost_mounting', 'start_up_cost', 'id_tg'])
    values = [tuple(data.values())]
    placeholders = ", ".join("?" * len(data.keys()))
    cursor.executemany(
        f'INSERT INTO cost_work '
        f'({columns}) '
        f'VALUES ({placeholders})', values)
    conn.commit()


def insert_kp_tpl(name_tpl: str, id_tg: int):
    cursor.execute(f"UPDATE users SET kp_tpl = '{name_tpl}' WHERE id_tg={id_tg}")
    conn.commit()


def insert_data_of_cameras(data):
    columns = ('model', 'description', 'specifications', 'price', 'image', 'view_cam', 'purpose', 'ppi', 'brand')
    columns = ', '.join(columns)
    for camera in data:
        placeholders = ', '.join('?' * len(camera))
        cursor.execute(f'INSERT INTO data_cameras ({columns}) VALUES ({placeholders})', camera)

    conn.commit()


def insert_choice_camera(column, model, id_tg):
    cursor.execute(f'UPDATE users SET {column} = ? WHERE id_tg = ?', (model, id_tg))
    conn.commit()


def get_data_of_cameras(view_cam, purpose, ppi, brand):
    columns = ('id', 'model', 'description', 'specifications', 'price', 'image')
    columns = ', '.join(columns)
    cursor.execute(
        f'''SELECT {columns}
        FROM data_cameras
        WHERE view_cam=?
        AND purpose=?
        AND ppi=?
        AND brand=?''', (view_cam, purpose, ppi, brand))
    cameras = cursor.fetchall()
    if len(cameras) == 0:
        return False
    return cameras


def get_price_of_camera(model):
    columns = ('model', 'description', 'specifications', 'price')
    columns = ', '.join(columns)
    cursor.execute(f'SELECT {columns} FROM data_cameras WHERE model = ?', (model,))
    result = cursor.fetchone()
    if len(result) == 0:
        return False
    return result


def get_model_camera_of_user(column, id_tg):
    cursor.execute(f'SELECT {column} FROM users WHERE id_tg = ?', (id_tg,))
    model = cursor.fetchone()[0]

    return model


def get_kp_tpl(id_tg: int):
    cursor.execute(f'SELECT kp_tpl FROM users WHERE id_tg = {id_tg}')
    kp_tpl = cursor.fetchone()

    return kp_tpl[0]


def get_data_cost(id_tg):
    columns = ', '.join(['cost_1_cam', 'cost_1_m', 'cnt_m', 'cost_mounting', 'start_up_cost'])
    cursor.execute(f'SELECT {columns} FROM cost_work WHERE id_tg={id_tg}')
    data = cursor.fetchone()

    return data


def get_reviews() -> list:
    """Функция получает отзывы и отдает последние три. Лимит задается кнопокй 'еще' в боте"""
    cursor.execute(f'SELECT review FROM reviews')
    reviews = cursor.fetchall()

    return reviews


def get_reviews_with_id():
    cursor.execute('SELECT id, review FROM reviews')
    reviews = cursor.fetchall()

    return reviews


def insert_reviews(text: str):
    """Запись отзыва в таблицу"""
    cursor.execute(f'INSERT INTO reviews (review) VALUES ("{text}")')
    conn.commit()


def del_review(num_id):
    cursor.execute(f'DELETE FROM reviews WHERE id = {num_id}')
    conn.commit()


def get_cursor():
    return cursor


def _init_db():
    """Инициализирует БД"""
    with open("createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='users'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()


def apply_script():
    """Вспомогательная функция для добавления изменений в базу данных. Вызывается из терминала"""
    with open('changedb.sql', 'r', encoding='UTF-8') as file:
        cursor.executescript(file.read())
    conn.commit()
    conn.close()


check_db_exists()
