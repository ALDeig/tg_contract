CREATE TABLE IF NOT EXISTS cost_work(
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

