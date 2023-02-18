import string
from subprocess import run


class anydesk:
    def __init__(self) -> None:
        pass

    def setPassword(self, password: str) -> bool:
        try:
            run(['echo', '"' + password + '"', "|", "sudo", "anydesk",  "--set-password"], capture_output=True)
            return True
        except Exception as e:
            return False

    def generateId(self) -> bool:
        try:
            run(['sudo', 'systemctl', 'stop', 'anydesk'])
            run(['sudo', 'rm', '/etc/anydesk/service.conf'], capture_output=True)
            run(['sudo', 'systemctl', 'start', 'anydesk'])
            return True
        except:
            return False

    def getId(self) -> string:
        anydesk_id = run(['anydesk', '--get-id'], capture_output=True).stdout.decode()
        return anydesk_id
