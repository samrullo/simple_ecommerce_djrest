import logging
import os
import pathlib

import django
import pandas as pd
from django.core.files import File

# Set the path to your settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Setup Django
django.setup()

logger = logging.getLogger(__name__)
from ecommerce.models.product.models import Product, ProductImage

data_folder = pathlib.Path(
    r"/Users/samrullo/programming/pyprojects/web_app_projects/simple_ecommerce_djrest/experiments/rakuten_products_preparation/data"
)
product_images_folder = data_folder.parent / "product_images"
prod_image_filename = "products_with_images.csv"
prodimagedf = pd.read_csv(data_folder / prod_image_filename)

for i, row in prodimagedf.iterrows():
    prod_name = row["eng_name"]
    image_filename = row["image_filename"]
    product = Product.objects.filter(name=prod_name).first()
    if not product:
        logger.warning(f"{product} doesn't exist")
        continue
    logger.info(f"Found product matching name {prod_name}")
    product_image = ProductImage.objects.filter(product=product).first()
    image_path = product_images_folder / image_filename
    if not image_path.exists():
        logger.warning(f"{image_filename} doesn't exist")
        continue

    with open(image_path, "rb") as fh:
        if not product_image:
            product_image = ProductImage.objects.create(
                product=product, image=File(fh, name=image_filename), tag="icon"
            )
            logger.info(
                f"Successfully created product image {image_filename} for : {product}"
            )
        else:
            logger.info(f"{prod_name} has product image : {product_image}")
            product_image.image = File(fh, name=image_filename)
            product_image.save()
