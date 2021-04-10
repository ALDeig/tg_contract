CREATE TABLE IF NOT EXISTS users(
    id SERIAL,
    name VARCHAR(255),
    city VARCHAR(255),
    phone VARCHAR(20),
    id_tg INT,
    type_executor VARCHAR(100),
    number_kp INT,
    kp_tpl VARCHAR(255),
    number_order INT,
    is_provider BOOL
);

CREATE TABLE IF NOT EXISTS choice_cams(
    id SERIAL,
    id_tg INT,
    type_cam TEXT,
    view_cam TEXT,
    purpose TEXT,
    model TEXT
);

CREATE TABLE IF NOT EXISTS data_cameras(
    id SERIAL,
    country VARCHAR(255),
    currency TEXT,
    provider VARCHAR(255),
    brand VARCHAR(255),
    type_cam VARCHAR(255),
    model VARCHAR(255),
    price VARCHAR(255),
    trade_price TEXT,
    view_cam VARCHAR(255),
    purpose VARCHAR(255),
    ppi VARCHAR(255),
    specifications TEXT,
    description TEXT,
    image TEXT,
    box TEXT
);

CREATE TABLE IF NOT EXISTS ChoiceRecorder(
    id SERIAL,
    id_tg INT,
    type_recorder VARCHAR(255),
    number_channels INT,
    number_hdd INT,
    number_poe INT,
    model VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS DataRecorder(
    id SERIAL,
    country VARCHAR(255),
    currency TEXT,
    provider VARCHAR(255),
    brand VARCHAR(255),
    type_recorder VARCHAR(255),
    model VARCHAR(255),
    price VARCHAR(255),
    trade_price TEXT,
    ppi TEXT,
    number_channels INT,
    number_hdd INT,
    max_size_hdd INT,
    number_poe INT,
    specifications TEXT,
    description TEXT,
    image TEXT,
    box INT
);

CREATE TABLE IF NOT EXISTS ChoiceSwitch(
    id SERIAL,
    id_tg INT,
    ports_poe INT,
    model VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS DataSwitch(
    id SERIAL,
    country VARCHAR(255),
    currency TEXT,
    provider VARCHAR(255),
    brand VARCHAR(255),
    number_ports INT,
    model VARCHAR(255),
    price TEXT,
    trade_price TEXT,
    ports_poe INT,
    power VARCHAR(255),
    specifications TEXT,
    description TEXT,
    image TEXT
);

CREATE TABLE IF NOT EXISTS ChoiceHDD(
    id SERIAL,
    id_tg INT,
    brand VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS DataHDD(
    id SERIAL,
    country VARCHAR(255),
    currency VARCHAR(255),
    provider VARCHAR(255),
    brand VARCHAR(255),
    memory_size REAL,
    model VARCHAR(255),
    price VARCHAR(255),
    trade_price VARCHAR(255),
    serial VARCHAR(255),
    type_hdd VARCHAR(255),
    interface VARCHAR(255),
    description TEXT,
    image TEXT
);

CREATE TABLE IF NOT EXISTS ChoiceBox(
    id SERIAL,
    id_tg INT,
    number_units INT,
    type_box INT,
    model VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS DataBox(
    id SERIAL,
    country VARCHAR(255),
    currency VARCHAR(255),
    provider VARCHAR(255),
    brand VARCHAR(255),
    type_box INT,
    number_units INT,
    model VARCHAR(255),
    price VARCHAR(255),
    trade_price VARCHAR(255),
    mounting_type VARCHAR(255),
    dimensions VARCHAR(255),
    specifications TEXT,
    description TEXT,
    image TEXT
);

CREATE TABLE IF NOT EXISTS ChoiceCable(
    id SERIAL,
    id_tg INT,
    type_system TEXT,
    use TEXT,
    brand TEXT
);

CREATE TABLE IF NOT EXISTS DataCable(
    id SERIAL,
    country VARCHAR(255),
    currency VARCHAR(255),
    provider VARCHAR(255),
    type_cable VARCHAR(255),
    type_system VARCHAR(255),
    brand VARCHAR(255),
    model TEXT,
    price TEXT,
    trade_price TEXT,
    use TEXT,
    specifications TEXT,
    description TEXT,
    image TEXT
);

CREATE TABLE IF NOT EXISTS ChoiceIBP(
    id SERIAL,
    id_tg INT,
    type_ibp VARCHAR(255),
    brand TEXT
);

CREATE TABLE IF NOT EXISTS DataIBP(
    id SERIAL,
    country VARCHAR(255),
    currency VARCHAR(255),
    provider VARCHAR(255),
    brand VARCHAR(255),
    model TEXT,
    power INT,
    price TEXT,
    trade_price TEXT,
    mounting_type TEXT,
    type_ibp VARCHAR(255),
    profile TEXT,
    specifications TEXT,
    description TEXT,
    image TEXT
);

CREATE TABLE IF NOT EXISTS ChoiceGofra(
    id SERIAL,
    id_tg INT,
    brand TEXT
);

CREATE TABLE IF NOT EXISTS DataBracing(
    id SERIAL,
    country VARCHAR(255),
    currency VARCHAR(255),
    provider VARCHAR(255),
    brand VARCHAR(255),
    model TEXT,
    price TEXT,
    trade_price TEXT,
    mount_type TEXT,
    specifications TEXT,
    description TEXT,
    image TEXT
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

CREATE TABLE IF NOT EXISTS cost_work_analog(
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
