import requests as r
import subprocess
import datetime
import time
import json


class networkJobs:
    def __init__(self, device_id: str, auth_key: str):
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

    def versionControl(self, version: str):
        response = r.get(self._versionLink)
        if response.status_code == 200:  ## Define control method
            if response.text != version:
                return False
            else:
                return True
        else:
            print('Version control error')
            return 0

    def setup(self) -> bool:

        try:
            req = r.get('http://clients3.google.com/generate_204')
            if req.status_code != 204:
                print("No internet connection found... Activating device at local mode")
                return True

            wifiName = subprocess.check_output("iw dev wlan0 link | grep SSID | awk '{print $2}'", stderr=subprocess.STDOUT, shell=True)
            time.sleep(3)
            setupCredentials = {
                'id': self._id,
                'authKey': self._authKey,
                'wifiName': wifiName
            }
            print(setupCredentials)

            response = r.post(self._setup_url, json=setupCredentials, headers=self._h)
            if response.status_code == 200: ## Define control method
                return True
            else:
                return False

        except Exception as e:
            print("Error whilst setting up device!", e)
            return True

    def isRegistered(self) -> bool:

        setupCredentials = {
            'id': self._id,
            'authKey': self._authKey
        }

        try:
            req = r.get('http://clients3.google.com/generate_204')
            if req.status_code != 204:
                print("No internet connection found... Activating device at local mode")
                return True

            response = r.post(self._control_url, json=setupCredentials, headers=self._h)
            if response.text and response.text == '-D':
                return False
            validated = True if response.json()['status'] == 1 or response.json()['status'] == 2 else False
            return validated
        except Exception as e:
            # print(e)
            return True

    def isActive(self) -> bool:

        setupCredentials = {
            'id': self._id,
            'authKey': self._authKey
        }

        try:
            req = r.get('http://clients3.google.com/generate_204')
            if req.status_code != 204:
                print("No internet connection found... Activating device at local mode")
                return True

            response = r.post(self._control_url, json=setupCredentials, headers=self._h)
            validated = True if response.json()['status'] == 1 else False
            return validated
        except Exception as e:
            # print(e)
            return True

    def getButtonCount(self) -> int:

        setupCredentials = {
            'id': self._id,
            'authKey': self._authKey
        }

        try:
            req = r.get('http://clients3.google.com/generate_204')
            if req.status_code != 204:
                print("No internet connection found... Activating device at local mode")
                return 6

            response = r.post(self._buttonCount_url, json=setupCredentials, headers=self._h)
            return int(response.json()['count'])
        except Exception as e:
            print(e)
            return 6

    def asyncFiles(self, currentFiles: list) -> list:

        deviceCredentials = {
            'id': self._id,
            'authKey': self._authKey
        }

        try:
            req = r.get('http://clients3.google.com/generate_204')
            if req.status_code != 204:
                print("No internet connection found... Activating device at local mode")
                return []

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

        except Exception as e:
            print("Error whilst asyncing files!")
            print(e)
            return []


    def getWorkingTimes(self):
        deviceCredentials = {
            'id': self._id,
            'authKey': self._authKey,
        }

        try:
            response = r.post(self._clock_url, json=deviceCredentials, headers=self._h)
            if response.status_code == 200:
                original = response.json()
                selections = original['time_data'].split("|")
                selection_start_first_array = selections[0].split("-")[0].split(":")
                selection_start_second_array = selections[1].split("-")[0].split(":")
                selection_end_first_array = selections[0].split("-")[1].split(":")
                selection_end_second_array = selections[1].split("-")[1].split(":")
                return [[datetime.time(int(selection_start_first_array[0]), int(selection_start_first_array[1])), datetime.time(int(selection_end_first_array[0]), int(selection_end_first_array[1]))], [datetime.time(int(selection_start_second_array[0]), int(selection_start_second_array[1])), datetime.time(int(selection_end_second_array[0]), int(selection_end_second_array[1]))] ]
            else:
                return False
        except Exception as e:
            return [[datetime.time(int(1), int(0)), datetime.time(int(23), int(59))], [datetime.time(int(1), int(0)), datetime.time(int(23), int(59))] ]

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
            print(e)
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
            response = r.post(self._printer_status, json=deviceCredentials, headers=self._h)
            if response.status_code == 200:
                # original = response.json()
                # print(original)
                return True
            else:
                return False
        except Exception as e:
            return False

    def getPrinterInformation(self):
        deviceCredentials = {
            'id': self._id,
            'authKey': self._authKey,
        }

        try:
            response = r.post(self._printer_information, json=deviceCredentials, headers=self._h)
            if response.status_code == 200:
                original = response.json()
                # print(original)
                return original
            else:
                return False
        except Exception as e:
            return False
