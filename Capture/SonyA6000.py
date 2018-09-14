import os

import gphoto2 as gp
import time
import GeneralSettings
from GeneralSettings import logger

class ptpCamera:
    EVENT_FILE_ADDED = gp.GP_EVENT_FILE_ADDED
    EVENT_FOLDER_ADDED = gp.GP_EVENT_FOLDER_ADDED
    EVENT_PTP_CONFIG = 0

    def __init__(self):
        # print("init camera")
        self.camera_ready = False
        self.__context = gp.gp_context_new()
        self.__camera = gp.check_result(gp.gp_camera_new())
        while True:
            # print("Connecting Camera")
            error = gp.gp_camera_init(self.__camera, self.__context)
            if error >= gp.GP_OK:
                # operation completed successfully so exit loop
                # print("Camera init successfull")
                self.camera_ready = True
                break
            if error != gp.GP_ERROR_MODEL_NOT_FOUND:
                # some other error we can't handle here
                if(error == -7):
                    print("Try as super user")
                self.camera_ready = False
                print(gp.GPhoto2Error(error))

            # no camera, try again in 2 seconds
            time.sleep(2)

    def usb_capture(self):
        if self.camera_ready:
                file_path = gp.check_result(gp.gp_camera_capture(
                    self.__camera, gp.GP_CAPTURE_IMAGE, self.__context))
                return file_path
        else:
            return None

    def download_file_from_camera(self, file_path, Targer= GeneralSettings.capture_dir):
        if not os.path.exists(Targer):
            os.makedirs(Targer, exist_ok=True)

        target = os.path.join(Targer, "capt%s.jpg" %(time.time()))
        # target = os.path.join(Targer, file_path.name)
        camera_file = gp.check_result(gp.gp_camera_file_get(
            self.__camera, file_path.folder, file_path.name,
            gp.GP_FILE_TYPE_NORMAL, self.__context))
        gp.check_result(gp.gp_file_save(camera_file, target))

        return target

    def list_files(self, path='/'):
        result = []
        # get files
        for name, value in gp.check_result(
                gp.gp_camera_folder_list_files(self.__camera, path,self.__context)):
            result.append(os.path.join(path, name))
        # read folders
        folders = []
        for name, value in gp.check_result(
                gp.gp_camera_folder_list_folders(self.__camera, path, self.__context)):
            folders.append(name)
        # recurse over subfolders
        for name in folders:
            result.extend(self.list_files(self.__camera, self.__context, os.path.join(path, name)))
        return result

    def watch_event(self, __timeout=10000):
        try:

            event = self.__camera.wait_for_event(__timeout, self.__context)
            return event

        except (gp.GPhoto2Error, IOError):
            print("\nCamera disconnected!")

    def getEventType(self, event):
        return event[0]

    def downloadPictureFromEvent(self, event):
        if event[0] == self.EVENT_FILE_ADDED:
            logger.debug("New file added to camera %s" %event[1])
            return self.download_file_from_camera(event[1])

        else:
            return None

    def __del__(self):
        #print("del camera")
        if self.camera_ready:
            gp.check_result(gp.gp_camera_exit(self.__camera))

