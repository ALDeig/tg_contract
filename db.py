import os

from num2words import num2words
from loguru import logger
from psycopg2.extras import DictCursor, NamedTupleCursor
import psycopg2

import config

conn = psycopg2.connect(
    database=config.DATABASE,
    user=config.USER_DB,
    password=config.PASSWORD,
    host=config.HOST,
    port=config.PORT
)

cursor = conn.cursor()
logger.info('Database opened succsefully...')

# def step_1():
#     with conn:
#         with conn.cursor(cursor_factory=NamedTupleCursor) as curs: # cursor_factory=DictCursor
#             curs.execute('SELECT * FROM users WHERE name = %s', ('dfdf',))
#             result = curs.fetchone()
#     return result
#
#
# def step_2():
#     cur = conn.cursor()
#     try:
#         cur.execute('SELECT name FROM user')
#     except Exception as e:
#         print('adsf')
#     finally:
#         cur.close()
#         return
#     result = cur.fetchone()
#     return result
# try:
#     result = step_1()
#     if not result:
#         print('Not')
#     print(result)
#     # for item in result:
#     #     print(item)
#         # print(f'Name - {item.name}, city - {item.city}, phone - {item.phone}')
# except Exception as e:
#     logger.debug(e)
# print(step_2())


def get_recorder_channels(number_channels=None):
    with conn:
        with conn.cursor() as cur:
            if not number_channels:
                cur.execute('SELECT DISTINCT number_channels FROM DataRecorder ORDER BY number_channels')
            else:
                cur.execute('SELECT DISTINCT number_channels FROM DataRecorder '
                            'WHERE number_channels >= %s '
                            'ORDER BY number_channels', (number_channels,))
            res = cur.fetchall()
    if len(res) == 0:
        return False

    return [item[0] for item in res]


def get_recorder_channels_with_brand(brand, number_channels=None):
    with conn:
        with conn.cursor() as cur:
            if not number_channels:
                cur.execute('SELECT DISTINCT number_channels FROM DataRecorder WHERE brand = %s ORDER BY number_channels',
                            (brand,))
            else:
                cur.execute('SELECT DISTINCT number_channels FROM DataRecorder '
                            'WHERE number_channels >= %s AND brand = %s'
                            'ORDER BY number_channels', (number_channels, brand))
            res = cur.fetchall()
    if len(res) == 0:
        return False

    return [item[0] for item in res]


def get_options(table, column, filters=None, operator=None) -> list or bool:
    with conn:
        with conn.cursor() as cur:
            if not filters:
                cur.execute(f'SELECT DISTINCT {column} FROM {table} ORDER BY {column}')
            else:
                cols = []
                for key in filters.keys():
                    cols.append(f'{key} {operator} %s')
                value = ' AND '.join(cols)
                # print(table)
                request = f'SELECT DISTINCT {column} FROM {table} WHERE {value} ORDER BY {column}'
                cur.execute(request, tuple(filters.values()))
            res = cur.fetchall()
    return [item[0] for item in res] if len(res) != 0 else False


# print(get_options('DataSwitch', 'number_ports', {'number_ports': 6}, '<'))

# print(get_recorder_channels(10, 2))


def get_hdd_memory_size(memory_size=6, brand=None):
    with conn:
        with conn.cursor() as cur:
            if brand:
                cur.execute('''SELECT DISTINCT memory_size FROM DataHDD 
                WHERE brand = %s AND memory_size <= %s 
                ORDER BY memory_size''', (brand, memory_size))
            else:
                cur.execute('SELECT DISTINCT memory_size FROM DataHDD '
                            'WHERE memory_size <= %s '
                            'ORDER BY memory_size', (memory_size,))
            hdd = cur.fetchall()
    return [item[0] for item in hdd]


# print(get_hdd_memory_size())

# import sqlite3


# conn = sqlite3.connect(os.path.join("db", "users.db"))
# cursor = conn.cursor()


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
    with conn:
        with conn.cursor as curs:
            curs.execute('SELECT id_tg FROM users')
            users = curs.fetchall()

    return users


