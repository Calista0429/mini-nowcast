-- Rename, type-cast and normalise. No business filtering happens here.
-- The two workbook sheets both contain 2010-12-01..2010-12-09, so that window is
-- taken from the later sheet only.
select
    invoice                                         as invoice_no,
    upper(trim(stockcode))                          as stock_code,
    nullif(trim(description), 'nan')                as description,
    quantity::bigint                                as quantity,
    price::double                                   as unit_price,
    quantity * price                                as line_amount,
    invoicedate                                     as invoiced_at,
    cast(invoicedate as date)                       as sale_date,
    cast("Customer ID" as bigint)                   as customer_id,
    country                                         as country,
    starts_with(invoice, 'C')                       as is_cancellation,
    source_sheet
from {{ source('raw', 'online_retail') }}
where not (source_sheet = 'Year 2009-2010' and invoicedate >= timestamp '2010-12-01')
