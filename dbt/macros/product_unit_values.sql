{#- Aggregate clean lines to one unit value (sales / quantity) per item and period.
    An item is product x price channel, so a shift between channels is not read as a price change. -#}
{% macro product_unit_values(grain) %}
select
    date_trunc('{{ grain }}', l.sale_date)::date as period,
    l.stock_code,
    l.price_channel,
    l.stock_code || '|' || l.price_channel      as item_id,
    p.category,
    sum(l.quantity)                              as quantity,
    sum(l.line_amount)                           as sales,
    sum(l.line_amount) / sum(l.quantity)         as unit_value
from {{ ref('int_sales_lines_clean') }} l
join {{ ref('int_products') }} p using (stock_code)
group by all
{% endmacro %}
