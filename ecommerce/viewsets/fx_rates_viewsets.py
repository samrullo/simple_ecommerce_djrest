import logging
import traceback
import pandas as pd
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, cache_control
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from typing import List
from decimal import Decimal
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.parsers import JSONParser
from ecommerce.permissions import IsStaff
from ecommerce.models.product.models import FXRate, Currency
from ecommerce.serializers.product.serializers import FXRateSerializer

logger = logging.getLogger(__name__)


def calculate_and_save_ccy_to_other_ccy_fx_rate(ccy: Currency, other_ccy: Currency, primary_ccy: Currency,
                                                fx_rate_against_primary_ccy: float) -> FXRate:
    """
    Update FX rate ccy to other ccy given primary ccy and against primary ccy fx rate
    :param ccy:
    :param other_ccy:
    :param primary_ccy:
    :param fx_rate_against_primary_ccy:
    :return:
    """
    other_ccy_to_primary_ccy_fx_rate = FXRate.objects.filter(currency_from=primary_ccy,
                                                             currency_to=other_ccy,
                                                             end_date__isnull=True).first()
    active_fx_rate = FXRate.objects.filter(currency_from=ccy,
                                           currency_to=other_ccy,
                                           end_date__isnull=True).first()
    if active_fx_rate:
        active_fx_rate.end_date = timezone.now().date()
        active_fx_rate.save()

    # create new fx rate
    ccy_to_other_ccy_fx_rate_val = other_ccy_to_primary_ccy_fx_rate.rate / fx_rate_against_primary_ccy
    new_fx_rate = FXRate.objects.create(currency_from=ccy,
                                        currency_to=other_ccy,
                                        rate=Decimal(ccy_to_other_ccy_fx_rate_val),
                                        start_date=timezone.now().date())
    logger.debug(f"Created new fx rate {new_fx_rate}")
    return new_fx_rate


def add_or_update_fx_rates_against_non_primary_currency(fx_rate_against_primary: FXRate):
    """
    Update fx rates of other currencies against the currency updated
    :param fx_rate_against_primary:
    :return:
    """
    primary_currency = fx_rate_against_primary.currency_from
    currency_to_update = fx_rate_against_primary.currency_to
    currency_from_id = fx_rate_against_primary.currency_from.id
    currency_to_id = fx_rate_against_primary.currency_to.id
    other_currencies = Currency.objects.exclude(Q(id=currency_from_id) | Q(id=currency_to_id))
    for other_currency in other_currencies:
        ccy_to_other_ccy_fx_rate = calculate_and_save_ccy_to_other_ccy_fx_rate(currency_to_update, other_currency,
                                                                               primary_currency,
                                                                               fx_rate_against_primary.rate)
        logger.debug(f"Created {ccy_to_other_ccy_fx_rate}")

        other_ccy_to_primary_ccy_fx_rate = FXRate.objects.filter(currency_from=primary_currency,
                                                                 currency_to=other_currency,
                                                                 end_date__isnull=True).first()
        other_ccy_to_ccy_fx_rate = calculate_and_save_ccy_to_other_ccy_fx_rate(other_currency, currency_to_update,
                                                                               primary_currency,
                                                                               other_ccy_to_primary_ccy_fx_rate.rate)
        logger.debug(f"Created {other_ccy_to_ccy_fx_rate}")


def create_fx_rate_given_new_rate(currency_from: Currency, currency_to: Currency, new_fx_rate: float,
                                  fx_rate_source: str = "FXRATESOURCE"):
    active_fx_rate = FXRate.objects.filter(currency_from=currency_from,
                                           currency_to=currency_to,
                                           end_date__isnull=True).first()
    if active_fx_rate:
        active_fx_rate.end_date = timezone.now().date()
        active_fx_rate.save()
    new_fx_rate_obj = FXRate.objects.create(currency_from=currency_from,
                                            currency_to=currency_to,
                                            rate=Decimal(new_fx_rate),
                                            start_date=timezone.now().date(),
                                            source=fx_rate_source)
    logger.debug(f"Created new fx rate {new_fx_rate_obj}")
    return new_fx_rate_obj


def create_or_udpate_fx_rate_given_against_primary_ccy_rate(fx_rate_data: dict):
    # we expect currency_from_id, currency_to_id, rate, source to be present in fx_rate_data
    currency_from = Currency.objects.get(
        id=fx_rate_data["currency_from_id"])  # this is expected to match primary currency
    currency_to = Currency.objects.get(id=fx_rate_data["currency_to_id"])
    new_against_primary_ccy_rate = create_fx_rate_given_new_rate(currency_from, currency_to,
                                                                 float(fx_rate_data.get("rate")))
    add_or_update_fx_rates_against_non_primary_currency(new_against_primary_ccy_rate)

    # also save currency to primary currency rate which is simple the reverse of specified rate in fx_rate_data
    ccy_to_primary_rate = 1 / float(fx_rate_data.get("rate"))
    create_fx_rate_given_new_rate(currency_to, currency_from, ccy_to_primary_rate)
    return new_against_primary_ccy_rate


class FXRateCreateUpdateAPIView(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsStaff]

    def post(self, request):
        try:
            logger.debug(f"Incoming data for fx rate update : {request.data}")
            new_fx_rate = create_or_udpate_fx_rate_given_against_primary_ccy_rate(request.data)
            return Response({"message": f"Successfully created {new_fx_rate}"})
        except Exception as e:
            logger.debug(f"Error happened when updating fx rate : {e}")
            return Response({"error": f"Error when updating fx rate {e}"}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            new_fx_rate = create_or_udpate_fx_rate_given_against_primary_ccy_rate(request.data)
            return Response({"message": f"Successfully created {new_fx_rate}"})
        except Exception as e:
            logger.debug(f"Error happened when updating fx rate : {e}")
            return Response({"error": f"Error when updating fx rate {e}"}, status=status.HTTP_400_BAD_REQUEST)


class FxRateAgainstPrimaryCcyListView(ListAPIView):
    serializer_class = FXRateSerializer

    def get_queryset(self):
        primary_currency_code = settings.PRIMARY_FXRATE_CURRENCY
        primary_currency = Currency.objects.filter(code=primary_currency_code).first()
        fx_rates_queryset = FXRate.objects.filter(currency_from=primary_currency, end_date__isnull=True).exclude(
            currency_to=primary_currency)
        return fx_rates_queryset.select_related("currency_from", "currency_to")


class ActiveFXRatesListView(ListAPIView):
    serializer_class = FXRateSerializer

    def get_queryset(self):
        return FXRate.objects.filter(end_date__isnull=True)
