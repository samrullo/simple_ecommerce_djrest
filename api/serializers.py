from rest_framework import serializers


class DummyProduct:
    def __init__(self, name: str, description: str, price: float):
        self.name = name
        self.description = description
        self.price = price


class DummyProductSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=500)
    price = serializers.FloatField()
