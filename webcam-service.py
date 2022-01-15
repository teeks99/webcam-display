import time
import glob
import os
import shutil
import json
from datetime import datetime, timezone
from string import Template
from PIL import Image

source_path = '/home/webcamuser/img/'
source_img_pattern = 'photo*.jpg'

title = "Teeks99 SkyCam"

dest_path = 'pub'

latest_img_name = "current.jpg"
current_file_id_file = "current.json"
next_file_id_file = "inwork.json"

file_timeout_sec = 10
prior_count = 0
sizes = [2048, 1024, 512, 256]

info_file = "info.json"
info = {
    "total_updates": 0,
    "timeline" : {
        latest_img_name: { "time": 0},
        "prior-00s.jpg": {"time": 0},
        "prior-10s.jpg": {"time": 0},
        "prior-20s.jpg": {"time": 0},
        "prior-30s.jpg": {"time": 0},
        "prior-40s.jpg": {"time": 0},
        "prior-50s.jpg": {"time": 0},
        "prior-01m.jpg": {"time": 0},
        "prior-02m.jpg": {"time": 0},
        "prior-03m.jpg": {"time": 0},
        "prior-04m.jpg": {"time": 0},
        "prior-05m.jpg": {"time": 0},
        "prior-06m.jpg": {"time": 0},
        "prior-07m.jpg": {"time": 0},
        "prior-08m.jpg": {"time": 0},
        "prior-09m.jpg": {"time": 0},
        "prior-10m.jpg": {"time": 0},
        "prior-20m.jpg": {"time": 0},
        "prior-30m.jpg": {"time": 0},
        "prior-40m.jpg": {"time": 0},
        "prior-50m.jpg": {"time": 0},
        "prior-01h.jpg": {"time": 0},
        "prior-02h.jpg": {"time": 0},
        "prior-03h.jpg": {"time": 0},
        "prior-04h.jpg": {"time": 0},
        "prior-05h.jpg": {"time": 0},
        "prior-06h.jpg": {"time": 0},
        "prior-07h.jpg": {"time": 0},
        "prior-08h.jpg": {"time": 0},
        "prior-09h.jpg": {"time": 0},
        "prior-10h.jpg": {"time": 0},
        "prior-11h.jpg": {"time": 0},
        "prior-12h.jpg": {"time": 0},
        "prior-13h.jpg": {"time": 0},
        "prior-14h.jpg": {"time": 0},
        "prior-15h.jpg": {"time": 0},
        "prior-16h.jpg": {"time": 0},
        "prior-17h.jpg": {"time": 0},
        "prior-18h.jpg": {"time": 0},
        "prior-19h.jpg": {"time": 0},
        "prior-20h.jpg": {"time": 0},
        "prior-21h.jpg": {"time": 0},
        "prior-22h.jpg": {"time": 0},
        "prior-23h.jpg": {"time": 0},
        "prior-24h.jpg": {"time": 0}
    }
}

def ensure_output_dir(dest_path):
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)

def generate_viewer(dest_path, title):
    template_file = ""
    with open("viewer.html.template", "r") as fin:
        template_file = fin.read()

    t = Template(template_file)
    out = t.substitute(title=title)
    with open(os.path.join(dest_path, "viewer.html"), "w") as fout:
        fout.write(out)

def generate_httaccess(dest_path):
    template_file = ""
    with open(".htaccess.template", "r") as fin:
        template_file = fin.read()

    t = Template(template_file)
    out = t.substitute()
    with open(os.path.join(dest_path, ".htaccess"), "w") as fout:
        fout.write(out)

def load_existing_info(info_path):
    info_path = os.path.join(dest_path, info_path)
    if os.path.exists(info_path):
        with open(info_path, "r") as fin:
            global info
            info = json.load(fin)

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
    sized_copies(dest)

def update_file_info():
    timestamp = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()
    current_info = {"current":{
        "name": latest_img_name,
        "time": timestamp
        
        },
        "sizes": sizes}
    info["timeline"][latest_img_name]["time"] = timestamp

    inwork = os.path.join(dest_path, next_file_id_file)
    final = os.path.join(dest_path, current_file_id_file)

    with open(inwork, "w") as fout:
        json.dump(current_info, fout)

    shutil.move(inwork, final)

def sized_copies(fpath):
    global info
    fname, ext = os.path.splitext(fpath)


    with Image.open(fpath) as img:
        for size in sizes:
            timg = img.copy()
            timg.thumbnail((size, size))
            timg.save(f"{fname}_{size}{ext}", "JPEG")

    info["original_height"] = img.height
    info["original_width"] = img.width
    info["sizes"] = sizes

def copy_prior(source, dest):
    global info
    source_file = os.path.join(dest_path, source)
    dest_file = os.path.join(dest_path, dest)

    source_filepre, source_ext = os.path.splitext(source_file)
    dest_filepre, dest_ext = os.path.splitext(dest_file)

    if os.path.exists(source_file):
        shutil.copy(source_file, dest_file)

        for size in info["sizes"]:
            sf = f"{source_filepre}_{size}{source_ext}"
            df = f"{dest_filepre}_{size}{dest_ext}"
            if os.path.exists(sf):
                shutil.copy(sf, df)
            else:
                print(f"Error - sized copy doesn't exist: {sf}")

        info["timeline"][dest]["time"] = info["timeline"][source]["time"]

def update_priors():
    global prior_count
    global info
    seperation_sec = 10

    if (prior_count * seperation_sec) % 3600 == 0:
        print("Hourly update")
        for hour in range(23, 0, -1):
            oldh = '{:02}'.format(hour)
            newh = '{:02}'.format(hour+1)
            copy_prior(f"prior-{oldh}h.jpg", f"prior-{newh}h.jpg")

        copy_prior("prior-50m.jpg", "prior-01h.jpg")

    if (prior_count * seperation_sec) % 600 == 0:
        print("Ten Minute Update")
        for min in range (40, 0, -10):
            oldm = '{:02}'.format(min)
            newm = '{:02}'.format(min+10)
            copy_prior(f"prior-{oldm}m.jpg", f"prior-{newm}m.jpg")

        copy_prior("prior-09m.jpg", "prior-10m.jpg")

    if (prior_count * seperation_sec) % 60 == 0:
        print("One Minute Update")
        for min in range(8, 0, -1):
            oldm = '{:02}'.format(min)
            newm = '{:02}'.format(min+1)
            copy_prior(f"prior-{oldm}m.jpg", f"prior-{newm}m.jpg")

        copy_prior("prior-50s.jpg", "prior-01m.jpg")

    for sec in range (40, 0, -10):
        olds = '{:02}'.format(sec)
        news = '{:02}'.format(sec+10)
        copy_prior(f"prior-{olds}s.jpg", f"prior-{news}s.jpg")

    copy_prior("prior-00s.jpg", "prior-10s.jpg")
    copy_prior(latest_img_name, "prior-00s.jpg")

    prior_count += 1

    info["total_updates"] = prior_count

    with open(os.path.join(dest_path, info_file), "w") as fout:
        json.dump(info, fout)

def loop():
    while True:
        list_of_files = get_matching_files(source_path, source_img_pattern)
        if list_of_files:
            latest = max(list_of_files, key=os.path.getmtime)
            copy_file(latest, dest_path, latest_img_name)
            cleanup_files(list_of_files)
            update_priors()
        time.sleep(1)

if __name__ == "__main__":
    ensure_output_dir(dest_path)
    generate_viewer(dest_path, title)
    generate_httaccess(dest_path)
    load_existing_info(info_file)

    loop()