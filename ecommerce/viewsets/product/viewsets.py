import logging
import traceback
import pandas as pd
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from typing import List
from decimal import Decimal
from django.db import transaction
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from sampytools.list_utils import get_list_diff
from ecommerce.permissions import IsStaff
from ecommerce.permissions import IsStaffOrReadOnly

from ecommerce.models import (
    Category,
    Brand,
    Tag,
    Product,
    ProductImage,
    ProductPrice,
    ProductReview,
    Wishlist,
)
from ecommerce.models.product.models import Currency, FXRate
from ecommerce.serializers.product.serializers import (
    CurrencySerializer,
    FXRateSerializer,
)
from ecommerce.serializers import (
    CategorySerializer,
    BrandSerializer,
    TagSerializer,
    ProductSerializer,
    ProductImageSerializer,
    ProductPriceSerializer,
    ProductReviewSerializer,
    WishlistSerializer,
)
from ecommerce.viewsets.accounting.viewsets import (
    journal_entries_for_direct_inventory_changes,
)

logger = logging.getLogger(__name__)


class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsStaffOrReadOnly]


class FXRateViewSet(viewsets.ModelViewSet):
    queryset = FXRate.objects.all()
    serializer_class = FXRateSerializer
    permission_classes = [IsStaffOrReadOnly]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsStaff]


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsStaff]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsStaff]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsStaffOrReadOnly]


# views.py

from rest_framework.generics import ListAPIView
from ecommerce.models.product.models import Product
from ecommerce.serializers.product.serializers import ProductWithImageSerializer


class ProductWithImageListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductWithImageSerializer


class ProductImageViewset(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsStaffOrReadOnly]


class ProductPriceViewSet(viewsets.ModelViewSet):
    queryset = ProductPrice.objects.all()
    serializer_class = ProductPriceSerializer
    permission_classes = [IsStaffOrReadOnly]


class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [IsStaffOrReadOnly]


class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsStaffOrReadOnly]


def make_new_product(
    name, description, category: Category, sku, brand: Brand = None, product_image=None
) -> Product:
    """
    Make new product
    :param name:
    :param description:
    :param category:
    :param sku:
    :param brand:
    :param product_image:
    :return:
    """
    product = Product.objects.create(
        name=name,
        description=description,
        sku=sku,
        category=category,
        brand=brand,
    )
    ProductImage.objects.create(product=product, image=product_image, tag="icon")
    return product


def add_or_update_product(
    category_name: str,
    brand_name: str = None,
    tag_names: List[str] = None,
    pk: int = None,
    product_name: str = None,
    product_description: str = None,
    product_sku: str = None,
    product_image=None,
) -> Product:
    """
    Add or update product
    :param category_name:
    :param brand_name:
    :param tag_names:
    :param pk:
    :param product_name:
    :param product_description:
    :param product_sku:
    :param product_image:
    :return:
    """
    # category
    category, _ = Category.objects.get_or_create(name=category_name)

    # Brand
    brand = None
    if brand_name:
        brand, _ = Brand.objects.get_or_create(name=brand_name)

    if pk is not None:
        # update existing product
        product = get_object_or_404(Product, pk=pk)
        if product_name:
            product.name = product_name
        if product_description:
            product.description = product_description
        if product_sku:
            product.sku = product_sku
        if product_image:
            product_image_obj = ProductImage.objects.filter(
                product=product, tag="icon"
            ).first()
            if product_image_obj is None:
                ProductImage.objects.create(
                    product=product, tag="icon", image=product_image
                )
            else:
                product_image_obj.image = product_image
                product_image_obj.save()
                logger.debug(f"Uploaded to: {product_image_obj.image.name}" )
                logger.debug(f"Accessible at: {product_image_obj.image.url}")
        if category:
            product.category = category
        if brand:
            product.brand = brand
        # updated at now
        product.updated_at = timezone.now()
        product.save()

    else:
        product = make_new_product(
            product_name,
            product_description,
            category,
            product_sku,
            brand,
            product_image,
        )

    # Tags
    if tag_names:
        tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
        product.tags.set(tags)
    return product


def add_or_update_product_price(
    product: Product, price: str | int | float, currency_code: str
):
    """
    Create or update product price
    :param product:
    :param price:
    :param currency_code: price currency
    :return:
    """
    try:
        currency_obj = Currency.objects.filter(code=currency_code).first()
        new_price = Decimal(price)
        active_price = ProductPrice.objects.filter(
            product=product, end_date__isnull=True
        ).first()

        if active_price:
            active_price.price = new_price
            active_price.currency = currency_obj
            active_price.save()
        else:
            ProductPrice.objects.create(
                product=product,
                price=new_price,
                currency=currency_obj,
                begin_date=timezone.now().date(),
                end_date=None,
            )
    except Exception as e:
        logger.debug(f"Price update error: {e}")


class ProductCreationAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsStaff]

    def post(self, request):
        try:
            logger.debug(f"Incoming data : {request.data}")
            with transaction.atomic():
                # Category
                category_name = request.data.get("category_name")
                brand_name = request.data.get("brand_name")
                # Tags
                tags_data = request.data.get("tags", "")
                tag_names = [t.strip() for t in tags_data.split(",") if t.strip()]
                logger.debug(f"""Creating new product:
                            category_name : {category_name},
                            brand_name : {brand_name},
                            tag_names : {tag_names},
                            name : {request.data.get("name")},
                            description : {request.data.get("description")},
                            sku : {request.data.get("sku")},
                            image : {request.data.get("image")}
                            """)
                product = add_or_update_product(
                    category_name,
                    brand_name,
                    tag_names,
                    product_name=request.data.get("name"),
                    product_description=request.data.get("description", ""),
                    product_sku=request.data.get("sku"),
                    product_image=request.data.get("image"),
                )
                # Price
                add_or_update_product_price(
                    product, request.data.get("price"), request.data.get("currency")
                )

                # Inventory
                quantity = int(request.data.get("stock", 1))
                journal_entries_for_direct_inventory_changes(
                    product, quantity, "1200", "2000"
                )
                return Response(
                    {"message": "Product created", "product_id": product.id},
                    status=status.HTTP_201_CREATED,
                )
        except Exception as e:
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProductUpdateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsStaff]

    def put(self, request, pk):
        try:
            with transaction.atomic():
                tag_names = [
                    t.strip()
                    for t in request.data.get("tags", "").split(",")
                    if t.strip()
                ]
                logger.debug(f"""Passing category_name : {request.data.get("category_name")},
                brand_name : {request.data.get("brand_name")},
                tag_names : {tag_names},
                pk : {pk},
                name : {request.data.get("name")},
                description : {request.data.get("description")},
                sku : {request.data.get("sku")},
                product_image : {request.FILES.get("image")}
                                """)
                product = add_or_update_product(
                    request.data.get("category_name"),
                    request.data.get("brand_name"),
                    tag_names,
                    pk,
                    request.data.get("name"),
                    request.data.get("description"),
                    request.data.get("sku"),
                    product_image=request.FILES.get("image"),
                )

                # --- Price update ---
                if "price" in request.data:
                    add_or_update_product_price(
                        product, request.data.get("price"), request.data.get("currency")
                    )
                # --- Stock update + journal ---
                if "stock" in request.data:
                    try:
                        new_quantity = int(request.data["stock"])
                        journal_entries_for_direct_inventory_changes(
                            product, new_quantity, "1200", "2000"
                        )
                    except Exception as e:
                        logger.debug(f"Inventory update error: {e}")

                return Response(
                    {"message": "Product updated successfully"},
                    status=status.HTTP_200_OK,
                )
        except Exception as e:
            logger.debug(f"Traceback: {traceback.format_exc()}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProductCreateUpdateFromCSVAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permissions = [IsStaff]

    def post(self, request):
        try:
            file_obj = request.FILES.get("file")
            if not file_obj:
                return Response(
                    {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
                )
            df = pd.read_csv(file_obj)
            required_cols = ["product_name", "category_name", "price", "stock"]
            missing_cols = get_list_diff(required_cols, df.columns)
            if len(missing_cols) > 0:
                return Response(
                    {
                        "error": f"Product Create and Update CSV file is missing columns : {missing_cols}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            for i, row in df.iterrows():
                with transaction.atomic():
                    if "tag_names" in df.columns and row["tag_names"] != "":
                        tag_names = [t.strip() for t in row["tag_names"].split(",")]
                    else:
                        tag_names = None

                    if "brand_name" in df.columns and row["brand_name"] != "":
                        brand_name = row["brand_name"]
                    else:
                        brand_name = None
                    existing_product = Product.objects.filter(
                        name__iexact=row["product_name"]
                    ).first()
                    if existing_product:
                        pk = existing_product.pk
                    else:
                        pk = None
                    if "description" in df.columns and row["description"] != "":
                        description = row["description"]
                    elif existing_product:
                        description = existing_product.description
                    else:
                        description = row["product_name"]

                    if "sku" in df.columns and row["sku"] != "":
                        sku = row["sku"]
                    elif existing_product:
                        sku = existing_product.sku
                    else:
                        sku = row["product_name"].upper()
                    product = add_or_update_product(
                        row["category_name"],
                        brand_name,
                        tag_names,
                        pk,
                        row["product_name"],
                        description,
                        sku,
                    )
                    currency_code = row.get("currency")
                    currency_code = (
                        currency_code
                        if pd.notna(currency_code)
                        else settings.ACCOUNTING_CURRENCY
                    )
                    add_or_update_product_price(product, row["price"], currency_code)
                    journal_entries_for_direct_inventory_changes(
                        product, row["stock"], "1200", "2000"
                    )
                logger.debug(
                    f"Finished creating or updating product with name : {row['product_name']}, category_name : {row['category_name']},brand_name : {brand_name}, tag_names : {tag_names}, price :{row['price']}, stock : {row['stock']}"
                )
            return Response(
                {"message": f"Successfully created or updated {len(df)} products"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.debug(f"Traceback:{traceback.format_exc()}")
            return Response(
                {"error": f"Product create or update from csv failed : {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
