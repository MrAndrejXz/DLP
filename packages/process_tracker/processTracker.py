import datetime
import logging
import threading
import time
import win32gui
import win32process
import psutil


class Process_struct(object):
    def __init__(self, title_window, name_process, time_start):
        self.title_window = title_window
        self.name_process = name_process
        self.time_start = time_start

    def __str__(self):
        return '{}\n{}\n{}'.format(self.title_window, self.name_process, self.time_start)


class ProcessTracker(object):

    def _pprint_secs(self, secs):
        # Format seconds in a human readable form.
        now = time.time()
        secs_ago = int(now - secs)
        if secs_ago < 60 * 60 * 24:
            fmt = "%H:%M:%S"
        else:
            fmt = "%Y-%m-%d %H:%M:%S"
        return datetime.datetime.fromtimestamp(secs).strftime(fmt)

    def _get_porcess_name(self, pid):
        # получаем список всех активных процессов с помощью модуля psutil
        processes = list(psutil.process_iter())
        # ищем наш процесс
        for p in processes:
            if p.pid == pid:
                # нашли его, получаем этот процесс и возвращаем его имя
                process = psutil.Process(p.pid)
                return process.name()

    def run(self):
        logging.debug('Запуск потока слежения зза процессами')
        threading.Thread(target=self.check).start()

    def check(self):
        last_pid = 0
        time_start = 0
        time_end = 0
        name_process = None
        while True:
            # получаем id активного окна
            hdlr = win32gui.GetForegroundWindow()
            title_window = win32gui.GetWindowText(hdlr)
            # получаем id процесса с помощью id окна
            pid = win32process.GetWindowThreadProcessId(hdlr)[1]

            if last_pid != pid:
                time_start = datetime.datetime.now()
                last_pid = pid
                name_process = self._get_porcess_name(pid)
                while last_pid == pid:
                    hdlr = win32gui.GetForegroundWindow()
                    pid = win32process.GetWindowThreadProcessId(hdlr)[1]
                    time.sleep(0.1)
                time_end = datetime.datetime.now()
                print("{}\t|\t{} - {}".format(name_process, time_start, time_end))