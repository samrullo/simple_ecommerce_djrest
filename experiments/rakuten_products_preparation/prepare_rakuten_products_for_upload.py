import logging
import pathlib
import pandas as pd
from sampytools.logging_utils import init_logging
from sampytools.pandas_utils import create_new_col_based_on_dict

init_logging(level=logging.INFO)

data_folder = pathlib.Path(
    r"/Users/samrullo/programming/pyprojects/web_app_projects/simple_ecommerce_djrest/experiments/rakuten_products_preparation/data"
)
product_images_folder = data_folder.parent / "product_images"
filename = "rakuten_all_concat_on_20221213.csv"
product_translations_filename = "product_names_translations.csv"
product_categories_filename = "product_categories.csv"

productdf = pd.read_csv(data_folder / filename)
logging.info(f"There are {len(productdf)} records")

transdf = pd.read_csv(data_folder / product_translations_filename)
logging.info(f"There are {len(transdf)} records in translations file")

# prodcatdf = pd.read_csv(data_folder / product_categories_filename)
from sampytools.text_utils import get_delimited_records_from_file

category_records = get_delimited_records_from_file(
    data_folder / product_categories_filename, ","
)
for idx, record in enumerate(category_records):
    if len(record) > 2:
        product_category = record[-1]
        product_name = ",".join(record[:-2])
        logging.info(f"product_name : {product_name}, category : {product_category}")
        category_records[idx] = [product_name, product_category]
prodcatdf = pd.DataFrame(
    {
        "product_name": [record[0] for record in category_records],
        "category": [record[1] for record in category_records],
    }
)

logging.info(f"There are {len(prodcatdf)} records in product categories filename")

productdf = create_new_col_based_on_dict(
    productdf,
    "name",
    "eng_name",
    {
        name: translation
        for name, translation in zip(transdf["product_name"], transdf["translation"])
    },
)
uploaddf = productdf[["eng_name", "price", "quantity"]].copy()
uploaddf = uploaddf.rename(columns={"eng_name": "product_name", "quantity": "stock"})
product_name_to_category = {
    name: category
    for name, category in zip(prodcatdf["product_name"], prodcatdf["category"])
}
uploaddf = create_new_col_based_on_dict(
    uploaddf, "product_name", "category_name", product_name_to_category
)
upload_filename = "rakuten_products_for_upload.csv"
uploaddf.to_csv(data_folder / upload_filename, index=False)
logging.info(f"Saved rakuten for upload file to {data_folder / upload_filename}")
