import os
import pyarrow.parquet as pq
import io
from PIL import Image

dir_path = os.path.dirname(os.path.realpath(__file__))
print(f'{dir_path}/data/product_eval/test-00000-of-00003.parquet')
destination = f'{dir_path}/data/images/'

parquet_file = pq.ParquetFile(f'{dir_path}/data/product_eval/test-00000-of-00003.parquet')

for i in parquet_file.iter_batches(2):
    df_parquet = i.to_pandas()
    break

def convert_image(x):
    img = dict(x['image'])
    image = Image.open(io.BytesIO(img['bytes']))
    image.save(f'{destination}{x['item_ID']}.jpg', 'jpeg')

df_parquet.apply(convert_image, axis=1)