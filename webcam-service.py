import time
import glob
import os
import shutil

source_path = '/home/webcamuser/img/'
source_img_pattern = 'photo*.jpg'
dest_path = 'pub'

latest_img_name = "current.img"

if not os.path.exists(dest_path):
    os.mkdir(dest_path)

while True:
    list_of_files = glob.glob(source_path + source_img_pattern)
    if list_of_files:
        latest = max(list_of_files, key=os.path.getmtime)
        dest = os.path.join(dest_path, latest_img_name)
        print(f"copying: {latest} to {dest}")
        shutil.copy(latest, dest)

        for file in list_of_files:
            print(f"removing: {file}")
            os.remove(file)

    time.sleep(1)