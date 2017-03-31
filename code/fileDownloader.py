from os import makedirs
import os.path
import uuid
from urllib import request
import asyncio

class File_Downloader():
    """Downloads images to local directory dl_cache at same level as /code

    Keeps same file name from URL
    Unique directory name every time
    Renames images of the same name
    @TODO self.attempts is currently total duplicates across all file names
    fail_count is restricted per file
    """

    directory = "../dl_cache/" + str(uuid.uuid4()) + "/"
    attempts = 0
    @asyncio.coroutine
    def download_image(self, image_url):
        fail_count = 1
        local_file = image_url.split('/')[-1]
        makedirs(self.directory, exist_ok=True)

        while(os.path.isfile(self.directory + local_file)):
            (name, ext) = (local_file.split('.')[0], local_file.split('.')[-1])
            local_file = name + self.uniquify() + ext
            self.attempts += 1
        result = request.urlretrieve(image_url, self.directory + local_file)
        # print("this is X" + str(result[1]['Connection']))
        while result[1]['connection'] != 'close':
            print('{0} Failed, attempt {1}'.format(local_file, fail_count))
        # else:
        yield
    # def image_is_downloaded(self):


    # Uniquify filename if already exists
    def uniquify(self):
        return str("(" + str(self.attempts) + ").")

    # def download_image(self, url):
    #     self.image_downloader.download_image(url)
    #     wait(5)
    #     # try:
    #     #     yield from asyncio.sleep(seconds_to_sleep)
    #     # except:
    #     #     pass