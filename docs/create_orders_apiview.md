# Create orders APIView

Here is the handwritten note transcribed into text:

⸻

APIView to create an Order and OrderItems

Incoming data will be a list of order items.
Each item will be represented by two keys:
	•	"product_id"
	•	"quantity"
	•	Pull the active prices for each product using ProductPrice model
	•	Calculate sum for each item
	•	Set Order status to pending
	•	Set the customer from the logged in user
	•	Create payment associated with the Order
	•	Set and save total amount of the Order
	•	Decrease inventory for each product
	•	Make necessary journal entries using function journal_entries_for_inventory_changes
	•	Make journal entries associated with the orders
	•	When we sell a product our income/cash increases

⸻

Let me know if you want this converted into a Django DRF view or any other format.