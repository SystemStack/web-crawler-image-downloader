from os import makedirs
from urllib import request
import uuid
from urllib.parse import urlparse
import os.path
class File_Downloader():
    """Downloads images to local directory dl_cache at same level as /code

    Keeps same file name from URL
    Unique directory name every time
    Renames images of the same name
    @TODO self.attempts is currently total duplicates across all file names
    """

    directory = "../dl_cache/" + str(uuid.uuid4()) + "/"
    attempts = 0

    def download_image(self, image_url):
        if image_url == None:
            return
        local_file = image_url.split('/')[-1]
        makedirs(self.directory, exist_ok=True)

        while(os.path.isfile(self.directory + local_file)):
            (name, ext) = (local_file.split('.')[0], local_file.split('.')[-1])
            local_file = name + self.uniquify() + ext
            self.attempts += 1
        request.urlretrieve(image_url, self.directory + local_file)

    # Uniquify filename if already exists
    def uniquify(self):
        return str("(" + str(self.attempts) + ").")