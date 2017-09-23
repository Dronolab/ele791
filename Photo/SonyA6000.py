import os

import gphoto2 as gp

class PTP:
    def __init__(self):
        self.__context = gp.gp__context_new()
        self.__camera = gp.check_result(gp.gp_camera_new())
        self.camera_ready = True
        try:
            gp.gp_camera_init(self.__camera, self.__context)
        except gp.GPhoto2Error as ex:
            if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                self.camera_ready = False
            # some other error we can't handle here
            raise
        
    def usb_capture(self):
        file_path = gp.check_result(gp.gp_camera_capture(
            self.__camera, gp.GP_CAPTURE_IMAGE, self.__context))
        return file_path

    def download_file_from_camera(self, file_path, Targer="./Photo"):
        if not os.path.exists(Targer):
            os.makedirs(Targer)
        target = os.path.join(Targer, file_path.name)
        camera_file = gp.check_result(gp.gp_camera_file_get(
            self.__camera, file_path.folder, file_path.name,
            gp.GP_FILE_TYPE_NORMAL, self.__context))
        gp.check_result(gp.gp_file_save(camera_file, target))

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
        event = self.__camera.wait_for__event(__timeout, self.__context)

    def __del__(self):
        if self.camera_ready:
            gp.check_result(gp.gp_camera_exit(self.__camera, self.__context))