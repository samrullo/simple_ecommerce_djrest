# Purchase and Order from CSV file

Columns related to purchase
- product_name
- quantity
- purchase_price
- purchase_currency : code like JPY, USD, SOM
- purchase_date in YYYY-MM-DD format optional, sets timezone.now() if not specified

Columns related to Order

Customer will be identified based on below in the order of importance
- customer_id (optional, will be prioritized if used)
- customer_username (optional, will be prioritized if used)
- customer_email (optional, same next in priority)
- customer_name (concatenation of last_name and first_name)

- selling_quantity
- selling_price
- selling_currency : code like JPY,USD,SOM
- payment_method (optional, default value cash_on_delivery)

- base_currency (optional, will be set to ACCOUNTING_CURRENCY is not specified)