-- Daily sales by category and country: the main table for ad-hoc questions.
select
    l.sale_date,
    p.category,
    l.country,
    sum(l.line_amount)             as revenue_gbp,
    sum(l.quantity)                as units_sold,
    count(distinct l.invoice_no)   as invoices,
    count(distinct l.customer_id)  as customers,
    count(distinct l.stock_code)   as products_sold
from {{ ref('int_sales_lines_clean') }} l
join {{ ref('int_products') }} p using (stock_code)
group by all
