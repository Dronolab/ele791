import os
from multiprocessing import Queue

from processAbstract import ProcessAbstract
import time

class PhotoSync(ProcessAbstract):
    POLLINTERVAL = 1 # Poll interval to watch for new file in sec
    PHOTO_SYNC_TOPIC = "photo_time_referenced"

    def __init__(self,path, flashQueue, cameraQueue):
        ProcessAbstract.__init__(self)
        self._path = path
        self.entensions = ".jpg", ".jpeg"
        self.substring = "capt"
        self.flashQueue = flashQueue
        self. cameraQueue = cameraQueue
        self.renamedQueue = Queue()

    def _process(self):
        listdir = []
        while not self._kill:
            for filename in os.listdir(self._path):
                if self.substring in filename:
                    if filename.endswith(self.entensions):
                        listdir.append(filename)

            for file in listdir:
                print(file)
                print(self._path)
                if not self.flashQueue.empty() and not self.flashQueue.empty():
                    filename, file_extension = os.path.splitext(file)
                    os.rename(self._path + file, self._path + str(self.flashQueue.get())+file_extension)
                    self.renamedQueue.put(self._path + str(self.flashQueue.get())+file_extension)
            listdir = []
            time.sleep(self.POLLINTERVAL)


