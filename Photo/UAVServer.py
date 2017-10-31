from multiprocessing import  Process
from time import sleep

from FlashSync import FlashSync
from Trigger import Trigger
from CameraPTP import Camera

class Server:
    def __init__(self):
        self.flash_sync = FlashSync()
        self.trigger = Trigger()
        self.cameraPTP = Camera()


    def serverStart(self):
        print("startig photo server")
        self.flash_sync.start()
        self.trigger.start()
        self.cameraPTP.start()
        sleep(10)
        print("asdads")
        self.trigger._kill = True


        while True:
            time = self.flash_sync.getFlashTime()
            print(time)
            if time == None:
                break





