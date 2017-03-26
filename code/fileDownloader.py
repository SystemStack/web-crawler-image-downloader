from os import makedirs
from urllib import request
import uuid

class File_Downloader():
    directory = "../dl_cache/" + str(uuid.uuid4()) + "/"

    def download_image(self, image_url, local_filename):
        makedirs(self.directory, exist_ok=True)
        request.urlretrieve(image_url, self.directory + local_filename)
