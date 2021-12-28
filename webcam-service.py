import time
import glob
import os
import shutil
import json
from datetime import datetime, timezone

source_path = '/home/webcamuser/img/'
source_img_pattern = 'photo*.jpg'
dest_path = 'pub'

latest_img_name = "current.jpg"
current_file_id_file = "current.json"
next_file_id_file = "inwork.json"

file_timeout_sec = 10


def ensure_output_dir(dest_path):
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

def get_matching_files(source_path, source_img_pattern):
    return glob.glob(source_path + source_img_pattern)

def cleanup_files(files_to_remove):
    for file in files_to_remove:
        print(f"removing: {file}")
        os.remove(file)

def read_contents(source_file):
    output = ""
    with open(source_file, "rb") as fin:
        output = fin.read()

    return output

def is_jpeg(filebytes):
    # JPEG Images start with 0xFFD8
    # https://en.wikipedia.org/wiki/JPEG#JPEG_files
    return filebytes[0] == 0xFF and filebytes[1] == 0xD8

def is_complete(filebytes):
    # JPEG Images end with 0xFFD9
    return filebytes[-2] == 0xFF and filebytes[-1] == 0xD9

def copy_file(source, dest_path, latest_img_name):
    filedata = read_contents(source)

    start = time.monotonic()
    while len(filedata) < 2:
        if time.monotonic() - start > file_timeout_sec:
            print(f"Error: timed out waiting for file {source} start writing")
            return
        time.sleep(0.1)
        filedata = read_contents(source)

    if not is_jpeg(filedata):
        print(f"Error: File {source} not JPEG format")
        return

    start = time.monotonic()
    while not is_complete(filedata):
        if time.monotonic() - start > file_timeout_sec:
            print(f"Error: timed out waiting for file {source} to complete")
            return
        time.sleep(0.1)
        filedata = read_contents(source)

    dest = os.path.join(dest_path, latest_img_name)
    print(f"copying: {source} to {dest}")
    with open(dest, "wb") as fout:
        fout.write(filedata)
    shutil.copystat(source, dest)
    update_file_info()

def update_file_info():
    info = {"current":{
        "name": latest_img_name,
        "time": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
        }}

    inwork = os.path.join(dest_path, next_file_id_file)
    final = os.path.join(dest_path, current_file_id_file)

    with open(inwork, "w") as fout:
        json.dump(info, fout)

    shutil.move(inwork, final)

def loop():
    while True:
        list_of_files = get_matching_files(source_path, source_img_pattern)
        if list_of_files:
            latest = max(list_of_files, key=os.path.getmtime)
            copy_file(latest, dest_path, latest_img_name)

            cleanup_files(list_of_files)
        time.sleep(1)

if __name__ == "__main__":
    ensure_output_dir(dest_path)
    loop()