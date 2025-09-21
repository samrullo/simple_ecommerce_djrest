# Product common cost and profits
The business has to pay per weight of the product when sending it from one country to another.
This application assumes for instance that the business buys products in Japan and sends them to Uz.

Set up a model ```WeightCost``` that will have fields
- cost_per_kg : cost per kg
- currency : cost denominated in currency
- start_date
- end_date
- audit mixins

The business may want to introduce a common profit rate when setting product price.
Set up a model ```ProfitRate``` that has following fields
- profit_rate : float, specifies profit rate. for instance if it is 0.3 it means product price will add 30% profit on top of product cost
- start_date
- end_date
- audit mixins