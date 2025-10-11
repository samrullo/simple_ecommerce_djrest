from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from ecommerce.models import FXRate
from ecommerce.models.audit_mixin import AuditMixin
from ecommerce.models.product.models import Currency
from ecommerce.serializers.product.serializers import CurrencySerializer
from ecommerce.permissions import IsStaff


class SpendingName(AuditMixin):
    """
    Defines a spending category (e.g., Travel, Office Supplies).
    """

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Spending(AuditMixin):
    """
    Records an actual spending instance.
    """

    spending_name = models.ForeignKey(
        SpendingName, on_delete=models.CASCADE, related_name="spendings"
    )
    adate = models.DateField(default=timezone.now)  # date of spending
    amount = models.FloatField()
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return (
            f"{self.spending_name.name}: {self.amount} {self.currency} on {self.adate}"
        )


class SpendingNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpendingName
        fields = "__all__"


class SpendingSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.PrimaryKeyRelatedField(
        source="currency", queryset=Currency.objects.all(), write_only=True
    )

    class Meta:
        model = Spending
        fields = [
            "id",
            "spending_name",
            "adate",
            "amount",
            "currency",
            "currency_id",
            "created_at",
            "modified_at",
            "modified_by",
        ]


class SpendingNameViewSet(ModelViewSet):
    queryset = SpendingName.objects.all()
    serializer_class = SpendingNameSerializer


class SpendingViewSet(ModelViewSet):
    permission_classes = [IsStaff]
    serializer_class = SpendingSerializer

    def get_queryset(self):
        queryset = Spending.objects.all().select_related("spending_name", "currency").order_by("-adate")
        start_date=self.request.query_params.get("start_date")
        end_date=self.request.query_params.get("end_date")

        if start_date:
            start_date=parse_date(start_date)
            if start_date:
                queryset=queryset.filter(adate__gte=start_date)
        if end_date:
            end_date=parse_date(end_date)
            if end_date:
                queryset=queryset.filter(adate__lte=end_date)
        return queryset

class SpendingTotalInAccountingCurrencyView(APIView):
    permission_classes = [IsStaff]

    def get(self, request, *args, **kwargs):
        start_date = parse_date(request.query_params.get("start_date"))
        end_date = parse_date(request.query_params.get("end_date"))

        queryset = Spending.objects.select_related("currency")

        if start_date:
            queryset = queryset.filter(adate__gte=start_date)
        if end_date:
            queryset = queryset.filter(adate__lte=end_date)

        fx_rates = FXRate.objects.filter(
            end_date__isnull=True,
            currency_to__code=settings.ACCOUNTING_CURRENCY
        ).select_related("currency_from", "currency_to")

        fx_map = {
            (fx.currency_from.code, fx.currency_to.code): Decimal(fx.rate)
            for fx in fx_rates
        }

        total = Decimal("0.00")
        for s in queryset:
            from_code = s.currency.code if s.currency else None
            to_code = settings.ACCOUNTING_CURRENCY
            rate = fx_map.get((from_code, to_code), Decimal("1.0") if from_code == to_code else None)

            if rate is None:
                continue  # skip if FX rate not available
            total += Decimal(s.amount) * rate

        return Response({
            "amount": round(total, 2),
            "currency": settings.ACCOUNTING_CURRENCY,
        })