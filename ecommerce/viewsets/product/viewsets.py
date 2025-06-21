import logging
import traceback
import pandas as pd
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from ecommerce.serializers import ProductSerializer
from ecommerce.serializers.accounting.serializers import JournalEntrySerializer
from typing import List
from decimal import Decimal
from django.db import transaction
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from sampytools.list_utils import get_list_diff
from ecommerce.permissions import IsStaff
from ecommerce.models import (
    Inventory,
    Account,
    JournalEntry,
    JournalEntryLine,
)
from ecommerce.permissions import IsStaffOrReadOnly

from ecommerce.models import (
    Category,
    Brand,
    Tag,
    Product,
    ProductPrice,
    ProductReview,
    Wishlist,
)
from ecommerce.serializers import (
    CategorySerializer,
    BrandSerializer,
    TagSerializer,
    ProductSerializer,
    ProductPriceSerializer,
    ProductReviewSerializer,
    WishlistSerializer,
)

logger = logging.getLogger(__name__)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.IsAdminUser]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAdminUser]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ProductPriceViewSet(viewsets.ModelViewSet):
    queryset = ProductPrice.objects.all()
    serializer_class = ProductPriceSerializer
    permission_classes = [IsStaffOrReadOnly]


class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAdminUser]


def make_new_product(name, description, category: Category, sku, brand: Brand = None, image=None):
    return Product.objects.create(
        name=name,
        description=description,
        image=image,
        sku=sku,
        category=category,
        brand=brand,
    )


def add_or_update_product(category_name: str,
                          brand_name: str = None,
                          tag_names: List[str] = None,
                          pk: int = None,
                          product_name: str = None,
                          product_description: str = None,
                          product_sku: str = None,
                          product_image=None) -> Product:
    """
    
    :param category_name: 
    :param brand_name: 
    :param tag_names: 
    :param pk: 
    :param product_name: 
    :param product_description: 
    :param product_sku: 
    :param product_image: 
    :return: 
    """""
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
            product.image = product_image
        if brand:
            product.brand = brand
        # updated at now
        product.updated_at = timezone.now()
        product.save()

    else:
        product = make_new_product(product_name, product_description, category, product_sku, brand, product_image)

    # Tags
    if tag_names:
        tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
        product.tags.set(tags)
    return product


def add_or_update_product_price(product: Product, price: str | int | float):
    """
    Create or update product price
    :param product:
    :param price:
    :return:
    """
    try:
        new_price = Decimal(price)
        active_price = ProductPrice.objects.filter(product=product, end_date__isnull=True).first()

        if active_price:
            active_price.price = new_price
            active_price.save()
        else:
            ProductPrice.objects.create(
                product=product,
                price=new_price,
                begin_date=timezone.now().date(),
                end_date=None
            )
    except Exception as e:
        logger.debug(f"Price update error: {e}")


