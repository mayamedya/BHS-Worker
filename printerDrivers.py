import usb
import re


class printerDriver:
    def __init__(self, printerName, printerManufacturer, printerId):
        self.printerName = printerName
        self.printerManufacturer = printerManufacturer
        self.printerId = printerId

    def getStatus(self):
        return

    def translateCode(self, code):
        translateCode = {
            "kp300v":{
                -1: "Bilinmiyor",
                0: "İyi",
                4: "Kağıt Yok",
            },
            "kp347":{
                0: "Bilinmiyor",
                18: "İyi",
                114: "Kağıt Yok",
                118: "Arıza",
            }
        }

        if not translateCode[code]:
            return "Bilinmiyor"

        return translateCode[code]

    def convertPrinterToFunction(self, printerId):
        if printerId == "kp347":
            return self.printer_0001()

        if printerId == "kp300v":
            return self.printer_0002()

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
            pattern = re.compile(r"array\('B', \[[0-9]+\]\)", re.IGNORECASE)
            res_code = pattern.match(response)

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
            pattern = re.compile(r"array\('B', \[[0-9]+\]\)", re.IGNORECASE)
            res_code = pattern.match(response)

            return self.translateCode(res_code)
        except Exception as e:
            print(e)
            return self.translateCode(-1)
