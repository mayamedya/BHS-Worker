from networkJobs import networkJobs
from fileJobs import fileJobs
import RPi.GPIO as GPIO
from threading import Thread
import time
import os
import dotenv
import subprocess
import random

dotenv.load_dotenv(dotenv_path='/home/pi/Desktop/BHS-Upgrader/.env')

GPIO.setmode(GPIO.BCM)

gpio_pins = [5, 19, 16, 23, 25, 27]

for pin in gpio_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

config = {
    'deviceID': os.getenv("DEVICEID"),
    'authKey': os.getenv("AUTHKEY"),
    'isRegistered': False,
    'fileLocation': os.getcwd() + "/versions/" + str(os.getenv('VERSION')) + "/pdf/",
    'isActive': False,
    'buttonCount': 0,
}

def asyncDevice():
    while True:
        try:
            NJ = networkJobs(config['deviceID'], config['authKey'])
            config['isRegistered'] = NJ.isRegistered()
            bc = NJ.getButtonCount()
            if bc > 0:
                config['buttonCount'] = bc
            else:
                quit("Button count problem")

            FJ = fileJobs(config['buttonCount'], config['fileLocation'])
            FJ.generateFolders()

            fileList = []

            for folder in range(config['buttonCount']):
                folder += 1
                result = FJ.getFiles(folder)
                fileList.append(result)

            jobList = NJ.asyncFiles(fileList)
            print(jobList)
            for folder in range(len(jobList)):
                FJ.deleteFiles(folder+1, jobList[folder][0])
                for file in jobList[folder][1]:
                    content = NJ.downloadFile(file)
                    FJ.saveFile(folder+1, file, content)

            # print(jobList)
            time.sleep(10)
        except Exception as e:
            print(e)
            time.sleep(10)


NJ = networkJobs(config['deviceID'], config['authKey'])

if not NJ.isRegistered():
    if NJ.setup():
        print("Setup request has been sent to server!")
    else:
        quit("There was a problem while setting up the device!")
else:
    config['isRegistered'] = True


while not config["isRegistered"]:
    if NJ.isRegistered():
        print("Verified")
        config['isRegistered'] = True
        bc = NJ.getButtonCount()
        if bc > 0:
            config['buttonCount'] = bc
        else:
            quit("Button count problem")
    else:
        time.sleep(10)


deviceAsync = Thread(target=asyncDevice)
deviceAsync.start()
FJ = fileJobs(config['buttonCount'], config['fileLocation'])

while True:
    try:
        if config['isActive'] and config['isRegistered']:
            pinStatus = []
            for pin in range(config['buttonCount']):
                pinStatus.append(False if int(GPIO.input(gpio_pins[pin])) == 0 else True)
            for pin_slot in range(len(pinStatus)):
                if pinStatus[pin_slot]:
                    filePath = config['fileLocation'].replace(".", "") + str(pin_slot+1) + "/"
                    pathFiles = FJ.getFiles(pin_slot+1)
                    pathLen = len(pathFiles)
                    if pathLen > 0:
                        selectedFile = random.randint(1, pathLen)
                        selectedFile_name = pathFiles[selectedFile-1]
                        selectedFile_path = os.getcwd() + filePath + selectedFile_name
                        subprocess.run(["lp", selectedFile_path + '.pdf'], capture_output=True)
                        print('Printing -> ' + selectedFile_path)
                        os.environ['printCount'] = str(int(os.getenv('printCount')) + 1)
                        dotenv.set_key('../../.env', "printCount", os.environ["printCount"])
                        time.sleep(3)
                        continue
                    else:
                        print("Selected buttons file is empty. Please assign a category or add story to category")

            print(pinStatus)
            time.sleep(1)
    except Exception as e:
        print(e)
        print("Error")
