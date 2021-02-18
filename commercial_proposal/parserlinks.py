import json
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


# options = webdriver.ChromeOptions()
# options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36')
# options.add_argument("--disable-blink-features=AutomationControlled")
# driver = webdriver.Chrome(options=options)
# driver.get('https://sekundomer.net/')
# # time.sleep(3)
# key = driver.find_element_by_id('start')
# key.click()
# time.sleep(5)
# for _ in range(10):
#     timer = driver.find_element_by_id('timer')
#     print(timer.text)
# key.click()
# time.sleep(2)
# driver.close()
class ParserLinks:

    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('headless')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument('--disable-infobars')
    # chrome_options.add_argument('--remote-debugging-port=9222')
    # driver = webdriver.Chrome(chrome_options=chrome_options)
    # # self.driver = webdriver.Chrome()
    # result_list = ('cup_r_2', 'cup_r_4', 'cup_o_2', 'cup_o_4',
    #                     'cyl_r_2', 'cyl_r_4', 'cyl_o_2', 'cyl_o_4',
    #                     'com_r_2', 'com_r_4', 'com_o_2', 'com_o_4')
    # result = dict()

    def __init__(self):
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-infobars')
        self.chrome_options.add_argument('--remote-debugging-port=9222')
        self.driver = webdriver.Chrome(chrome_options=self.chrome_options)
        # self.driver = webdriver.Chrome()
        self.result_list = ('cup_r_2', 'cup_r_4', 'cup_o_2', 'cup_o_4',
                            'cyl_r_2', 'cyl_r_4', 'cyl_o_2', 'cyl_o_4',
                            'com_r_2', 'com_r_4', 'com_o_2', 'com_o_4')
        self.result = dict()

    def get_page(self):
        self.driver.get('https://hi.watch/products/selection?c-camera,c-camera')
        self.driver.implicitly_wait(5)

    def get_bottoms(self):
        btm_body = {'cupol': "input_1_2",
                    'cylindr': 'input_1_3',
                    'compact': 'input_1_4'}
        btm_execution = {'room': 'input_2_1',
                         'outdoor': 'input_2_2'}
        btm_ppi = {'2mp': 'input_5_6',
                   '4mp': 'input_5_4'}

        return btm_body, btm_execution, btm_ppi

    def get_links(self, bottoms):
        actions = ActionChains(self.driver)
        cnt = 0
        for body in bottoms[0].values():
            body_btn = body
            for execute in bottoms[1].values():
                execute_btn = execute
                for ppi in bottoms[2].values():
                    actions = ActionChains(self.driver)
                    actions.click(self.driver.find_element_by_id(execute_btn))
                    actions.click(self.driver.find_element_by_id('input_32_1'))
                    actions.click(self.driver.find_element_by_id(body_btn))
                    actions.click(self.driver.find_element_by_id(ppi))
                    actions.click(self.driver.find_element_by_id('input_12_4'))
                    actions.perform()
                    self.driver.implicitly_wait(5)
                    time.sleep(5)
                    elements = self.driver.find_elements_by_class_name('uk-width-large-1-4')
                    links = []
                    for elem in elements[1:]:
                        href = elem.find_element_by_tag_name('a')
                        links.append(href.get_attribute('href'))

                    self.result[self.result_list[cnt]] = links
                    cnt += 1
                    time.sleep(5)
                    self.driver.get('https://hi.watch/products/selection?c-camera,c-camera')

    def save_result(self):
        with open('links_hiwatch.json', 'w', encoding='utf-8') as file:
            json.dump(self.result, file, indent=4, ensure_ascii=True)

        print('Файл создан')

    def main(self):
        self.get_page()
        bottoms = self.get_bottoms()
        self.get_links(bottoms)
        self.save_result()
        self.driver.close()


# parser = Parser()
# parser.main()

