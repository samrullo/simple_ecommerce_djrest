import logging
import pathlib

import pandas as pd
from sampytools.list_utils import get_list_diff
from sampytools.logging_utils import init_logging
from sampytools.pandas_utils import (
    convert_columns_to_lowercase_and_nowhitespace,
    create_new_col_based_on_dict,
)

init_logging(level=logging.INFO)

data_folder = pathlib.Path(
    r"/Users/samrullo/programming/pyprojects/web_app_projects/simple_ecommerce_djrest/experiments/rakuten_products_preparation/data"
)

product_categories_filename = "product_categories.csv"
category_mapping_filename = "category_mapping.csv"

pcdf = pd.read_csv(data_folder / product_categories_filename)
cmdf = pd.read_csv(data_folder / category_mapping_filename)
cmdf = convert_columns_to_lowercase_and_nowhitespace(cmdf)

print(f"category mapping records : {len(cmdf)}")
orig_categories = pcdf["category"].unique().tolist()
unmapped_orig_categories = get_list_diff(
    orig_categories, cmdf["original_category"].unique()
)
logging.info(f"Number of new categories : {cmdf['mapped_category'].nunique()}")
logging.info(
    f"Unmapped original categories {len(unmapped_orig_categories)} : {unmapped_orig_categories}"
)

pcdf = pcdf.rename(columns={"category": "old_category"})
old_to_new_category_mapping = {
    old_cat: new_cat
    for old_cat, new_cat in zip(cmdf["original_category"], cmdf["mapped_category"])
}
pcdf = create_new_col_based_on_dict(
    pcdf, "old_category", "category", old_to_new_category_mapping
)
pcdf = pcdf.drop("old_category", axis=1)
new_product_category_filename = "product_categories2.csv"
pcdf.to_csv(data_folder / new_product_category_filename, index=False)
logging.info(
    f"Saved product categories with {pcdf['category'].nunique()} new categories to {data_folder / new_product_category_filename}"
)
