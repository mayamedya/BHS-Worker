from networkJobs import networkJobs
from fileJobs import fileJobs
# import RPi.GPIO as GPIO
# import keyboard
from pynput.keyboard import Key, Listener
from threading import Thread
import time
import os
import dotenv
import subprocess
import random
from anydesk import anydesk

adk = anydesk()

dotenv.load_dotenv(dotenv_path='home/pi/Desktop/BHS-Upgrader/.env')

# GPIO.setmode(GPIO.BCM)

# gpio_pins = [16, 5, 25, 19, 27, 23]
keyboard_pins = ["1", "2", "3", "4", "5", "6"]

# for pin in gpio_pins:
#     GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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
            config['isActive'] = NJ.isActive()
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

            for folder in range(config['buttonCount']):
                path = config['fileLocation'] + str(folder+1)
                files = os.listdir(path)
                for file in files:
                    lpath = config['fileLocation'] + str(folder + 1)
                    lpath += "/" + file
                    if os.path.getsize(lpath) < 10:
                        os.remove(lpath)

            # print(jobList)
            time.sleep(3600)
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

if os.getenv("ANYDESK") == "0":
    if adk.generateId():
        time.sleep(10)
        if adk.setPassword("fattoli3417"):
            time.sleep(4)
            anyID = adk.getId()
            if NJ.updateAnyDeskInfo(anyID, os.getenv("PASSWORD")):
                # dotenv.set_key("../../.env", "ANYDESK", anyID)
                print("Setup completed")

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


def controlKey(input_key):
    try:
        input_key = int(input_key.replace("'", ''))
    except Exception as e:
        lsp = []
        for i in range(config['buttonCount']):
            lsp.append(False)
        print(e)
        return lsp

    lsl = []
    for i in range(config['buttonCount']):
        apData = False
        if i+1 == input_key:
            apData = True

        lsl.append(apData)

    return lsl

def onButtonPress(key):
    print(key)

def onButtonRelease(pushedButton):
    try:
        if config['isActive'] and config['isRegistered']:
            pinStatus = controlKey(pushedButton)
            # for pin in range(config['buttonCount']):
            #     # pinStatus.append(False if int(GPIO.input(gpio_pins[pin])) == 0 else True)
            #     pinStatus.append(controlKey(keyboard_pins[pin]))

            if True in pinStatus:
                for pin_slot in range(len(pinStatus)):
                    if pinStatus[pin_slot]:
                        filePath = config['fileLocation'] + str(pin_slot+1) + "/"
                        pathFiles = FJ.getFiles(pin_slot+1)
                        pathLen = len(pathFiles)
                        if pathLen > 0:
                            selectedFile = random.randint(1, pathLen)
                            selectedFile_name = pathFiles[selectedFile-1]
                            selectedFile_path = filePath + selectedFile_name
                            subprocess.run(['cancel', '-a']);
                            subprocess.run(["lp", selectedFile_path + '.pdf'], capture_output=True)
                            print('Printing -> ' + selectedFile_path)
                            os.environ['printCount'] = str(int(os.getenv('printCount')) + 1)
                            dotenv.set_key('home/pi/Desktop/BHS-Upgrader/.env', "printCount", os.environ["printCount"])
                            time.sleep(3)
                            continue
                        else:
                            print("Selected buttons file is empty. Please assign a category or add story to category")

            print(pinStatus)
            time.sleep(0.4)
    except Exception as e:
        print(e)
        print("Error")


with Listener(on_press=onButtonPress, on_release=onButtonRelease) as listener:
    listener.join()
