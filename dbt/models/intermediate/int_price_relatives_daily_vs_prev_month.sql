-- Each item's price on day t against its average price over the previous calendar month.
-- Comparing to a monthly base (instead of to yesterday) keeps daily noise from compounding.
select
    d.period                               as period,
    m.period                               as base_month,
    d.item_id,
    d.stock_code,
    d.price_channel,
    d.category,
    d.unit_value                           as price_t,
    m.unit_value                           as price_prev,
    d.sales                                as sales_t,
    m.sales                                as sales_prev,
    ln(d.unit_value / m.unit_value)        as log_ratio,
    abs(ln(d.unit_value / m.unit_value)) > {{ var('max_abs_log_price_ratio') }} as is_outlier
from {{ ref('int_product_daily') }} d
join (
    -- all complete months, including the 2009-12 base month
    select * from ({{ product_unit_values('month') }})
) m
  on m.item_id = d.item_id
 and m.period = date_trunc('month', d.period) - interval 1 month
