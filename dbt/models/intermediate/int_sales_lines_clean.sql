select
    invoice_no, stock_code, description, quantity, unit_price, line_amount,
    invoiced_at, sale_date, customer_id, country,
    -- Lines without a customer ID are priced ~2x registered (wholesale) customers for the same
    -- product, so they are treated as a separate price channel in the index.
    case when customer_id is null then 'unregistered' else 'registered' end as price_channel
from {{ ref('int_sales_lines_flagged') }}
where exclusion_reason is null
