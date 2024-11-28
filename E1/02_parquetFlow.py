#!/usr/bin/env python

import math
import sys
import pyarrow.parquet as pq
import pandas as pd
import os
import io
from PIL import Image
from tqdm import tqdm

write_img = True
if len(sys.argv) > 1 and sys.argv[1]:
    write_img = False

print("write_img", write_img)

name = 'product_eval'
base_data_path = './data/'
csv_file = f'{base_data_path}{name}.csv'
path_images = f'{base_data_path}images'
if os.path.isfile(f'{base_data_path}{name}.json') is False:
    print('**** Pas de fichiers parquet ****')
    exit(0)

json = pd.read_json(f'{base_data_path}{name}.json')
glob = list(json.iloc[:, 0])
batch_size = 10

# exit()

os.makedirs(path_images, exist_ok=True)

if os.path.isfile(csv_file):
    os.remove(csv_file)


def convert_img(row):
    img_path = os.path.join(path_images, f"{row['item_ID']}.jpg")
    image = Image.open(io.BytesIO(row['image']['bytes']))
    row['image'] = img_path
    if write_img:
        rgb_im = image.convert('RGB')
        rgb_im.save(img_path, 'jpeg')

for parquet_file in tqdm(glob):
    df = None
    parquet_file = pq.ParquetFile(f'{base_data_path}{parquet_file}')
    total = parquet_file.metadata.num_rows

    for record_batch in tqdm(parquet_file.iter_batches(batch_size=batch_size, columns=['image', 'item_ID', 'title']), total=math.ceil(total / batch_size)):
        batch = record_batch.to_pandas()
        batch.apply(convert_img, axis=1)

        if df is None:
            df = batch
        else:
            df = pd.concat([df, batch])

    df.to_csv(path_or_buf=csv_file, index=False, mode='a')

print(f"**** SAVE CSV in {csv_file} ****")