def journal_entries_for_direct_inventory_changes(product: Product,
                                                 new_quantity: int,
                                                 inventory_account_code: str = "1200",
                                                 accounts_payable_account_code: str = "2000") -> Inventory:
    """
    Make journal entries related to direct inventory change.
    When inventory increased it means you purchased products and spent cash
    :param product:
    :param new_quantity:
    :param inventory_account_code:
    :param accounts_payable_account_code:
    :return:
    """
    # get inventory related to this product
    inventory = Inventory.objects.filter(product=product).first()

    # existing inventory of the product before change
    previous_quantity = inventory.stock if inventory else 0
    inventory = inventory or Inventory(product=product)
    inventory.stock = new_quantity
    inventory.save()

    quantity_diff = new_quantity - previous_quantity
    if quantity_diff != 0:
        # simply getting product price
        unit_price = ProductPrice.objects.filter(product=product, end_date__isnull=True).first()
        unit_price = unit_price.price if unit_price else Decimal("0")

        inventory_account = Account.objects.get(code=inventory_account_code)  # Inventory
        accounts_payable = Account.objects.get(code=accounts_payable_account_code)  # Accounts Payable

        # journal entry to record inventory changes. This journal entry will have two JournalEntryLines associated with it
        journal_entry = JournalEntry.objects.create(
            description=f"Inventory adjustment for product: {product.name}"
        )

        delta_value = unit_price * abs(quantity_diff)

        if quantity_diff > 0:
            # Inventory increased (purchase)
            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=inventory_account,
                debit=delta_value,
                credit=0,
                description="Inventory increase"
            )
            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=accounts_payable,
                debit=0,
                credit=delta_value,
                description="Accounts Payable"
            )
        else:
            # Inventory decreased (write-off or sale adjustment)
            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=inventory_account,
                debit=0,
                credit=delta_value,
                description="Inventory decrease"
            )
            JournalEntryLine.objects.create(
                journal_entry=journal_entry,
                account=accounts_payable,
                debit=delta_value,
                credit=0,
                description="Reversal from Accounts Payable"
            )
    return inventory


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
                            name : {request.data.get('name')},
                            description : {request.data.get('description')},
                            sku : {request.data.get('sku')},
                            image : {request.data.get('image')}
                            """)
                product = add_or_update_product(category_name,
                                                brand_name,
                                                tag_names,
                                                product_name=request.data.get("name"),
                                                product_description=request.data.get("description", ""),
                                                product_sku=request.data.get("sku"),
                                                product_image=request.data.get("image"))
                # Price
                add_or_update_product_price(product, request.data.get("price"))

                # Inventory
                quantity = int(request.data.get("stock", 1))
                journal_entries_for_direct_inventory_changes(product, quantity, "1200", "2000")
                return Response(
                    {"message": "Product created", "product_id": product.id},
                    status=status.HTTP_201_CREATED,
                )
        except Exception as e:
            logger.debug("Traceback:", traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProductUpdateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsStaff]

    def put(self, request, pk):
        try:
            with transaction.atomic():
                tag_names = [t.strip() for t in request.data.get("tags", "").split(",") if t.strip()]
                logger.debug(f"""Passing category_name : {request.data.get('category_name')},
                brand_name : {request.data.get('brand_name')},
                tag_names : {tag_names},
                pk : {pk},
                name : {request.data.get('name')},
                description : {request.data.get('description')},
                sku : {request.data.get('sku')},
                product_image : {request.FILES.get('image')}
                                """)
                product = add_or_update_product(request.data.get("category_name"),
                                                request.data.get("brand_name"),
                                                tag_names,
                                                pk,
                                                request.data.get("name"),
                                                request.data.get("description"),
                                                request.data.get("sku"),
                                                product_image=request.FILES.get("image"))

                # --- Price update ---
                if "price" in request.data:
                    add_or_update_product_price(product, request.data.get("price"))
                # --- Stock update + journal ---
                if "stock" in request.data:
                    try:
                        new_quantity = int(request.data["stock"])
                        journal_entries_for_direct_inventory_changes(product, new_quantity, "1200", "2000")
                    except Exception as e:
                        logger.debug(f"Inventory update error: {e}")

                return Response({"message": "Product updated successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.debug("Traceback:", traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProductCreateUpdateFromCSVAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permissions = [IsStaff]

    def post(self, request):
        try:
            file_obj = request.FILES.get("file")
            if not file_obj:
                return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
            df = pd.read_csv(file_obj)
            required_cols = ["product_name", "category_name", "price", "stock"]
            missing_cols = get_list_diff(required_cols, df.columns)
            if len(missing_cols) > 0:
                return Response({"error": f"Product Create and Update CSV file is missing columns : {missing_cols}"},
                                status=status.HTTP_400_BAD_REQUEST)

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
                    existing_product = Product.objects.filter(name__iexact=row["product_name"]).first()
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
                    product = add_or_update_product(row["category_name"], brand_name, tag_names, pk,
                                                    row["product_name"], description, sku)
                    add_or_update_product_price(product, row["price"])
                    journal_entries_for_direct_inventory_changes(product, row["stock"], "1200", "2000")
                logger.debug(
                    f"Finished creating or updating product with name : {row['product_name']}, category_name : {row['category_name']},brand_name : {brand_name}, tag_names : {tag_names}, price :{row['price']}, stock : {row['stock']}")
            return Response({"message": f"Successfully created or updated {len(df)} products"},
                            status=status.HTTP_200_OK)
        except Exception as e:
            logger.debug("Traceback:", traceback.format_exc())
            return Response({"error": f"Product create or update from csv failed : {e}"},
                            status=status.HTTP_400_BAD_REQUEST)
