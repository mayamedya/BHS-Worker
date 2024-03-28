import usb
import re


class printerDriver:
    def __init__(self, printerName, printerManufacturer, printerId):
        self.printerName = printerName
        self.printerManufacturer = printerManufacturer
        self.printerId = printerId

    def getStatus(self):
        return self.convertPrinterToFunction(self.printerId)

    def translateCode(self, code):
        try:
            translateCode = {
                "kp300v": {
                    "-1": ["Bilinmiyor", "yellow"],
                    "0": ["İyi", "green"],
                    "4": ["Kağıt Yok", "yellow"],
                },
                "kp347": {
                    "0": ["Bilinmiyor", "yellow"],
                    "18": ["İyi", "green"],
                    "114": ["Kağıt Yok", "yellow"],
                    "118": ["Arıza", "red"],
                }
            }

            if not translateCode[self.printerId][str(code)][0]:
                return ["Bilinmiyor", "yellow"]

            return [translateCode[self.printerId][str(code)][0], translateCode[self.printerId][str(code)][1]]
        except Exception as e:
            print("translateCode")
            print(e)
            return "Bilinmiyor"

    def convertPrinterToFunction(self, printerId):
        try:
            if printerId == "kp347":
                return self.printer_0001()

            if printerId == "kp300v":
                return self.printer_0002()
        except Exception as e:
            print("Convert Printer To Function")
            print(e)
            return "Bilinmiyor"

    def printer_0001(self):
        try:
            dev = usb.core.find(idVendor=0x0fe6, idProduct=0x811e)

            if not dev:
                return self.translateCode(0)

            dev.reset()

            if dev.is_kernel_driver_active(0):
                dev.detach_kernel_driver(0)

            dev.set_configuration()

            EP_OUT = 0x03
            EP_IN = 0x82

            data = [0x10, 0x04, 0x02]
            dev.write(EP_OUT, data)

            response = dev.read(EP_IN, 8, timeout=10000)
            res_code = response[0]

            return self.translateCode(res_code)
        except Exception as e:
            print(e)
            return self.translateCode(0)

    def printer_0002(self):
        try:
            dev = usb.core.find(idVendor=0x0fe6, idProduct=0x811e)

            if not dev:
                return self.translateCode(-1)

            dev.reset()

            if dev.is_kernel_driver_active(0):
                dev.detach_kernel_driver(0)

            dev.set_configuration()

            EP_OUT = 0x03
            EP_IN = 0x81

            data = [0x1B, 0X76]
            dev.write(EP_OUT, data)

            response = dev.read(EP_IN, 8, timeout=10000)
            res_code = response[0]

            return self.translateCode(res_code)
        except Exception as e:
            print(e)
            return self.translateCode(-1)
