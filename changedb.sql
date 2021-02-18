--CREATE TABLE IF NOT EXISTS cost_work(
--    id INTEGER PRIMARY KEY AUTOINCREMENT,
--    cost_1_cam TEXT,
--    cost_1_m TEXT,
--    cnt_m TEXT,
--    cost_mounting TEXT,
--    start_up_cost TEXT,
--    id_tg INTEGER
--);
--
--CREATE TABLE IF NOT EXISTS reviews(
--    id integer PRIMARY KEY AUTOINCREMENT,
--    review TEXT NOT NULL
--);
--
--ALTER TABLE users ADD COLUMN kp_tpl VARCHAR(255);
CREATE TABLE IF NOT EXISTS choice_cams(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_tg INTEGER,
    view_cam TEXT,
    purpose TEXT,
    model TEXT
);

INSERT INTO choice_cams (id_tg, view_cam, purpose, model) VALUES (381428187, 'Купольная', 'Уличная', 'DS-303');