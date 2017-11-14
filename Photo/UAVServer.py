from time import sleep

from CameraPTP import Camera
from FlashSync import FlashSync
from Trigger import Trigger
from photoSync import PhotoSync


class Server:
    def __init__(self):
        self.flash_sync = FlashSync()
        self.trigger = Trigger()
        self.cameraPTP = Camera()
        self.photoSync = PhotoSync("./Photo/", self.flash_sync.getTimeQueue(), self.cameraPTP.getTimeQueue())



    def serverStart(self):
        print("startig photo server")
        self.flash_sync.start()
        self.trigger.start()
        self.cameraPTP.start()
        self.photoSync.start()

    def cmdWatcher(self):
        print("cmd watcher")
        sleep(100)





