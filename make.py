import csv
import json
import os

import requests

scraped_data_file_name = 'data.work.csv'
scrape_to = "./data"


def main():
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
            if row[3]:
                meta["linkedin"] = row[3]
                cnt_li += 1
            if row[4]:
                meta["image"] = row[4]
                cnt_img += 1
            else:
                continue
            if row[5]:
                meta["positions"] = row[5].split("|")
            if row[6]:
                meta["companies"] = row[6].split("|")
            if row[7]:
                meta["links"] = row[7].split("|")

            data.append(meta)

    print("rows: {}, with linkedin profiles: {}, with images: {}".format(cnt, cnt_li, cnt_img))

    for profile in data:
        save_speaker(profile)


def save_speaker(data):
    store_dir = os.path.join(scrape_to, data['name'].replace(" ", "_"))
    if not os.path.isdir(store_dir):
        os.makedirs(store_dir)
    photo_url = data['image']
    r = requests.get(photo_url, stream=True)
    ext = "jpg"
    if "Content-Type" in r.headers:
        ct = r.headers["Content-Type"]
        if ct.startswith("image/"):
            ext = ct[6:]
    img_filename = os.path.join(store_dir, 'image.' + ext)
    with open(img_filename, 'wb') as f:
        for chunk in r.iter_content():
            f.write(chunk)
    del data['image']
    with open(os.path.join(store_dir, 'meta.json'), 'w') as m:
        json.dump(data, m, indent=2)
    print('saved {} with picture and metadata'.format(data['name']))


if __name__ == '__main__':
    main()
