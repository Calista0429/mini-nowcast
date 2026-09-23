{#-
  Pair each product's unit value with its value in the previous period in which *anything*
  was sold (the previous trading day for daily data; there are no Saturday trades).
  Only items sold in both periods are "matched" and enter the index.
-#}
{% macro price_relatives(unit_values_ref) %}
with periods as (
    select period, lag(period) over (order by period) as prev_period
    from (select distinct period from {{ ref(unit_values_ref) }})
),
cur as (
    select u.*, p.prev_period
    from {{ ref(unit_values_ref) }} u
    join periods p using (period)
    where p.prev_period is not null
)
select
    cur.period,
    cur.prev_period,
    cur.item_id,
    cur.stock_code,
    cur.price_channel,
    cur.category,
    cur.unit_value                      as price_t,
    prev.unit_value                     as price_prev,
    cur.sales                           as sales_t,
    prev.sales                          as sales_prev,
    ln(cur.unit_value / prev.unit_value) as log_ratio,
    abs(ln(cur.unit_value / prev.unit_value)) > {{ var('max_abs_log_price_ratio') }} as is_outlier
from cur
join {{ ref(unit_values_ref) }} prev
  on prev.item_id = cur.item_id
 and prev.period = cur.prev_period
{% endmacro %}
