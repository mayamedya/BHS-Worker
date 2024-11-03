from env_controller import get_env, set_env_variable
from fs_jobs import fileJobs
from threading import Thread
from datetime import datetime
import time
import os


class device_sync:
    def __init__(self, networkJobs, printer):
        print(f"[SYNCING | MAIN] Syncing created successfully")
        self.network = networkJobs
        self.printer = printer
        self.deviceStartTime = None
        self.deviceEndTime = None
        self.device_second_StartTime = None
        self.device_second_EndTime = None
        self.isRegistered = int(get_env('REGISTERED')) or 0
        self.isActive = True
        self.buttonCount = int(get_env('BUTTONCOUNT'))
        self.pdf_file_location = f"{os.getcwd()}/pdf/"
        self.FJ = fileJobs()

        [[self.deviceStartTime, self.deviceEndTime], [self.device_second_StartTime, self.device_second_EndTime]] = self.network.getWorkingTimes()

        self.thread = Thread(target=self.async_device)
        self.syncing_status = True

        self.thread.start()

    def async_device(self):
        while True:
            if self.syncing_status:
                try:
                    control_isRegistered = 1 if self.network.isRegistered() else 0
                    if control_isRegistered != self.isRegistered:
                        self.isRegistered = control_isRegistered
                        set_env_variable('REGISTERED', control_isRegistered)

                    if control_isRegistered == 0:
                        print('Device is not registered. Waiting 30 seconds for next try...')
                        time.sleep(30)
                        continue

                    self.isActive = self.network.isActive()

                    bc = self.network.getButtonCount()
                    if 0 < bc != self.buttonCount:
                        self.buttonCount = bc
                        set_env_variable('BUTTONCOUNT', bc)

                    self.FJ.generateFolders()

                    fileList = []

                    for folder in range(self.buttonCount):
                        folder += 1
                        result = self.FJ.getFiles(folder)
                        fileList.append(result)

                    jobList = self.network.asyncFiles(fileList)
                    job_list_data_printout = [[len(i[0]), len(i[1])] for i in jobList]
                    is_changed = False

                    for i, list_data in enumerate(job_list_data_printout):
                        if list_data[0] > 0:
                            print(f'[X - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] Deleting total of {list_data[0]} from folder pdf/{i+1}')
                            is_changed = True
                        if list_data[1] > 0:
                            print(f'[~ - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] Downloading total of {list_data[1]} to folder pdf/{i+1}')
                            is_changed = True

                    if not is_changed:
                        print(f'[Sync | {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] There was nothing to do')

                    for folder in range(len(jobList)):
                        self.FJ.deleteFiles(folder + 1, jobList[folder][0])
                        for file in jobList[folder][1]:
                            content = self.network.downloadFile(file)
                            if not content:
                                continue
                            self.FJ.saveFile(folder + 1, file, content)

                    for folder in range(self.buttonCount):
                        path = self.pdf_file_location + str(folder + 1)
                        files = os.listdir(path)
                        for file in files:
                            lpath = self.pdf_file_location + str(folder + 1)
                            lpath += "/" + file
                            if os.path.getsize(lpath) < 10:
                                os.remove(lpath)

                    working_times = self.network.getWorkingTimes()
                    self.deviceStartTime = working_times[0][0]
                    self.deviceEndTime = working_times[0][1]
                    self.device_second_StartTime = working_times[1][0]
                    self.device_second_EndTime = working_times[1][1]
                    print(f'~~~~~~~~{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}~~~~~~~~`')
                    print(f'Device working times #1: {self.deviceStartTime} - {self.deviceEndTime}')
                    print(f'Device working times #2: {self.device_second_StartTime} - {self.device_second_EndTime}')
                    print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

                    printer_information = self.network.getPrinterInformation()

                    if printer_information:
                        if get_env('PRINTER_MODEL') != printer_information['printerID']:
                            self.printer.change_printer_device(printer_information['printerID'])
                            set_env_variable('PRINTER_MODEL', printer_information['printerID'])

                        self.network.updatePrinterStatus(self.printer.printer_status, self.printer.level_code)
                    time.sleep(300)
                except Exception as e:
                    print('############## Async Problem ##############')
                    print(e)
                    print('###########################################')
                    time.sleep(10)
            else:
                self.isActive = True
                self.isRegistered = True
                time.sleep(30)
