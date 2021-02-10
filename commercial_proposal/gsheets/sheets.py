from datetime import time, timedelta, datetime
import os
import shutil

import urllib.request
import urllib.error
import pygsheets
from google_drive_downloader import GoogleDriveDownloader as gdd

import config

# client = pygsheets.authorize(service_file=os.path.join('commercial_proposal', 'gsheets', 'creds.json'))
client = pygsheets.authorize(service_file=os.path.join('creds.json'))
sh = client.open_by_key(config.SHEETS_ID)


def get_info(table, directory, image_index=12):
    wks = sh.worksheet('index', table)
    data = wks.range('B40:Q43')
    result = list()
    for row in data:
        if row[0].value != '':
            result.append([i.value for i in row if i.value])
    # print(*result, sep='\n')
    # return
    print('Start save image')
    save_images(result, directory, image_index)
    return result


#
# get_info_test(1, 'dfads')

# def get_info(table, directory, image_index=12):
#     # tables = {1: sh.worksheet('index', 1), 2: sh.sheet2, 3: sh.sheet3, 4: sh.sheet4, 5: sh.sheet5}
#     wks = sh.worksheet('index', table)
#     result = list()
#     now = datetime.now()
#     for cnt in range(2, 5000):
#         if cnt % 100 == 0:
#             print(now)
#             print(datetime.now() - now)
#             now = datetime.now()
#             print(cnt)
#         data = wks.range(f'B{cnt}:Q{cnt}')
#         if data[0][0].value:
#             result.append([i.value for i in data[0] if i.value or i.value == ' '])
#         else:
#             break
#     print('Start save images')
#     save_images(result, directory, image_index)

# return result
# print(get_info(0, 'dfad'))


def delete_dirs(directory):
    path = os.path.join('commercial_proposal', 'images', directory)
    # print(path)
    for index, dir_ in enumerate(os.walk(path)):
        if index == 0:
            pass
        else:
            shutil.rmtree(dir_[0])


# gdd.download_file_from_google_drive(file_id='1iytA1n2z4go3uVCwE__vIKouTKyIDjEq',
#                                     dest_path='./data/mnist.zip',
#                                     unzip=True)
def save_images(data, directory, image_index):
    # path = os.path.join('commercial_proposal', 'images', directory)
    path = os.path.join('images', directory)
    delete_dirs(directory)
    for camera in data:
        try:
            # print(camera[image_index])
            url = camera[image_index].split('/')
            if url[2] == 'drive.google.com':
                if not os.path.exists(os.path.join(path, camera[3])):
                    os.mkdir(os.path.join(path, camera[3]))
                name = camera[5].strip().replace('/', '').replace('\\', '')
                path = os.path.join(path, camera[3], name + f'.jpg')
                gdd.download_file_from_google_drive(file_id=url[-2], dest_path=path)
                continue
            else:
            # img = urllib.request.urlopen(camera[image_index])
            # print(img.headers)
                img = urllib.request.urlopen(camera[image_index]).read()
            # print(img)
        except urllib.error.HTTPError as er:
            print('Ошибка при скачивании фото: ', er)
            print(camera[image_index])
            continue
        except Exception as e:
            print('Ошибка при скачивании фото: ', e)
            print(image_index)
            print(camera)
            continue
        if not os.path.exists(os.path.join(path, camera[3])):
            os.mkdir(os.path.join(path, camera[3]))
        name = camera[5].strip().replace('/', '').replace('\\', '')
        # type_file = camera[image_index].split('.')[-1]
        with open(os.path.join(path, camera[3], name + f'.jpg'), 'wb') as file:
            file.write(img)


get_info(3, 'switch', 11)
# def get_info_of_recorder()
#     result = list()
#     for cnt in range(2, 1000):
#         data = wks.range(f'B{cnt}:O{cnt}')
#         if data[0][0].value:
#             result.append([i.value for i in data[0]])
#         else:
#             break
#     save_images(result, 'camera'1QqdE8t9O7QDTIHa8EB1uHh2jnNjRQQVc)
# 1RtXqqxdfYFW6tIrTscyNkEbvaqO8Ab0H3EqtipIB5u0#
#     return result

# img = urllib.request.urlopen('https://cctv.qtech.ru/upload/iblock/881/252K_280219_QVC_IPC_501Z_2.8_12_view.jpg').read()
