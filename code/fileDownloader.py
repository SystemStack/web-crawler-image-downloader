from os import makedirs
import os.path
import uuid
from urllib import request
import asyncio

from PIL import Image


"""Downloads images to local directory web-crawler/cache_dl"""
class File_Downloader():
    json_dl = []
    # Generate unique directory for this run
    directory = "../cache_dl/" + str(uuid.uuid4()) + "/"
    attempts = 0

    @asyncio.coroutine
    def download_image(self, image_url):
        # Grab file name from URL
        local_file = image_url.split('/')[-1]
        try:
            # Make the directory, if dir already exists do not throw an exception
            makedirs(self.directory, exist_ok=True)
            # If the file name already exists, then we will make the file name unique
            dir_file = self.directory + local_file
            while(os.path.isfile(dir_file)):
                (name, ext) = (local_file.split('.')[0], local_file.split('.')[-1])
                local_file = name + self.uniquify() + ext
                dir_file = self.directory + local_file
                self.attempts += 1
            # downloads from image_url and stores it in unique_dir/unique_file.ext
            result = request.urlretrieve(image_url, dir_file)
            self.format_json(dir_file)
        except Exception as e:
            print('Error: {0}, url:{1}'.format(str(e),image_url))
        finally:
            yield

    # Uniquify filename if already exists
    def uniquify(self):
        return str("(" + str(self.attempts) + ").")

    # JSON formats the image location, width, and height that will be used in the website
    def format_json(self, file):
        data = {}
        im = Image.open(file)
        (width, height) = im.size
        data['width'] = width
        data['height'] = height
        data['location'] = file
        self.json_dl.append(data)
