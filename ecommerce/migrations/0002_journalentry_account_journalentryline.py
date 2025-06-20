# Generated by Django 5.1.6 on 2025-06-09 11:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('reference', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('account_type', models.CharField(choices=[('asset', 'Asset'), ('liability', 'Liability'), ('equity', 'Equity'), ('income', 'Income'), ('expense', 'Expense')], max_length=20)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='ecommerce.account')),
            ],
        ),
        migrations.CreateModel(
            name='JournalEntryLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('debit', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('credit', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ecommerce.account')),
                ('journal_entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='ecommerce.journalentry')),
            ],
            options={
                'verbose_name': 'Journal Entry Line',
                'verbose_name_plural': 'Journal Entry Lines',
            },
        ),
    ]
