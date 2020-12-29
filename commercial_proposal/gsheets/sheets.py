import os
import shutil

import urllib.request
import pygsheets

import config

client = pygsheets.authorize(service_file=os.path.join('commercial_proposal', 'gsheets', 'creds.json'))
sh = client.open_by_key(config.SHEETS_ID)
wks = sh.sheet1


def get_info_of_cameras():
    result = list()
    for cnt in range(2, 1000):
        data = wks.range(f'B{cnt}:O{cnt}')
        if data[0][0].value:
            result.append([i.value for i in data[0]])
        else:
            break
    save_images(result)

    return result


def delete_dirs():
    path = os.path.join('commercial_proposal', 'images')
    # print(path)
    for index, dir_ in enumerate(os.walk(path)):
        if index == 0:
            pass
        else:
            # print(dir_[0])
            shutil.rmtree(dir_[0])


def save_images(data):
    path = os.path.join('commercial_proposal', 'images')
    delete_dirs()
    for camera in data:
        img = urllib.request.urlopen(camera[13]).read()
        if not os.path.exists(os.path.join(path, camera[3])):
            os.mkdir(os.path.join(path, camera[3]))
        with open(os.path.join(path, camera[3], camera[5] + '.jpg'), 'wb') as file:
            file.write(img)


# os.mkdir('dir1')
# a = os.walk('dir1')
# for index, dir_ in enumerate(a):
#     if index == 0:
#         pass
#     else:
#         os.rmdir(dir_[0])

# print(os.listdir('dir1'))
# shutil.rmtree(os.path.join('dir1', 'dir2'))
# path = os.path.join('dir1', 'dir2')
# if os.path.exists(os.path.join(path, 'dir4')):
#     print('Ok')