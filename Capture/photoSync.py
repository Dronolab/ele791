import os
from multiprocessing import Queue

from Utility.processAbstract import ProcessAbstract
import time

class PhotoSync(ProcessAbstract):
    POLLINTERVAL = 1 # Poll interval to watch for new file in sec
    PHOTO_SYNC_TOPIC = "photo_time_referenced"

    def __init__(self,path , flashQueue, cameraQueue):
        ProcessAbstract.__init__(self)
        # self._path = os.path.normpath(path)
        self._path = path
        print(self._path)

        os.makedirs(self._path, exist_ok = True)
        self.entensions = ".jpg", ".jpeg"
        self.substring = "capt"
        self.flashQueue = flashQueue
        self. cameraQueue = cameraQueue
        self.renamedQueue = Queue()

    def _process(self):
        listdir = []
        while self._kill_pill.empty():
            try:
                for filename in sorted(os.listdir(self._path)):
                    if self.substring in filename:
                        if filename.endswith(self.entensions):
                            listdir.append(filename)

                for file in listdir:
                    print(file)
                    # print(self._path)

                    if not self.flashQueue.empty() and not self.flashQueue.empty():
                        filename, file_extension = os.path.splitext(file)
                        print(filename)
                        rename_target =  self._path +'/'+ str(self.flashQueue.get())+file_extension
                        os.rename(self._path + file, rename_target)
                        self.renamedQueue.put(rename_target)
                listdir = []
                time.sleep(self.POLLINTERVAL)
            except KeyboardInterrupt:
                self.softProcessStop()

