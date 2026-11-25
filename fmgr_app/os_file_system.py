import os
import shutil

from fmgr_app.interfaces import FileSystem


class OsFileSystem(FileSystem):
    """Implementation reelle avec os et shutil"""

    def exists(self, path):
        return os.path.exists(path)

    def is_file(self, path):
        return os.path.isfile(path)

    def is_dir(self, path):
        return os.path.isdir(path)

    def copy(self, source, destination):
        if os.path.isdir(source):
            target = destination
            if os.path.isdir(destination):
                target = os.path.join(destination, os.path.basename(source))
            return shutil.copytree(source, target)
        return shutil.copy2(source, destination)

    def move(self, source, destination):
        return shutil.move(source, destination)

    def remove_file(self, path):
        os.remove(path)

    def remove_dir(self, path):
        shutil.rmtree(path)
