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
        try:
            # #Malformed URLs
            # if '://' not in image_url:
            #     image_url = self.root_url + image_url
            local_file = image_url.split('/')[-1]
            makedirs(self.directory, exist_ok=True)
            while(os.path.isfile(self.directory + local_file)):
                (name, ext) = (local_file.split('.')[0], local_file.split('.')[-1])
                local_file = name + self.uniquify() + ext
                self.attempts += 1
            result = request.urlretrieve(image_url, self.directory + local_file)
            while result[1]['connection'] != 'close':
                print('{0} Failed, attempt {1}'.format(local_file, fail_count))
                fail_count+=1
        except Exception as e:
            print('Error: {0}, url:{1}'.format(str(e),image_url))
        finally:
            yield


    # Uniquify filename if already exists
    def uniquify(self):
        return str("(" + str(self.attempts) + ").")

    def set_url(self, url):
        self.root_url = url
