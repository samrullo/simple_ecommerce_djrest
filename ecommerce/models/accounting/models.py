from django.db import models


class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ("asset", "Asset"),
        ("liability", "Liability"),
        ("equity", "Equity"),
        ("income", "Income"),
        ("expense", "Expense"),
    ]

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


class JournalEntry(models.Model):
    date = models.DateField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    reference = models.CharField(max_length=100, blank=True)  # e.g., order number

    def __str__(self):
        return f"Journal Entry {self.id} on {self.date}"

    @property
    def is_balanced(self):
        total_debit = sum(line.debit for line in self.lines.all())
        total_credit = sum(line.credit for line in self.lines.all())
        return total_debit == total_credit


class JournalEntryLine(models.Model):
    journal_entry = models.ForeignKey(
        JournalEntry, related_name="lines", on_delete=models.CASCADE
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    credit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.account.name}: Debit {self.debit} / Credit {self.credit}"

    class Meta:
        verbose_name = "Journal Entry Line"
        verbose_name_plural = "Journal Entry Lines"
