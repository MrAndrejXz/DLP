import logging
import threading
import win32com.client
import win32file
import time


class USBTracker(object):
    ''' Monitor udev for detection of usb '''

    def run(self):
        logging.debug('Запуск потока прослушивания usb')
        threading.Thread(target=self.check).start()

    def locate_usb(self):
        drive_list = []
        drivebits = win32file.GetLogicalDrives()
        for d in range(1, 26):
            mask = 1 << d
            if drivebits & mask:
                # here if the drive is at least there
                drname = '%c:\\' % chr(ord('A') + d)
                t = win32file.GetDriveType(drname)
                if t == win32file.DRIVE_REMOVABLE:
                    drive_list.append(drname)
        return drive_list

    def __insert_db(self, usb_list):
        print(usb_list)

    def check(self):
        usb_list_old = list()
        while True:
            usb_list_now = self.locate_usb()
            if usb_list_now == usb_list_old:
                time.sleep(0.1)
                continue
            else:
                if len(usb_list_now) != 0:
                    self.__insert_db(usb_list_now)
                usb_list_old = usb_list_now
