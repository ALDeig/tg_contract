from datetime import time, timedelta, datetime
import os
import shutil

import urllib.request
import urllib.error
import pygsheets
from google_drive_downloader import GoogleDriveDownloader as gdd
from loguru import logger

import config

client = pygsheets.authorize(service_file=os.path.join('commercial_proposal', 'gsheets', 'creds.json'))
# client = pygsheets.authorize(service_file=os.path.join('creds.json'))
sh = client.open_by_key(config.SHEETS_ID)


def get_info(table, directory, image_index=12):
    wks = sh.worksheet('index', table)
    data = wks.range('B2:R2500')
    result = list()
    for row in data:
        if row[0].value != '':
            result.append([i.value for i in row if i.value])
    # print(*result, sep='\n')
    # return
    logger.info(f'Start save image - {table}')
    save_images(result, directory, image_index)
    return result


def delete_dirs(directory):
    path = os.path.join('commercial_proposal', 'images', directory)
    # print(path)
    for index, dir_ in enumerate(os.walk(path)):
        if index == 0:
            pass
        else:
            shutil.rmtree(dir_[0])


def save_images(data, directory, image_index):
    path = os.path.join('commercial_proposal', 'images', directory)
    # path = os.path.join('images', directory)
    delete_dirs(directory)
    for camera in data:
        try:
            url = camera[image_index].split('/')
            if url[2] == 'drive.google.com':
                if not os.path.exists(os.path.join(path, camera[3].strip())):
                    os.mkdir(os.path.join(path, camera[3].strip()))
                name = camera[5].strip().replace('/', '').replace('\\', '')
                path_file = os.path.join(path, camera[3].strip(), name + f'.jpg')
                gdd.download_file_from_google_drive(file_id=url[-2], dest_path=path_file)
                continue
            else:
                img = urllib.request.urlopen(camera[image_index]).read()
        except urllib.error.HTTPError as er:
            print('Ошибка при скачивании фото: ', er)
            print(camera[image_index])
            continue
        except Exception as e:
            print('Неизвестная Ошибка при скачивании фото: ', e)
            print(camera[image_index])
            continue
        if not os.path.exists(os.path.join(path, camera[3].strip())):
            os.mkdir(os.path.join(path, camera[3].strip()))
        name = camera[5].strip().replace('/', '').replace('\\', '')
        # type_file = camera[image_index].split('.')[-1]
        with open(os.path.join(path, camera[3].strip(), name + f'.jpg'), 'wb') as file:
            file.write(img)
