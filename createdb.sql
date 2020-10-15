CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    city VARCHAR(255),
    phone INTEGER,
    id_tg INTEGER,
    type_executor VARCHAR(100)
);

CREATE TABLE executor_ooo(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_org TEXT,
    initials TEXT,
    position_in_org TEXT,
    ogrn INTEGER,
    kpp INTEGER,
    address TEXT,
    name_bank TEXT,
    number_account TEXT,
    inn INTEGER,
    form TEXT,
    bik INTEGER,
    check_acc TEXT,
    warranty TEXT,
    number_contract TEXT,
    user_id_tg INTEGER
);

CREATE TABLE executor_ip(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_ip TEXT,
    inn INTEGER,
    ogrn INTEGER,
    type_ip TEXT,
    code_region TEXT,
    address TEXT,
    form TEXT,
    bik INTEGER,
    name_bank TEXT,
    cor_account TEXT,
    check_acc TEXT,
    warranty TEXT,
    number_contract TEXT,
    user_id_tg INTEGER
);

CREATE TABLE cost_work(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cost_1_cam TEXT,
    cost_1_m TEXT,
    cnt_m TEXT,
    cost_mounting TEXT,
    start_up_cost TEXT,
    id_tg INTEGER
);
