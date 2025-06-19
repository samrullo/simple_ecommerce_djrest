import logging
import traceback
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from ecommerce.serializers import ProductSerializer
from ecommerce.serializers.accounting.serializers import JournalEntrySerializer
from decimal import Decimal
from django.db import transaction
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
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


class ProductCreationAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            logger.debug(f"Incoming data : {request.data}")
            with transaction.atomic():
                # Category
                category_name = request.data.get("category_name")
                category, _ = Category.objects.get_or_create(name=category_name)

                # Brand
                brand_name = request.data.get("brand")
                brand = None
                if brand_name:
                    brand, _ = Brand.objects.get_or_create(name=brand_name)

                # Tags
                tags_data = request.data.get("tags", "")
                tag_names = [t.strip() for t in tags_data.split(",") if t.strip()]
                tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]

                # Product
                product = Product.objects.create(
                    name=request.data["name"],
                    description=request.data.get("description", ""),
                    image=request.FILES.get("image"),
                    sku=request.data["sku"],
                    category=category,
                    brand=brand,
                )
                product.tags.set(tags)

                # Price
                price = Decimal(request.data["price"])
                ProductPrice.objects.create(product=product, price=price)

                # Inventory
                quantity = int(request.data.get("stock", 1))
                Inventory.objects.create(product=product, stock=quantity)

                # Accounting
                inventory_account = Account.objects.get(code="1200")  # Inventory
                accounts_payable = Account.objects.get(code="2000")  # Accounts Payable

                journal_entry = JournalEntry.objects.create(
                    description=f"Initial purchase of product: {product.name}"
                )
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=inventory_account,
                    debit=price * quantity,
                    credit=0,
                    description="Inventory increase",
                )
                JournalEntryLine.objects.create(
                    journal_entry=journal_entry,
                    account=accounts_payable,
                    debit=0,
                    credit=price * quantity,
                    description="Accounts Payable",
                )

                return Response(
                    {"message": "Product created", "product_id": product.id},
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            logger.debug("Traceback:", traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProductUpdateAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            with transaction.atomic():
                product = get_object_or_404(Product, pk=pk)

                # --- Basic field updates ---
                product.name = request.data.get("name", product.name)
                product.sku = request.data.get("sku", product.sku)
                product.description = request.data.get("description", product.description)

                # --- Category update ---
                category_name = request.data.get("category_name")
                if category_name:
                    category, _ = Category.objects.get_or_create(name=category_name)
                    product.category = category

                # --- Brand update ---
                brand_name = request.data.get("brand_name")
                if brand_name:
                    brand, _ = Brand.objects.get_or_create(name=brand_name)
                    product.brand = brand

                # --- Tags update ---
                tag_names = [t.strip() for t in request.data.get("tags", "").split(",") if t.strip()]
                if tag_names:
                    tags = [Tag.objects.get_or_create(name=t)[0] for t in tag_names]
                    product.tags.set(tags)

                # --- Image (optional) ---
                if "image" in request.FILES:
                    product.image = request.FILES["image"]

                # updated at now
                product.updated_at=timezone.now()

                product.save()

                # --- Price update ---
                if "price" in request.data:
                    try:
                        new_price = Decimal(request.data["price"])
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

                # --- Stock update + journal ---
                if "stock" in request.data:
                    try:
                        new_quantity = int(request.data["stock"])
                        inventory = Inventory.objects.filter(product=product).first()

                        previous_quantity = inventory.stock if inventory else 0
                        inventory = inventory or Inventory(product=product)
                        inventory.stock = new_quantity
                        inventory.save()

                        quantity_diff = new_quantity - previous_quantity
                        if quantity_diff != 0:
                            unit_price = ProductPrice.objects.filter(product=product, end_date__isnull=True).first()
                            unit_price = unit_price.price if unit_price else Decimal("0")

                            inventory_account = Account.objects.get(code="1200")  # Inventory
                            accounts_payable = Account.objects.get(code="2000")  # Accounts Payable

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
                    except Exception as e:
                        logger.debug(f"Inventory update error: {e}")

                return Response({"message": "Product updated successfully"}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.debug("Traceback:", traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
