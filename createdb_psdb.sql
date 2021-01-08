CREATE TABLE IF NOT EXISTS users(
    id SERIAL,
    name VARCHAR(255),
    city VARCHAR(255),
    phone VARCHAR(20),
    id_tg INT,
    type_executor VARCHAR(100),
    number_kp INT,
    kp_tpl VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS choice_cams(
    id SERIAL,
    id_tg INT,
    view_cam TEXT,
    purpose TEXT,
    model TEXT
);

CREATE TABLE IF NOT EXISTS executor_ooo(
    id SERIAL,
    name_org TEXT,
    initials TEXT,
    position_in_org TEXT,
    ogrn TEXT,
    kpp INT,
    address TEXT,
    name_bank TEXT,
    number_account TEXT,
    inn TEXT,
    form TEXT,
    bik INT,
    check_acc TEXT,
    warranty TEXT,
    number_contract TEXT,
    user_id_tg INT
);

CREATE TABLE IF NOT EXISTS executor_ip(
    id SERIAL,
    name_ip TEXT,
    inn TEXT,
    ogrn TEXT,
    type_ip TEXT,
    code_region TEXT,
    address TEXT,
    form TEXT,
    bik INT,
    name_bank TEXT,
    cor_account TEXT,
    check_acc TEXT,
    warranty TEXT,
    number_contract TEXT,
    user_id_tg INT
);

CREATE TABLE IF NOT EXISTS cost_work(
    id SERIAL,
    cost_1_cam TEXT,
    cost_1_m TEXT,
    cnt_m TEXT,
    cost_mounting TEXT,
    start_up_cost TEXT,
    id_tg INT
);

CREATE TABLE IF NOT EXISTS reviews(
    id SERIAL,
    review TEXT
);

CREATE TABLE IF NOT EXISTS data_cameras(
    id SERIAL,
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
    image TEXT
);
