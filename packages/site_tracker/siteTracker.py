import os
import shutil
import glob
import sqlite3
import json
import time
import threading
import winreg
import logging
import re


class SiteTracker(object):
    __chrome = False
    __yandex = False

    def __init__(self):
        """
        1. Инициализируем время последней зафиксированной записи
        2. Инициализируем браузеры
        3. Запрещаем браузерам режим "инкогнито"
        """
        logging.debug('Инициализация времени последней зафиксированной записи...')
        with open('init.json', 'r') as f:
            self.data = json.load(f)

        logging.debug('Инициализация времени последней зафиксированной записи...\tОК')
        logging.debug('Инициализация браузеров...')

        logging.debug('Инициализация Chrome...')
        self.__list_path_histoy_chrome = glob.glob(
            r'{}\Users\*\AppData\Local\Google\Chrome\User Data\**\History'.format(os.environ['SYSTEMDRIVE']),
            recursive=True)
        if len(self.__list_path_histoy_chrome) != 0:
            self.__chrome = True
            logging.debug('Инициализация Chrome...\tTrue')
            logging.debug('Запрет \'Инкогнито\' Chrome...')
            if self.__set_reg(r'Software\Policies\Google\Chrome', 'IncognitoModeAvailability', 1):
                logging.debug('Запрет \'Инкогнито\' Chrome...\tОК')
            else:
                logging.debug('Запрет \'Инкогнито\' Chrome...\tFalse')
        else:
            logging.debug('Инициализация Chrome...\tFalse')

        logging.debug('Инициализация Yandex...')
        self.__list_path_histoy_yandex = glob.glob(
            r'{}\Users\*\AppData\Local\Yandex\YandexBrowser\User Data\**\History'.format(os.environ['SYSTEMDRIVE']),
            recursive=True)
        if len(self.__list_path_histoy_yandex) != 0:
            self.__yandex = True
            logging.debug('Инициализация Yandex...\tOK')
            logging.debug('Запрет \'Инкогнито\' Yandex...')
            if self.__set_reg(r'Software\Policies\YandexBrowser', 'IncognitoModeAvailability', 1):
                logging.debug('Запрет \'Инкогнито\' Yandex...\tОК')
            else:
                logging.debug('Запрет \'Инкогнито\' Yandex...\tFalse')
        else:
            logging.debug('Инициализация Yandex...\tFalse')
        logging.debug('Инициализация браузеров...\tОК')

    @staticmethod
    def __set_reg(reg_path, name, value):
        """
        Функция устанавки значения в реестре

        :param reg_path: Раздел
        :param name: Имя параметра
        :param value: Значение
        """
        try:
            winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            registry_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path, 0,
                                          winreg.KEY_WRITE)
            winreg.SetValueEx(registry_key, name, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(registry_key)
            return True
        except WindowsError:
            return False

    @staticmethod
    def __copy_files(browser, path_files):
        """
        Функция копирования файлов

        :param browser: Название браузера
        :param path_browser: Путь файлам истории браузера
        """
        count = 0
        for i in path_files:
            shutil.copy(i, r'packages\site_tracker\temp\{}\{}_{}.{}'.format(browser, browser, str(count), re.search(r'Users\\(.*)\\AppData', i)[1]))
            count += 1

    def copy(self):
        """
        Копируем файлы истории браузеров
        """
        if self.__chrome:
            logging.debug('Копирование истории Chrome...')
            self.__copy_files('chrome', self.__list_path_histoy_chrome)
            logging.debug('Копирование истории Chrome...\tОК')
        if self.__yandex:
            logging.debug('Копирование истории Yandex...')
            self.__copy_files('yandex', self.__list_path_histoy_yandex)
            logging.debug('Копирование истории Yandex...\tОК')

    def __check(self, browser):
        """
        Функция чтения истории из файлов

        :param browser: Название браузера
        """
        for i in glob.glob(r'packages\site_tracker\temp\{}\*'.format(browser)):
            user =i.split('.')[1]
            print(user)
            conn = sqlite3.connect(i)
            cur = conn.cursor()
            cur.execute(
                'SELECT '
                'datetime(last_visit_time/1000000 + (strftime("%s", "1601-01-01T07:00:00")), "unixepoch") as last_visited, '
                'url, '
                'title, '
                'visit_count '
                'FROM urls '
                'WHERE datetime(last_visit_time/1000000 + (strftime("%s", "1601-01-01T07:00:00")), "unixepoch") > "{date}" '
                'ORDER BY last_visited;'.format(date=self.data['History']['last_{}'.format(browser)]))
            rows = cur.fetchall()
            if len(rows) == 0:
                logging.debug('{}\tНовые записи: False'.format(i))
                continue
            logging.debug('{}\tНовые записи: True'.format(i))

            for i in rows:
                logging.info(i)

            self.data['History']['last_{}'.format(browser)] = rows[len(rows) - 1][0]
            logging.debug('Запись времени последней зафиксированной записи...')
            with open('init.json', 'w') as f:
                json.dump(self.data, f)
            logging.debug('Запись времени последней зафиксированной записи...\t ОК')

    def check(self):
        """
        Читаем историю браузеров
        """
        if self.__chrome:
            if self.data["History"]["last_chrome"] == 0:
                self.data["History"]["last_chrome"] = '1601-01-01 07:00:00'
            logging.debug('Проверка истории на наличие новых записей Chrome')
            self.__check('chrome')
        if self.__yandex:
            logging.debug('Проверка истории на наличие новых записей Yandex')
            self.__check('yandex')

    def copy_check(self):
        while True:
            self.copy()
            self.check()
            time.sleep(10)

    def run(self):
        logging.debug('Запуск потока прослушки истории браузеров')
        threading.Thread(target=self.copy_check).start()