def get_info(columns: str, table: str, id_tg: int, column: str):
    cursor.execute(f'SELECT {columns} FROM {table} WHERE {column} = %s', (id_tg,))
    info = cursor.fetchone()

    return info


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
    values = tuple(data.values())
    placeholders = ", ".join(["%s"] * len(data.keys()))
    cursor.execute(
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


def delete_cost_work(table: str, id_tg: int):
    cursor.execute(f'DELETE FROM {table} WHERE id_tg = {id_tg}')
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


def insert_cost(table: str, data: dict, id_tg: int):
    data.update({'id_tg': id_tg})
    columns = ', '.join(['cost_1_cam', 'cost_1_m', 'cnt_m', 'cost_mounting', 'start_up_cost', 'id_tg'])
    values = tuple(data.values())
    placeholders = ", ".join(["%s"] * len(data.keys()))
    with conn:
        with conn.cursor() as curs:
            curs.execute(
                f'INSERT INTO {table} '
                f'({columns}) '
                f'VALUES ({placeholders})', values)
        conn.commit()


def insert_kp_tpl(name_tpl: str, id_tg: int):
    cursor.execute(f"UPDATE users SET kp_tpl = '{name_tpl}' WHERE id_tg={id_tg}")
    conn.commit()


def insert_data_of_equipments(data, column=None, table=None):
    if not column:
        columns = ('model', 'description', 'specifications', 'price', 'image', 'view_cam', 'purpose', 'ppi', 'brand')
        columns = ', '.join(columns)
    else:
        columns = ', '.join(column)
    with conn:
        with conn.cursor() as cur:
            cur.execute(f'TRUNCATE {table}')
            conn.commit()
            for camera in data:
                placeholders = ', '.join(['%s'] * len(camera))
                cur.execute(f'INSERT INTO {table} ({columns}) VALUES ({placeholders})', camera)
            conn.commit()


# Функции аналогового КП
def get_model_analog_camera_of_user(filters):
    """Получает модель камеры выбранную пользвателем по параметрам"""
    cols = [f'{key} {op[0]} %s' for key, op in filters.items()]
    value = ' AND '.join(cols)
    request = f'SELECT model FROM choice_cams WHERE {value}'
    with conn:
        with conn.cursor() as curs:
            curs.execute(request, [value[1] for value in filters.values()])
            model = curs.fetchone()
    if model:
        return model
    return model


def get_data_cam(filters: dict):
    """Возвращает данные по камере по фильтру."""
    columns = 'model, description, specifications, price, ppi, image, box, brand'
    cols = [f'{key} {op[0]} %s' for key, op in filters.items()]
    value = ' AND '.join(cols)
    request = f'SELECT {columns} FROM data_cameras WHERE {value}'
    cursor.execute(request, [value[1] for value in filters.values()])
    data = cursor.fetchall()

    return data


def get_data(columns: str, table: str, filters: dict):
    """Принимает колонки строкой, таблицу и фильтры. Фильры в виде словаря в котором ключ - имя стобца, а значение -
    кортеж или список. Первый элемент оператор фильтра, а второй значение.
    Функция возвращает полученные данные в виде списка именованных кортежей"""
    cols = [f'{key} {value[0]} %s' for key, value in filters.items()]
    value = ' AND '.join(cols)
    request = f'SELECT {columns} FROM {table} WHERE {value}'
    with conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute(request, [value[1] for value in filters.values()])
            data = curs.fetchall()
    return data


def get_types(column: str, table: str, filters: dict = None):
    """Ищет все варианты по одному столбцу по фильтру или без него"""
    with conn:
        with conn.cursor() as curs:
            if not filters:
                request = f'SELECT DISTINCT {column} FROM {table}'
                curs.execute(request)
            else:
                cols = [f'{key} {value[0]} %s' for key, value in filters.items()]
                value = ' AND '.join(cols)
                request = f'SELECT DISTINCT {column} FROM {table} WHERE {value}'
                curs.execute(request, [value[1] for value in filters.values()])
            cams = curs.fetchall()
    types = [item[0] for item in cams]
    types.sort()
    return types
# Конец функций аналогового КП

def get_equipments_types(column: str, table: str, filters: dict = None) -> set:
    """Получает данные по колонке из базы данных с фильтрами. Применяется для создания кнопок во время подбора"""
    if not filters:
        request = f'SELECT {column} FROM {table}'
        cursor.execute(request)
    else:
        cols = []
        for key in filters.keys():
            cols.append(f'{key}=%s')
        value = ' AND '.join(cols)
        request = f'SELECT {column} FROM {table} WHERE {value}'
        cursor.execute(request, list(filters.values()))

    cams = cursor.fetchall()

    return set(i[0] for i in cams)


def select_choice_equipment(value: str, data: dict, table: str):
    """Возвращает подобронное пользователем оборудование. Если не выбрано возвращает None"""
    filters = ' AND '.join([i + ' = %s' for i in data.keys()])
    # text = f'SELECT {value} FROM {table} WHERE {filters} AND id_tg = %s'
    text = f'SELECT {value} FROM {table} WHERE {filters}'
    cursor.execute(text, tuple(data.values()))
    result = cursor.fetchone()
    return result


def insert_choice_equipment(table: str, columns: str, values: dict, filter_for_del: dict):
    """Вносит в базу данных выбранное пользователем оборудование"""
    placeholders = ', '.join(['%s'] * len(values))
    filters = ' AND '.join([i + ' = %s' for i in values.keys()])
    filters_for_del = ' AND '.join([i + ' = %s' for i in filter_for_del.keys()])
    cursor.execute(f'DELETE FROM {table} WHERE {filters_for_del}', tuple(filter_for_del.values()))
    cursor.execute(f'INSERT INTO {table} ({columns}) VALUES ({placeholders})', tuple(values.values()))
    conn.commit()


def insert_choice_camera(type_cam, view_cam, purpose, model, id_tg):
    if type_cam == 'IP':
        operator = '='
    else:
        operator = '!='
    cursor.execute(f'SELECT model FROM choice_cams '
                   f'WHERE id_tg = %s AND type_cam {operator} %s AND view_cam = %s '
                   f'AND purpose = %s', (id_tg, 'IP', view_cam, purpose))
    old_choice = cursor.fetchone()
    if not old_choice:
        cursor.execute(f'INSERT INTO choice_cams (id_tg, type_cam, view_cam, purpose, model) VALUES (%s, %s, %s, %s, %s)',
                       (id_tg, type_cam, view_cam, purpose, model))
    else:
        cursor.execute(f'UPDATE choice_cams SET model = %s, type_cam = %s WHERE id_tg = %s AND type_cam {operator} %s'
                       f'AND view_cam = %s AND purpose = %s', (model, type_cam, id_tg, 'IP', view_cam, purpose))
    conn.commit()


def get_data_equipments(table: str, columns: str, data: dict):
    filters = ' AND '.join([i + ' = %s' for i in data.keys()])
    text = f'SELECT {columns} FROM {table} WHERE {filters}'
    cursor.execute(text, tuple(data.values()))
    results = cursor.fetchall()
    if len(results) == 0:
        return False

    return results


def get_equipment_data_by_model(table: str, columns: str, model: str):
    cursor.execute(f'SELECT {columns} FROM {table} WHERE model = %s', (model,))
    result = cursor.fetchone()

    return result


def get_data_of_cameras(type_cam, view_cam, purpose, ppi, brand):
    columns = ('id', 'model', 'description', 'specifications', 'price', 'image')
    columns = ', '.join(columns)
    if not purpose:
        cursor.execute(f'SELECT {columns} FROM data_cameras WHERE type_cam = %s AND view_cam = %s '
                       f'AND ppi = %s AND brand = %s', (type_cam, view_cam, ppi, brand))
    else:
        cursor.execute(
            f'''SELECT {columns}
            FROM data_cameras
            WHERE type_cam = %s 
            AND view_cam=%s
            AND purpose=%s
            AND ppi=%s
            AND brand=%s''', (type_cam, view_cam, purpose, ppi, brand))
    cameras = cursor.fetchall()
    if len(cameras) == 0:
        return False
    return cameras


def get_price_of_camera(model=None, type_cam=None, view_cam=None, purpose=None, ppi=None):
    """Получает из базы данные по камере необходимые для КП"""
    columns = ('model', 'description', 'specifications', 'price', 'ppi', 'image', 'box', 'brand')
    columns = ', '.join(columns)
    if model:
        cursor.execute(f'SELECT {columns} FROM data_cameras WHERE model = %s', (model,))
    else:
        cursor.execute(
            f'SELECT {columns} FROM data_cameras WHERE type_cam = %s AND view_cam = %s AND purpose = %s AND ppi = %s',
            (type_cam, view_cam, purpose, ppi))
    result = cursor.fetchone()
    if not result:
        return False
    return result


def get_model_camera_of_user(view_cam, purpose, id_tg):
    """Получает модель камеры выбранную пользвателем по параметрам"""
    cursor.execute(f'SELECT model FROM choice_cams WHERE view_cam = %s AND purpose = %s AND id_tg = %s',
                   (view_cam, purpose, id_tg))
    model = cursor.fetchone()
    # if not model:
    #     return False
    # print(f'get_model_camera_of_user - {model}')
    return model


def get_kp_tpl(id_tg: int):
    cursor.execute(f'SELECT kp_tpl FROM users WHERE id_tg = %s', (id_tg,))
    kp_tpl = cursor.fetchone()

    return kp_tpl[0]


def get_data_cost(id_tg, table):
    columns = ', '.join(['cost_1_cam', 'cost_1_m', 'cnt_m', 'cost_mounting', 'start_up_cost'])
    cursor.execute(f'SELECT {columns} FROM {table} WHERE id_tg= %s', (id_tg,))
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
    cursor.execute(f'INSERT INTO reviews (review) VALUES (%s)', (text,))
    conn.commit()


def del_review(num_id):
    cursor.execute(f'DELETE FROM reviews WHERE id = %s', (num_id,))
    conn.commit()


def get_cursor():
    return cursor


# def _init_db():
#     """Инициализирует БД"""
#     with open("createdb.sql", "r") as f:
#         sql = f.read()
#     cursor.executescript(sql)
#     conn.commit()


# def check_db_exists():
#     """Проверяет, инициализирована ли БД, если нет — инициализирует"""
#     cursor.execute("SELECT name FROM sqlite_master "
#                    "WHERE type='table' AND name='users'")
#     table_exists = cursor.fetchall()
#     if table_exists:
#         return
#     _init_db()


def _apply_script():
    """Вспомогательная функция для добавления изменений в базу данных. Вызывается из терминала"""
    with open('createdb_psdb.sql', 'r', encoding='UTF-8') as file:
        cursor.execute(file.read())
    conn.commit()
    conn.close()

# check_db_exists()
