import csv
import json
import os
import sys

import requests

scraped_data_file_name = 'data.linkedin.scraped.csv'
save_to_dir = "../data"
overwrite_image = False


def main():
    global save_to_dir

    if len(sys.argv) < 2:
        print("usage: %s <save-to-dir> [additional_meta...]" % sys.argv[0])
        exit(1)
    save_to_dir = sys.argv[1]

    additional = []
    if len(sys.argv) > 2:
        additional = sys.argv[2:]

    data = []
    cnt = 0
    cnt_li = 0
    cnt_img = 0
    with open(scraped_data_file_name, mode='r') as r:
        csv_data = csv.reader(r, delimiter=';')
        next(csv_data)  # read header
        for row in csv_data:
            cnt += 1
            meta = {"name": row[0]}
            if row[1]:
                meta["position"] = row[1]
            if row[2]:
                meta["company"] = row[2]
            i = 3
            for a in additional:
                meta[a] = row[i]
                i += 1
            if row[i]:
                meta["linkedin"] = row[i]
                cnt_li += 1
            if row[i + 1]:
                meta["image"] = row[i + 1]
                cnt_img += 1
            else:
                continue
            if row[i + 2]:
                meta["positions"] = row[i + 2].split("|")
            if row[i + 3]:
                meta["companies"] = row[i + 3].split("|")
            if row[i + 4]:
                meta["links"] = row[i + 4].split("|")
            if row[i + 5]:
                meta["bio"] = row[i + 5]

            data.append(meta)

    print("rows: {}, with linkedin profiles: {}, with images: {}".format(cnt, cnt_li, cnt_img))

    cnt = 1
    for profile in data:
        save_speaker(profile, cnt=cnt)
        cnt += 1


def save_speaker(data, cnt=0):
    store_dir = os.path.join(save_to_dir, data['name'].replace(" ", "_"))
    if not os.path.isdir(store_dir):
        os.makedirs(store_dir)
    photo_url = data['image']
    # r = requests.options(photo_url, stream=True)
    # ext = "jpg"
    # if "Content-Type" in r.headers:
    #     ct = r.headers["Content-Type"]
    #     if ct.startswith("image/"):
    #         ext = ct[6:]
    # img_filename = os.path.join(store_dir, 'linkedin.' + ext)
    img_filename = os.path.join(store_dir, 'linkedin.jpg')
    write_image = True
    if os.path.exists(img_filename):
        write_image = overwrite_image
        if overwrite_image:
            os.remove(img_filename)
    if write_image:
        r = requests.get(photo_url, stream=True)
        with open(img_filename, 'wb') as f:
            for chunk in r.iter_content():
                f.write(chunk)
    del data['image']
    meta_filename = os.path.join(store_dir, 'meta.json')
    if os.path.exists(meta_filename):
        with open(meta_filename, 'r') as r:
            loaded_data = json.load(r)
            for k in loaded_data:
                if k not in data:
                    data[k] = loaded_data[k]
    with open(meta_filename, 'w') as m:
        json.dump(data, m, indent=2)
    print('{}. saved {} {} picture'.format(cnt, data['name'], 'with' if write_image else 'without'))


if __name__ == '__main__':
    main()
