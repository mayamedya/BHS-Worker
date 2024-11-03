import os
import time
import random
from pynput.keyboard import Listener
from datetime import datetime


class buttons:
    def __init__(self, fileJobs, printer):
        self.buttons_count = 0
        self.delay = False
        self.is_listening_time = False
        self.is_device_active = True
        self.file_location = f"{os.getcwd()}/pdf/"
        self.file_controller = fileJobs
        self.printer = printer
        self.listener = Listener(on_release=self.onButtonRelease)
        self.listener.start()
        print(f"[BUTTONS | MAIN] Generating...")
        self.active_status = {
            'BUTTON1': False,
            'BUTTON2': False,
            'BUTTON3': False,
            'BUTTON4': False,
            'BUTTON5': False,
            'BUTTON6': False,
            'BUTTON7': False,
            'BUTTON8': False,
        }
        self.button_taps_to = {
            'BUTTON1': int(os.getenv('BUTTON1', '1')),
            'BUTTON2': int(os.getenv('BUTTON2', '2')),
            'BUTTON3': int(os.getenv('BUTTON3', '3')),
            'BUTTON4': int(os.getenv('BUTTON4', '4')),
            'BUTTON5': int(os.getenv('BUTTON5', '5')),
            'BUTTON6': int(os.getenv('BUTTON6', '6')),
            'BUTTON7': int(os.getenv('BUTTON7', '7')),
            'BUTTON8': int(os.getenv('BUTTON8', '8')),
        }

        print(self.button_taps_to)
        print(f"[BUTTONS | MAIN] Completed")

    def reset_delay(self):
        self.listener.stop()
        time.sleep(5)
        self.delay = False
        self.listener = Listener(on_release=self.onButtonRelease)
        self.listener.start()

    def listener_stop(self):
        self.listener.stop()
        self.listener = Listener(on_release=self.onButtonRelease)

    def listener_continue(self):
        self.listener.start()

    def onButtonRelease(self, pushedButton):
        try:
            if self.delay:
                return

            if not self.is_listening_time:
                if not self.is_device_active:
                    return
                print(f'Someone tried to print a PDF at {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
                return

            pin = self.controlKey(pushedButton)

            if not isinstance(pin, int) or not pin:
                return

            button = f'BUTTON{pin}'
            from_folder = self.button_taps_to.get(button)
            print(from_folder)
            if isinstance(from_folder, int) and 0 < from_folder < 9:
                self.delay = True

                pdfs = self.file_controller.getFiles(from_folder)
                if len(pdfs) > 0:
                    selectedPdf = pdfs[random.randint(0, len(pdfs) - 1)]
                    self.printer.printout(from_folder, selectedPdf)

                self.reset_delay()

            time.sleep(0.4)
        except Exception as e:
            print(e)
            print("Error")

    def onButtonPress(self, key):
        # print(key)
        if str(key).replace("'", '') == 'q':
            quit()

    def controlKey(self, input_key):
        try:
            input_key = int(str(input_key).replace("'", ''))
            return input_key
        except Exception as e:
            return False
 