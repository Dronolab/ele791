from time import sleep

from CameraPTP import Camera
from FlashSync import FlashSync
from TriggerHandler import TriggerHandler
from photoSync import PhotoSync


class Server:
    def __init__(self):
        self.flash_sync = FlashSync()
        self.trigger = TriggerHandler()
        self.cameraPTP = Camera()
        self.photoSync = PhotoSync("./Capture/", self.flash_sync.getTimeQueue(), self.cameraPTP.getTimeQueue())



    def SubProcessStart(self):
        print("startig photo server")
        self.flash_sync.start()
        self.trigger.start()
        self.cameraPTP.start()
        self.photoSync.start()

    def cmdWatcher(self):
        print("cmd watcher")
        sleep(100)





