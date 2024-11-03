import requests as r
import datetime
import time
import os
import dotenv
import env_controller


class networkJobs:
    def __init__(self, device_id: str, auth_key: str):
        print(f"[NETWORK | MAIN] Network access creating using id:{device_id}")

        self._id = device_id
        self._authKey = auth_key
        self._setup_url = "https://panel.buhikayesenin.com/api/setupDevice.php"
        self._control_url = "https://panel.buhikayesenin.com/api/controlDevice.php"
        self._buttonCount_url = "https://panel.buhikayesenin.com/api/buttonCount.php"
        self._async_url = "https://panel.buhikayesenin.com/api/asyncFiles.php"
        self._downloadURL = "https://panel.buhikayesenin.com/api/downloadFile.php"
        self._versionLink = "https://panel.buhikayesenin.com/api/version.php"
        self._anyinfo_url = "https://panel.buhikayesenin.com/api/anydesk.php"
        self._clock_url = "https://panel.buhikayesenin.com/api/getclock.php"
        self._printer_status = "https://panel.buhikayesenin.com/api/change_printer_status.php"
        self._printer_information = "https://panel.buhikayesenin.com/api/get_printer_information.php"
        self._h = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        print(f"[NETWORK | MAIN] Network class generated")

        if self.is_connected():
            if not self.isRegistered():
                self.setup()
                print('Registiration Sent')
                while not self.isRegistered():
                    print('Waiting for system grant...')
                    time.sleep(5)

    def is_connected(self):
        try:
            r.get('https://www.google.com', timeout=5)
            return True
        except (r.ConnectionError, r.Timeout):
            return False

    def versionControl(self, version: str):
        try:
            if self.is_connected():
                response = r.get(self._versionLink)
                if response.status_code == 200:
                    if response.text != version:
                        return False
                    else:
                        print('Continuing on current version')
                        return True
                else:
                    print('Version control error')
                    return True
            else:
                print('Version cannot be checked currently. No internet interface found')
                return True
        except Exception as e:
            print('-------------Version Control-------------')
            print(e)
            print('--------------------------')

    def setup(self) -> bool:

        try:
            if self.is_connected():
                # wifiName = subprocess.check_output("iw dev wlan0 link | grep SSID | awk '{print $2}'", stderr=subprocess.STDOUT, shell=True)
                time.sleep(3)
                setupCredentials = {
                    'id': self._id,
                    'authKey': self._authKey,
                    'wifiName': "Device Setup"
                }
                print(setupCredentials)

                response = r.post(self._setup_url, json=setupCredentials, headers=self._h)
                if response.status_code == 200:
                    return True
                else:
                    return False
            else:
                print('Setup process failed due no internet connection')
                return False

        except Exception as e:
            print('-------------Setup Process-------------')
            print(e)
            print('--------------------------')
            return False

    def isRegistered(self) -> bool:

        setupCredentials = {
            'id': self._id,
            'authKey': self._authKey
        }

        try:
            if self.is_connected():
                response = r.post(self._control_url, json=setupCredentials, headers=self._h)
                if response.text and response.text == '-D':
                    return False
                validated = True if response.json()['status'] == 1 or response.json()['status'] == 2 else False
                return validated
            else:
                print('Registration  data is not available. Continuing for no network mode')
                return True
        except Exception as e:
            print('-------------Is Device Registered-------------')
            print(e)
            print('--------------------------')
            return True

    def isActive(self) -> bool:

        setupCredentials = {
            'id': self._id,
            'authKey': self._authKey
        }

        try:
            if self.is_connected():
                response = r.post(self._control_url, json=setupCredentials, headers=self._h)
                validated = True if response.json()['status'] == 1 else False
                return validated
            else:
                print('Device active status is not available. Continuing for no network mode')
                return True
        except Exception as e:
            print('-------------Is Device Active-------------')
            print(e)
            print('--------------------------')
            return True

    def getButtonCount(self) -> int:

        setupCredentials = {
            'id': self._id,
            'authKey': self._authKey
        }

        try:
            if self.is_connected():
                response = r.post(self._buttonCount_url, json=setupCredentials, headers=self._h)
                return int(response.json()['count'])
            else:
                print('Button count is not available. Returning last count for device')
                return int(os.getenv('BUTTONCOUNT'))
        except Exception as e:
            print('-------------Button Count Setup-------------')
            print(e)
            print('--------------------------')
            return int(os.getenv('BUTTONCOUNT'))

    def asyncFiles(self, currentFiles: list) -> list:

        deviceCredentials = {
            'id': self._id,
            'authKey': self._authKey
        }

        try:
            if self.is_connected():
                response = r.post(self._async_url, json=deviceCredentials, headers=self._h)
                if response.status_code == 200:
                    original = response.json()
                    # print(original)
                    total_files = []
                    for i in range(len(original)):
                        wd = []  # Delete
                        wg = []  # Download

                        for f in currentFiles[i]:
                            if f not in original[i]:
                                wd.append(f)
                        for j in original[i]:
                            if j not in currentFiles[i]:
                                wg.append(j)

                        total_files.append([wd, wg])

                    return total_files
                else:
                    return []
            else:
                print('Network not found. Async method is exiting with empty data')
                return []

        except Exception as e:
            print('-------------Async Files-------------')
            print(e)
            print('--------------------------')
            return []


    def getWorkingTimes(self):
        deviceCredentials = {
            'id': self._id,
            'authKey': self._authKey,
        }

        try:
            if self.is_connected():
                response = r.post(self._clock_url, json=deviceCredentials, headers=self._h)
                if response.status_code == 200:
                    original = response.json()
                    selections = original['time_data'].split("|")
                    selection_start_first_array = selections[0].split("-")[0].split(":")
                    selection_start_second_array = selections[1].split("-")[0].split(":")
                    selection_end_first_array = selections[0].split("-")[1].split(":")
                    selection_end_second_array = selections[1].split("-")[1].split(":")
                    env_controller.set_env_variable('WORKTIME_START', f"{selection_start_first_array[0]}:{selection_start_first_array[1]}")
                    env_controller.set_env_variable('WORKTIME_END',
                                                    f"{selection_end_first_array[0]}:{selection_end_first_array[1]}")
                    env_controller.set_env_variable('WORKTIME_SECOND_START',
                                                    f"{selection_start_second_array[0]}:{selection_start_second_array[1]}")
                    env_controller.set_env_variable('WORKTIME_SECOND_END',
                                                    f"{selection_end_second_array[0]}:{selection_end_second_array[1]}")
                    env_controller.reload_env(dotenv.find_dotenv())
                    return [[datetime.time(int(selection_start_first_array[0]), int(selection_start_first_array[1])), datetime.time(int(selection_end_first_array[0]), int(selection_end_first_array[1]))], [datetime.time(int(selection_start_second_array[0]), int(selection_start_second_array[1])), datetime.time(int(selection_end_second_array[0]), int(selection_end_second_array[1]))] ]
                else:
                    return False
            else:
                print('Network not found, starting at the last set time...')
                return [[datetime.time(int(os.getenv('WORKTIME_START').split(':')[0]), int(os.getenv('WORKTIME_START').split(':')[1])), datetime.time(int(os.getenv('WORKTIME_END').split(':')[0]), int(os.getenv('WORKTIME_END').split(':')[1]))], [datetime.time(int(os.getenv('WORKTIME_SECOND_START').split(':')[0]), int(os.getenv('WORKTIME_SECOND_START').split(':')[1])), datetime.time(int(os.getenv('WORKTIME_SECOND_END').split(':')[0]), int(os.getenv('WORKTIME_SECOND_END').split(':')[1]))]]
        except Exception as e:
            print('-------------Async Time-------------')
            print(e)
            print('--------------------------')
            return [[datetime.time(int(os.getenv('WORKTIME_START').split(':')[0]), int(os.getenv('WORKTIME_START').split(':')[1])), datetime.time(int(os.getenv('WORKTIME_END').split(':')[0]), int(os.getenv('WORKTIME_END').split(':')[1]))], [datetime.time(int(os.getenv('WORKTIME_SECOND_START').split(':')[0]), int(os.getenv('WORKTIME_SECOND_START').split(':')[1])), datetime.time(int(os.getenv('WORKTIME_SECOND_END').split(':')[0]), int(os.getenv('WORKTIME_SECOND_END').split(':')[1]))]]

    def downloadFile(self, file: str):
        setupCredentials = {
            'id': self._id,
            'authKey': self._authKey,
            'fileName': file
        }

        try:
            response = r.post(self._downloadURL, json=setupCredentials).content
            return response
        except Exception as e:
            print('-------------Download File-------------')
            print(e)
            print('--------------------------')
            return False

    def updateAnyDeskInfo(self, anyDesk_id: str, anyDesk_password: str) -> bool:
        deviceCredentials = {
            'id': self._id,
            'authKey': self._authKey,
            'anyDesk_id': anyDesk_id,
            'anyDesk_password': anyDesk_password
        }

        try:

            response = r.post(self._anyinfo_url, json=deviceCredentials, headers=self._h)
            if response.status_code == 200:
                # original = response.json()
                # print(original)
                return True
            else:
                return False
        except Exception as e:
            return False

    def updatePrinterStatus(self, status_string, level):
        deviceCredentials = {
            'id': self._id,
            'authKey': self._authKey,
            'status_code': status_string,
            'level': level
        }

        try:
            if self.is_connected():
                response = r.post(self._printer_status, json=deviceCredentials, headers=self._h)
                if response.status_code == 200:
                    return True
                else:
                    return False
            else:
                print('Network not found. Device status is not sent.')
                return False
        except Exception as e:
            print('-------------Update Printer Status-------------')
            print(e)
            print('--------------------------')
            return False

    def getPrinterInformation(self):
        deviceCredentials = {
            'id': self._id,
            'authKey': self._authKey,
        }

        try:
            if self.is_connected():
                response = r.post(self._printer_information, json=deviceCredentials, headers=self._h)
                if response.status_code == 200:
                    original = response.json()
                    return original
                else:
                    return False
            else:
                return False
        except Exception as e:
            print('-------------Get Printer Information-------------')
            print(e)
            print('--------------------------')
            return False
