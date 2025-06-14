from rest_framework import serializers
from ecommerce.models.accounting.models import Account, JournalEntry, JournalEntryLine


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "name", "code", "account_type", "parent"]


class JournalEntryLineSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)
    account_id = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(), source="account", write_only=True
    )

    class Meta:
        model = JournalEntryLine
        fields = [
            "id",
            "account",
            "account_id",
            "debit",
            "credit",
            "description",
        ]


class JournalEntrySerializer(serializers.ModelSerializer):
    lines = JournalEntryLineSerializer(many=True)

    class Meta:
        model = JournalEntry
        fields = [
            "id",
            "date",
            "description",
            "reference",
            "lines",
        ]

    def create(self, validated_data):
        lines_data = validated_data.pop("lines")
        journal_entry = JournalEntry.objects.create(**validated_data)
        for line_data in lines_data:
            JournalEntryLine.objects.create(journal_entry=journal_entry, **line_data)
        return journal_entry

    def update(self, instance, validated_data):
        lines_data = validated_data.pop("lines", None)
        instance.description = validated_data.get("description", instance.description)
        instance.reference = validated_data.get("reference", instance.reference)
        instance.save()

        if lines_data is not None:
            instance.lines.all().delete()
            for line_data in lines_data:
                JournalEntryLine.objects.create(journal_entry=instance, **line_data)

        return instance
