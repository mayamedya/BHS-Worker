import requests as r
import subprocess
import time
import json


class networkJobs:
    def __init__(self, device_id: str, auth_key: str):
        self.id = device_id
        self.authKey = auth_key
        self.setup_url = "https://panel.buhikayesenin.com/api/setupDevice.php"
        self.control_url = "https://panel.buhikayesenin.com/api/controlDevice.php"
        self.buttonCount_url = "https://panel.buhikayesenin.com/api/buttonCount.php"
        self.async_url = "https://panel.buhikayesenin.com/api/asyncFiles.php"
        self.h = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        self.downloadURL = "https://panel.buhikayesenin.com/api/downloadFile.php"
        self.versionLink = "https://panel.buhikayesenin.com/api/version.php"
        self.anyinfo_url = "https://panel.buhikayesenin.com/api/anydesk.php"

    def versionControl(self, version: str):
        response = r.get(self.versionLink)
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
            wifiName = subprocess.check_output("iw dev wlan0 link | grep SSID | awk '{print $2}'", stderr=subprocess.STDOUT, shell=True)
            time.sleep(3)
            setupCredentials = {
                'id': self.id,
                'authKey': self.authKey,
                'wifiName': wifiName
            }
            print(setupCredentials)

            response = r.post(self.setup_url, json=setupCredentials, headers=self.h)
            if response.status_code == 200: ## Define control method
                return True
            else:
                return False

        except Exception as e:
            print("Error whilst setting up device!", e)
            return False

    def isRegistered(self) -> bool:

        setupCredentials = {
            'id': self.id,
            'authKey': self.authKey
        }

        try:
            response = r.post(self.control_url, json=setupCredentials, headers=self.h)
            validated = True if response.json()['status'] == 1 or response.json()['status'] == 2 else False
            return validated
        except Exception as e:
            # print(e)
            return False

    def isActive(self) -> bool:

        setupCredentials = {
            'id': self.id,
            'authKey': self.authKey
        }

        try:
            response = r.post(self.control_url, json=setupCredentials, headers=self.h)
            validated = True if response.json()['status'] == 1 else False
            return validated
        except Exception as e:
            # print(e)
            return False

    def getButtonCount(self) -> int:

        setupCredentials = {
            'id': self.id,
            'authKey': self.authKey
        }

        try:
            response = r.post(self.buttonCount_url, json=setupCredentials, headers=self.h)
            return int(response.json()['count'])
        except Exception as e:
            print(e)
            return 0

    def asyncFiles(self, currentFiles: list) -> list:

        deviceCredentials = {
            'id': self.id,
            'authKey': self.authKey
        }

        try:
            response = r.post(self.async_url, json=deviceCredentials, headers=self.h)
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

    def downloadFile(self, file: str):
        setupCredentials = {
            'id': self.id,
            'authKey': self.authKey,
            'fileName': file
        }

        try:
            response = r.post(self.downloadURL, json=setupCredentials).content
            return response
        except Exception as e:
            print(e)
            return False

    def updateAnyDeskInfo(self, anyDesk_id: str, anyDesk_password: str) -> bool:
        deviceCredentials = {
            'id': self.id,
            'authKey': self.authKey,
            'anyDesk_id': anyDesk_id,
            'anyDesk_password': anyDesk_password
        }

        try:
            response = r.post(self.anyinfo_url, json=deviceCredentials, headers=self.h)
            if response.status_code == 200:
                # original = response.json()
                # print(original)
                return True
            else:
                return False
        except Exception as e:
            return False