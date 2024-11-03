from statistics import statistics
from network import networkJobs
from sync import device_sync
from fs_jobs import fileJobs
from printer import Printer
from buttons import buttons
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from anydesk import anydesk
from env_controller import set_env_variable, reload_env

import time
import os

load_dotenv()

device_id = os.getenv('DEVICEID')
authKey = os.getenv('DEVICEKEY')
printer_model = os.getenv('PRINTER_MODEL')

network = networkJobs(device_id, authKey)
statistics = statistics()
printer = Printer(printer_model, statistics)
syncing = device_sync(network, printer)
filecontroller = fileJobs()
buttoncontroller = buttons(filecontroller, printer)
adk = anydesk()

if os.getenv("ANYDESK") == "0":
    try:
        if adk.generateId():
            time.sleep(10)
            if adk.setPassword(os.getenv("PASSWORD")):
                time.sleep(4)
                anyID = adk.getId()
                if network.updateAnyDeskInfo(anyID, os.getenv("PASSWORD")):
                    set_env_variable("ANYDESK", '1')
                    reload_env(find_dotenv())
                    print("Setup completed")
    except Exception as e:
        print(e, 'anydesk')

while True:
    try:
        syncing.syncing_status = network.is_connected()

        deviceStartTime = syncing.deviceStartTime
        deviceEndTime = syncing.deviceEndTime
        device_second_StartTime = syncing.device_second_StartTime
        device_second_EndTime = syncing.device_second_EndTime

        current_time = datetime.now().time()

        if (deviceStartTime <= current_time <= deviceEndTime) or (device_second_StartTime <= current_time <= device_second_EndTime):
            if syncing.isActive and syncing.isRegistered:
                buttoncontroller.is_listening_time = True
                buttoncontroller.is_device_active = True
            else:
                buttoncontroller.is_listening_time = False
                buttoncontroller.is_device_active = False
        else:
            buttoncontroller.is_listening_time = False

        time.sleep(30)
    except Exception as e:
        print('----------[GRANT ERROR]----------')
        print(e)
        time.sleep(30)
