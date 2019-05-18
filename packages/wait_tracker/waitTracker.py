from datetime import timedelta
from datetime import datetime
import win32api
import time
import threading
import logging


class WaitTracker(object):

    def __init__(self, allow_time):
        self.allow_time = allow_time

    def run(self):
        """
        Запуск потока
        """
        logging.debug('Запуск потока слежения простоя')
        threading.Thread(target=self.check).start()

    def __message(self, time_start, time_end):
        # try:
        #     logging.debug('Вставка в БД...')
        #     logging.debug('Вставка в БД...\tОК')
        # except Exception as ex:
        #     logging.debug(ex)
        logging.info('Зафиксирован простой {}-{}: {}'.format(self.get_time(time_start), self.get_time(time_end),
                                                              self.get_time(time_end - time_start)))

    def stop(self):
        """Флаг выхода из цикла"""
        self.flag_stop = True

    def check(self):
        """
        Запуск проверки простоя
        """
        old_tik = 0
        while True:
            current_tik = win32api.GetLastInputInfo()
            logging.debug('Текущий тик {}'.format(current_tik))
            if current_tik == old_tik:
                time_start = datetime.now()
                while current_tik == old_tik:
                    current_tik = win32api.GetLastInputInfo()
                    logging.debug('Текущий тик {}'.format(current_tik))
                    time.sleep(0.5)
                time_end = datetime.now()
                if (time_end - time_start).seconds > self.allow_time:
                    self.__message(time_start, time_end)
                continue
            old_tik = current_tik
            time.sleep(0.5)

    def get_time(self, x_time):
        """
        Вывод времени в формате
        """
        if type(x_time) is timedelta:
            return '{}:{}:{}'.format(x_time.seconds // 3600, (x_time.seconds % 3600) // 60,
                                     (x_time.seconds % 3600) % 60)
        return '{}:{}:{}'.format(x_time.hour, x_time.minute, x_time.second)
