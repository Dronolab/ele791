from multiprocessing import Queue, Process, Lock

class ProcessAbstract:
    def __init__(self):
        # self._timeQueue = Queue()

        self._kill_pill = Queue()
        self._process_lock = Lock()
        self._proc = None
        self._createNewProcess()

    def _createNewProcess(self):
        self._proc = Process(target=self._process)
        self._proc.daemon = True

    def start(self):
        if not self._proc == None:
            self._proc.start()

    def hardProcessStop(self):
        self._proc.terminate()

    def softProcessStop(self):
        self._kill_pill.put("DIE")

    def pauseLoop(self):
        self._process_lock.acquire()

    def resumeLoop(self):
        self._process_lock.release()

    def is_alive(self):
        return self._proc.is_alive()

    # def addTimeToQueue(self,localtime):
    #     self._timeQueue.put(localtime)
    #
    # def qetTimeFromQueue(self):
    #     if not self._timeQueue.empty():
    #         return self._timeQueue.get()
    #     else:
    #         return None
    #
    # def getTimeQueue(self):
    #     return self._timeQueue