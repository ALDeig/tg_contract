import os
import shutil

import urllib.request
import pygsheets

import config

client = pygsheets.authorize(service_file=os.path.join('commercial_proposal', 'gsheets', 'creds.json'))
# client = pygsheets.authorize(service_file=os.path.join('creds.json'))
sh = client.open_by_key(config.SHEETS_ID)


def get_info(table, directory, image_index=12):
    # tables = {1: sh.worksheet('index', 1), 2: sh.sheet2, 3: sh.sheet3, 4: sh.sheet4, 5: sh.sheet5}
    wks = sh.worksheet('index', table)
    result = list()
    for cnt in range(2, 1000):
        data = wks.range(f'B{cnt}:P{cnt}')
        if data[0][0].value:
            result.append([i.value for i in data[0] if i.value])
        else:
            break
    save_images(result, directory, image_index)

    return result
# print(get_info(0, 'dfad'))


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
    delete_dirs(directory)
    for camera in data:
        img = urllib.request.urlopen(camera[image_index]).read()
        if not os.path.exists(os.path.join(path, camera[3])):
            os.mkdir(os.path.join(path, camera[3]))
        with open(os.path.join(path, camera[3], camera[5].replace('/', '') + '.jpg'), 'wb') as file:
            file.write(img)

# def get_info_of_recorder()
#     result = list()
#     for cnt in range(2, 1000):
#         data = wks.range(f'B{cnt}:O{cnt}')
#         if data[0][0].value:
#             result.append([i.value for i in data[0]])
#         else:
#             break
#     save_images(result, 'camera')
#
#     return result

