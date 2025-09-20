# Updating FX Rates
Admin will update FX Rate against primary currency, which is by default USD.
For instance, Admin will specify new rate for USD/JPY
The endpoint will close existing USD/JPY record, create new record with new rate with end_date null
And then it will calculate fx rates against JPY based on new rate and do the same, close with end_date as today and open new record against JPY.
