# Purchases with orders simultaneously
The ability to enter purchases together with orders in a single row the administrator 
can buy a product and simultaneously sell the product to a customer. 
The administrator can specify the customer in the row by one of three columns 
- Customer first name 
- Customer last name 
- Customer username 
- Customer email 
email or username will be prioritized when identifying the customer from the database


# Profit rate
We will introduce a table called profit rate where 
the administrator will record the current profit rate. 
The table will hold the profit rate, which will be a floating point number with start date and end date. 
There will be only one record with end date null. 
Record with end date null will be the active record.
We can introduce a constraint, a unique constraint by Django

When creating a new product, we will introduce a purchase price field 
and then the application will calculate the price of the product using weight cost, and profit rate

# Products from CSV
When creating products from CSV file, we will introduce a purchase price column 
and also price column. 
If the price is left blank, The application will calculate the price of the product 
using weight cost per kilogram and profit rate.
if the administrator does not specify the weight of the product in the CSV file 
then the application will use the default weight of the product which will be set to 0.1 kg.

# Price calculator
We shall create a React component that will help administrator
to quickly find out the price of a product given its purchase price and weight.
The application will fetch the weight cost, the FX rate and the profit rate from the API 
and show it as the values of the form fields.
The administrator will have the ability to override these values

# Income and Spending

## Spending
make model, serializer viewset for SpendingName and Spending models. 
SpendingName will define a spending with name, 
description fields and extends AuditMixin, 
Spending will have foreign key to SpendingName 
with related name spendings, adate that will specify the DateField spending was spent, 
amount float field, currency field to specify in what currency the amount was. 
Spending should also extend AuditMixin
