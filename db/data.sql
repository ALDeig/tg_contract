INSERT INTO hub (name, short_name, devices, rooms, cams, rex, motioncam, price, photo) VALUES
    ('Hub', 'Центр управления системы безопасности', '100', '50', '10', '1', 'false', '9550', 'https://ajax.systems/wp-content/uploads/2018/09/HUB_B-1x.png'),
    ('Hub Plus', 'Центр управления системы безопасности', '150', '50', '50', '5', 'false', '17890', 'https://ajax.systems/wp-content/uploads/2018/09/HUB_B-1x.png'),
    ('Hub 2', 'Центр управления системы безопасности', '100', '50', '25', '5', 'true', '13750', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/product/hub2/hero@1x.jpg'),
    ('Hub 2 plus', 'Центр управления системы безопасности', '201', '50', '100', '5',	'true', '23050', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/product/hub2-plus/hero_hub2plus_xl_l@1x.jpg'),
    ('ReX', 'Ретранслятор системы безопасности', '0', '0', '0', '0', '0', '6690', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/product/rex/hero@1x.jpg');

INSERT INTO invasion (name, short_name, type_sensor, type, price, installation, photo) VALUES
    ('MotionCam', 'Датчик движения', 'm', 'Датчик движения', '8250', 'Внутрений', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/MotionCam_black@1x.png'),
    ('MotionProtect', 'Датчик движения', 'm', 'Датчик движения', '2460', 'Внутрений',' https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/MotionProtect_black@1x.png'),
    ('MotionProtect Plus', 'Датчик движения', 'm', 'Датчик движения', '4470a', 'Внутрений', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/MotionProtect_white@1x.png'),
    ('CombiProtect', 'Датчик движения/разбития', 'm', 'Датчик движения разбития', '4490', 'Внутрений', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/CombiProtect_black@1x.png'),
    ('MotionProtect Curtain', 'Датчик движения', 'm', 'Датчик движения', '4290', 'Внутрений', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/MotionProtectCurtain_black@1x.png'),
    ('DoorProtect', 'Датчик движения', 'o', 'Датчик открытия', '1680', 'Внутрений', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/DoorProtect_black@1x.png'),
    ('DoorProtect Plus', 'Датчик открытия/удара/наклона', 'o', 'Датчик открытия/удара/наклона', '2800', 'Внутрений', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/DoorProtect_white@1x.png'),
    ('GlassProtect', 'Датчик разбития', 'm', 'Датчик разбития', '3350', 'Внутрений', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/GlassProtect_black@1x.png'),
    ('MotionProtect Outdoor', 'Датчик движения', 'm', 'Датчик движения', '8390', 'Уличный', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/MotionProtectOutdoor1_white@1x.png'),
    ('Hood для MotionProtect Outdoor', 'Козырёк', 'm', 'Козырёк', '770', 'Уличный', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/hood_white@1x.png');

INSERT INTO fire (name, short_name, type, price, photo) VALUES
    ('FireProtect', 'Датчик дыма/температуры', 'Датчик дыма/температуры', '3350', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/FireProtect_white@1x.png'),
    ('FireProtect Plus', 'Датчик дыма/температуры/угарного газа', 'Датчик дыма/температуры/угарного газа', '5590', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/FireProtect_black@1x.png');

INSERT INTO leak (name, short_name, type, price, photo) VALUES
    ('LeaksProtect', 'Датчик протечки', 'Датчик протечки', '2800', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/LeaksProtect_black@1x.png');

INSERT INTO control (name, short_name, type, price, photo) VALUES
    ('DoubleButton', 'Кнопка', 'Кнопка', '1890', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/doublebutton_white@1x.png'),
    ('Button', 'Кнопка', 'Кнопка', '1890', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/Button_black@1x.png'),
    ('Holder для Button/DoubleButton', 'Крепление кнопки', 'Крепление', '310', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/holder_black@1x.png'),
    ('SpaceControl', 'Брелок', 'Брелок', '1350', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/SpaceControl_white@1x.png'),
    ('KeyPad', 'Клавиатура', 'Клавиатура', '4250', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/KeyPad_black@1x.png');

INSERT INTO siren (name, short_name, type, price, installation, photo) VALUES
    ('HomeSiren', 'Сирена', 'Сирена', '3350', 'Внутрений', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/HomeSiren_black@1x.png'),
    ('StreetSiren', 'Сирена', 'Сирена', '6990', 'Уличный', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/StreetSiren_black@1x.png'),
    ('StreetSiren DoubleDeck', 'Сирена', 'Сирена', '6990', 'Уличный',	'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/doubledeck_white@1x.png'),
    ('Brandplate', 'Лицевая панель для брендирования уличной сирены', 'Панель', '5000', 'Уличный', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/brandplate_black@1x.png');

INSERT INTO automation (name, short_name, type, price, photo) VALUES
    ('Socket', 'Розетка', 'Розетка', '4000', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/Socket_white@1x.png'),
    ('WallSwitch', 'Силовое реле', 'Силовое реле', '2250', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/WallSwitch@1x.png'),
    ('Relay', 'Слаботочное реле', 'Слаботочное реле', '2250', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/WallSwitch@1x.png');

INSERT INTO integration (name, short_name, type, price, photo) VALUES
    ('uartBridge', 'Модуль-приемник', 'Модуль-приемник', '2250', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/uartBridge@1x.png'),
    ('ocBridge Plus', 'Модуль-приемник', 'Модуль-приемник', '3350', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/ocBridgePlus@1x.png'),
    ('Transmitter', 'Модуль для подключения уличных датчиков движения', 'Модуль для подключения уличных датчиков движения', '2250', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/Transmitter@1x.png'),
    ('MultiTransmitter', 'Модуль для подлкючения проводных сигнализаций', 'Модуль для подлкючения проводных сигнализаций', '9625', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/multitransmitter_black@1x.png');

INSERT INTO bbp (name, short_name, type, price, photo) VALUES
    ('6V PSU для Hub 2/Hub 2 Plus', 'Плата блока питания',	'Плата блока питания', '1550', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/ps_6v@1x.png'),
    ('12V PSU для Hub/Hub Plus/ReX', 'Плата блока питания', 'Плата блока питания', '1550', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/12vpsu-hub@1x.png'),
    ('12V PSU для Hub2', 'Плата блока питания', 'Плата блока питания', '1550', 'https://ajax.systems/wp-content/themes/ajax/assets/images/template/catalog/products/12vpsu-hub2@1x.png');
