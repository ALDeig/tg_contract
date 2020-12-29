CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255),
    city VARCHAR(255),
    phone INTEGER,
    id_tg INTEGER,
    type_executor VARCHAR(100),
    number_kp INTEGER,
    kp_tpl VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS choice_cams(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tg INTEGER,
    view_cam TEXT,
    purpose TEXT,
    model TEXT
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

CREATE TABLE IF NOT EXISTS reviews(
    id integer PRIMARY KEY AUTOINCREMENT,
    review TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS data_cameras(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country VARCHAR(50),
    currency TEXT,
    provider VARCHAR(100),
    brand VARCHAR(100),
    type_cam VARCHAR(20),
    model VARCHAR(50),
    price VARCHAR(50),
    trade_price TEXT,
    view_cam VARCHAR(50),
    purpose VARCHAR(50),
    ppi VARCHAR(50),
    specifications TEXT,
    description TEXT,
    image VARCHAR(50)
);
