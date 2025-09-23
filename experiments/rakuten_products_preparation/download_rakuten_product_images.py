import logging
import pathlib

import pandas as pd
import requests
from sampytools.logging_utils import init_logging
from sampytools.pandas_utils import create_new_col_based_on_dict
from sampytools.text_utils import extract_words_from_text_and_join_with_char
from tqdm import tqdm

init_logging(level=logging.INFO)


data_folder = pathlib.Path(
    r"/Users/samrullo/programming/pyprojects/web_app_projects/simple_ecommerce_djrest/experiments/rakuten_products_preparation/data"
)
product_images_folder = data_folder.parent / "product_images"
filename = "rakuten_all_concat_on_20221213.csv"
product_translations_filename = "product_names_translations.csv"

productdf = pd.read_csv(data_folder / filename)
logging.info(f"There are {len(productdf)} records")

transdf = pd.read_csv(data_folder / product_translations_filename)
logging.info(f"There are {len(transdf)} records in translations file")

productdf = create_new_col_based_on_dict(
    productdf,
    "name",
    "eng_name",
    {
        name: translation
        for name, translation in zip(transdf["product_name"], transdf["translation"])
    },
)

engproductdf = productdf[["eng_name", "image"]].copy()
engproductdf = engproductdf.drop_duplicates("eng_name")

with tqdm(total=len(engproductdf), desc="Download images") as pbar:
    for i, row in engproductdf.iterrows():
        image_filename = (
            extract_words_from_text_and_join_with_char(row["eng_name"]) + ".jpg"
        )
        image_url = row["image"]
        response = requests.get(image_url)
        (product_images_folder / image_filename).write_bytes(response.content)
        engproductdf.loc[i, "image_filename"] = image_filename
        pbar.update(1)

eng_products_filename = "products_with_images.csv"
engproductdf.to_csv(data_folder / eng_products_filename, index=False)
