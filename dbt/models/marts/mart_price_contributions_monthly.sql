-- How much each item (product x price channel) pushed the monthly index up or down (in index log-points).
-- Contributions within a month sum to that month's log_change.
with rel as (
    select * from {{ ref('int_price_relatives_monthly') }} where not is_outlier
),
weighted as (
    select
        *,
        0.5 * (sales_t / sum(sales_t) over (partition by period)
             + sales_prev / sum(sales_prev) over (partition by period)) as weight
    from rel
)
select
    w.period                     as month,
    w.stock_code,
    w.price_channel,
    p.description,
    w.category,
    w.price_prev,
    w.price_t,
    w.price_t / w.price_prev - 1 as price_change_pct,
    w.weight,
    w.weight * w.log_ratio       as contribution
from weighted w
join {{ ref('int_products') }} p using (stock_code)
