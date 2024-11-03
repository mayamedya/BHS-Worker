# This will hold statistics1 and send it
import json
import traceback

from env_controller import get_env, set_env_variable
from datetime import datetime
import os


class statistics:
    def __init__(self):
        self.current_tap_count = int(get_env('TAP_COUNT'))
        self.statistics_file = f"{os.getcwd()}/statistics/full_log.json"

        if not os.path.exists(self.statistics_file):
            os.makedirs(os.path.dirname(self.statistics_file), exist_ok=True)
            with open(self.statistics_file, 'w') as file:
                json.dump({"data": []}, file)

        print(f"[STATISTICS | MAIN] Statistics opened successfully")

    def add_tap(self, button, pdf_id):
        self.current_tap_count += 1
        set_env_variable('TAP_COUNT', self.current_tap_count)
        with open(self.statistics_file, 'r+') as file:
            content = file.read()
            if content:
                json_statistics = json.loads(content)
            else:
                json_statistics = {"data": []}

            json_statistics['data'].append({
                "job": "print",
                "pdf": pdf_id,
                "button": button,
                "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            })

            file.seek(0)
            json.dump(json_statistics, file)
            file.truncate()

    def log_printer(self, printer_model, status_code):
        with open(self.statistics_file) as file:
            json_statistics = json.loads(file.read())
            json_statistics['data'].append({"job": "printer_control", "model": printer_model, "code": status_code, "timestamp": datetime.now()})
            file.write(json.dumps(json_statistics))
            file.close()
